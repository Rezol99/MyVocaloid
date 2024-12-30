import glob
from typing import Any, Union
import json
from pydub import AudioSegment
import librosa
import numpy as np
import os
from audio_utils import audio_to_mel, load_audio

TMP_PARSED_USTS = "./tmp/parsed_usts.json"

class FileEncoder:
    max_pitch = 30
    min_pitch = 100

    def __init__(
        self, target_dir: str, output_dir: str
    ):
        self.target_dir = target_dir
        self.output_dir = output_dir
        self.phoneme_list = [] 
    

    def _encode_x(self):
        # generate parsed ust master
        self._generate_parsed_usts()

        with open(TMP_PARSED_USTS, "r") as f:
            parsed_usts = json.load(f)

        _names = []
        durations = []
        notenums = []
        lyric_indexs = []
        ms_times = dict()

        max_duration = 0

        for ust_data in parsed_usts["usts"]:
            song_name = ust_data["name"]
            ust = ust_data["data"]

            lyric_indexs_elem = []
            duration_elem = []
            notenum_elem = []
            ms_times_elem = []

            note_count = 0
            current_time = 0

            for note in ust["notes"]:
                lyric_indexs_elem.append(self._lyric_to_index(note["lyric"]))
                duration_elem.append(note["duration"])

                normalized_notenum = (note["notenum"] - self.min_pitch) / (self.max_pitch - self.min_pitch)
                notenum_elem.append(normalized_notenum)
                duration = note["duration"]
                max_duration = max(max_duration, duration)

                note_count += 1
                current_time += duration * 1000

                # group notes by 4
                if note_count % 4 == 0:
                    _names.append(song_name)
                    lyric_indexs.append(lyric_indexs_elem)
                    durations.append(duration_elem)
                    notenums.append(notenum_elem)
                    ms_times[song_name] = ms_times.get(song_name, []) + [current_time]

        # normalize duration
        for duration_elem in durations:
            for elem in duration_elem:
                elem = np.log1p(elem) / np.log1p(max_duration)
                assert 0 <= elem <= 1, f"Invalid duration: {elem}"

        print(f"name length: {len(_names)}")
        print(f"lyric_indexs length: {len(lyric_indexs)}")
        print(f"durations length: {len(durations)}")
        print(f"notenums length: {len(notenums)}") 
        assert (
            len(_names)
            == len(lyric_indexs)
            == len(durations)
            == len(notenums)
        ), "Invalid data length"

        print(f"Data length: {len(_names[0])}")
        print(f"note length example: {len(lyric_indexs[0])}")

        # padding
        max_len = max([len(elem) for elem in lyric_indexs])
        lyric_indexs = np.array(
            [
                np.pad(item, (0, max_len - len(item)), constant_values=0)
                for item in lyric_indexs
            ]
        )
        max_len = max([len(elem) for elem in durations])
        durations = np.array(
            [
                np.pad(item, (0, max_len - len(item)), constant_values=0)
                for item in durations
            ]
        )

        max_len = max([len(elem) for elem in notenums])
        notenums = np.array(
            [
                np.pad(item, (0, max_len - len(item)), constant_values=0)
                for item in notenums
            ]
        )

        return _names, lyric_indexs, durations, notenums, ms_times
    
    def _pad_spectrogram(self, spectrogram, target_length):
        if spectrogram.shape[1] < target_length:
            pad_width = target_length - spectrogram.shape[1]
            return np.pad(spectrogram, ((0, 0), (0, pad_width)), mode='constant')
        else:
            return spectrogram[:, :target_length]
    
    def _encode_y(self, ms_time_map: dict):
        max_length = 0 
        ret = []

        with open(TMP_PARSED_USTS, "r") as f:
            parsed_usts = json.load(f)
        
        song_paths = [ust_data["path"] for ust_data in parsed_usts["usts"]]

        for song_path in song_paths:
            song_name = song_path.split("/")[-1]

            ms_times = ms_time_map[song_name]


            audio = AudioSegment.from_wav(song_path + f"/{song_name}.wav")

            for i in range(len(ms_times) - 1):
                start_time = ms_times[i]
                end_time = ms_times[i + 1]
                audio = audio[start_time:end_time]

                audio_array = np.array(audio.get_array_of_samples())


                # 整数型を浮動小数点型に変換（16-bit PCMの場合）
                if audio.sample_width == 2:  # 16-bitの場合
                    audio_array = audio_array.astype(np.float32) / 32768.0
                elif audio.sample_width == 3:  # 24-bitの場合
                    audio_array = audio_array.astype(np.float32) / 8388608.0
                elif audio.sample_width == 4:  # 32-bitの場合
                    audio_array = audio_array.astype(np.float32) / 2147483648.0

                # ステレオの場合、片方のチャンネルを選択（librosaはモノラルを想定）
                if audio.channels == 2:
                    audio_array = audio_array[:, 0]  # 左チャンネルを選択


                # mel spectrogram
                mel_spectrogram = audio_to_mel(audio_array)

                max_length = max(max_length, mel_spectrogram.shape[1])

                ret.append(mel_spectrogram)

        # padding 
        ret = [self._pad_spectrogram(spec, max_length) for spec in ret]

        # normalize
        ret = np.array(ret)
        ret = (ret - np.min(ret)) / (np.max(ret) - np.min(ret))

        return ret

    def _clean(self):
        # remove tmp file
        os.remove(TMP_PARSED_USTS)
        pass

    def encode(self):
        _names, lyric_indexs, duration_indexs, notenum_indexs, ms_times = self._encode_x()
        y = self._encode_y(ms_times)
        self._clean()
        return _names, lyric_indexs, duration_indexs, notenum_indexs, y

    def _lyric_to_index(self, lyric: str):
        is_new = lyric not in self.phoneme_list
        if is_new:
            self.phoneme_list.append(lyric)
        return self.phoneme_list.index(lyric)

    def _generate_parsed_usts(self):
        paths = self._get_all_song_paths()

        usts_data = dict()
        usts_data["usts"] = list()

        for path in paths:
            usts = glob.glob(f"{path}/*.ust")
            assert len(usts) == 1, f"ust file not found in {path}"
            ust = usts[0]
            parsed_ust = self._parse_ust(ust)
            name = path.split("/")[-1]

            data = dict()
            data["name"] = name
            data["data"] = parsed_ust
            data["path"] = path

            usts_data["usts"].append(data)

        with open(TMP_PARSED_USTS, "w") as f:
            json.dump(usts_data, f, indent=4, ensure_ascii=False)

    def _get_all_song_paths(self):
        return glob.glob(f"{self.target_dir}/*")

    def _get_song_files(self, song_name):
        return glob.glob(f"{self.target_dir}/{song_name}/*")

    def _parse_key_value(self, line):
        key, value = line.split("=")
        # strip whitespaces
        key = key.strip()
        value: Any = value.strip()

        # empty value
        if value == "":
            return key, None

        # value is number
        if value.isdigit():
            value = int(value)

        if type(value) != int:
            try:
                # value is float
                value = float(value)
            except ValueError:
                pass

        # key lower case
        key = key.lower()

        return key, value

    def _add_duration_to_note(self, note, tempo: int):
        if "length" in note:
            note["duration"] = note["length"] / 480 * (60 / tempo)

    def _parse_ust(self, ust_file):

        # shift-jis encoding
        with open(ust_file, "r", encoding="shift_jis") as f:
            ust_content = f.read()

        print("parsing ust file...")

        ret = dict()
        ret["setting"] = dict()
        ret["notes"] = list()

        is_notes = False
        tmp_note: Union[None, dict] = None
        is_setting = False

        for line in ust_content.split("\n"):
            is_content = line.startswith("[#") and line.endswith("]")

            if is_content:
                if line.startswith("[#VERSION]"):
                    continue
                if line.startswith("[#SETTING]"):
                    is_setting = True
                    continue
                if line.startswith("[#TRACKEND]"):
                    break
                else:
                    is_setting = False

                content_text = line[2:-1]

                is_note = all([c.isdigit() for c in content_text])
                assert is_note, f"Invalid note content: {content_text}"

                is_notes = True
                if tmp_note is not None:
                    ret["notes"].append(tmp_note)
                tmp_note = dict()
                continue

            if is_setting:
                key, value = self._parse_key_value(line)
                ret["setting"][key] = value

            if is_notes:
                key, value = self._parse_key_value(line)
                if tmp_note is not None and value is not None:
                    self._add_duration_to_note(tmp_note, ret["setting"]["tempo"])
                    tmp_note[key] = value

        print("done parsing ust file")
        return ret
