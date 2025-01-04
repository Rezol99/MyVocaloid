import glob
from typing import Any, Union
import json
import librosa
import numpy as np
import os
from audio_utils import audio_to_mel, load_audio, split_audio

Y_ENCODE_PARAMS = "../data/json/encode_params.json"
TMP_PARSED_USTS = "../tmp/parsed_usts.json"

class FileEncoder:
    def __init__(
        self, target_dir: str, output_dir: str, max_pitch: int, min_pitch: int, note_chunk: int, duration_features: int, pitch_features: int
    ):
        self.target_dir = target_dir
        self.output_dir = output_dir
        self.max_pitch = max_pitch
        self.min_pitch = min_pitch
        self.note_chunk = note_chunk
        self.duration_features = duration_features
        self.pitch_features = pitch_features

        self._phoneme_list = [] 


    def _encode_x(self):
        # generate parsed ust master
        self._generate_parsed_usts()

        with open(TMP_PARSED_USTS, "r") as f:
            parsed_usts = json.load(f)

        durations = []
        notenums = []
        lyric_indexs = []

        max_duration = 0
        split_times_map = dict() # 曲名からノートの区切り時間を取得するための辞書
        usts = parsed_usts["usts"]

        for ust_data in usts:
            ust = ust_data["data"]
            name = ust_data["name"]

            notes = ust["notes"]
            split_times_map[name] = []

            for note in notes:
                duration = note["duration"]
                durations.append(duration)

                max_duration = max(max_duration, duration)
                split_times_map[name].append(duration)

                notenum = note["notenum"]
                notenum = (notenum - self.min_pitch) / (self.max_pitch - self.min_pitch)
                notenums.append(notenum)

                lyric = note["lyric"]
                lyric_index = self._lyric_to_index(lyric)
                lyric_indexs.append(lyric_index)

        # normalize duration
        for i, duration in enumerate(durations):
            durations[i] = duration / max_duration
            assert 0 <= durations[i] <= 1, f"Invalid duration: {duration}"
        
        print("lyric_indexs: ", max(lyric_indexs))

        assert (
            len(lyric_indexs)
            == len(durations)
            == len(notenums)
        ), "Invalid data length"

        print("lyric_indexs length: ", len(lyric_indexs))

        lyric_indexs = np.array(lyric_indexs).reshape(-1, self.note_chunk)
        durations = np.array(durations).reshape(-1, self.note_chunk, self.duration_features)
        notenums = np.array(notenums).reshape(-1, self.note_chunk, self.pitch_features)

        return lyric_indexs, durations, notenums, split_times_map

    
    def _pad_spectrogram(self, spectrogram, target_length):
        if spectrogram.shape[1] < target_length:
            pad_width = target_length - spectrogram.shape[1]
            return np.pad(spectrogram, ((0, 0), (0, pad_width)), mode='constant')
        else:
            return spectrogram[:, :target_length]
    
    def _encode_y(self, split_times_map):
        print("encoding y...")
        max_length = 0 

        with open(TMP_PARSED_USTS, "r") as f:
            parsed_usts = json.load(f)
        
        song_paths = [ust_data["path"] for ust_data in parsed_usts["usts"]]

        audio_parts = []

        for song_path in song_paths:
            song_name = song_path.split("/")[-1]
            split_times = split_times_map[song_name]
            wav_files = glob.glob(f"{song_path}/*.wav")
            assert len(wav_files) == 1, f"wav file not found in {song_path}"
            wav_file = wav_files[0]
            y = load_audio(wav_file)

            tmp = y

            for ms in split_times:
                part, others = split_audio(tmp, ms)
                tmp = others
                audio_parts.append(part)

        ret = [] 
        max_length = 0
        for audio_part in audio_parts:
            mel_spectrogram = audio_to_mel(audio_part)
            ret.append(mel_spectrogram)
            max_length = max(max_length, mel_spectrogram.shape[1])
        
        ret = [self._pad_spectrogram(spec, max_length) for spec in ret]

        is_same_length = all([spec.shape[1] == max_length for spec in ret])
        assert is_same_length, "Invalid spectrogram length"

        max_value = np.max(ret).astype(float)
        min_value = np.min(ret).astype(float)

        with open(Y_ENCODE_PARAMS, "w") as f:
            json.dump({"max": max_value, "min": min_value}, f, indent=4, ensure_ascii=False)
        
        ret = np.array(ret)
        ret = (ret - min_value) / (max_value - min_value)

        print("done encoding y")

        return ret


    def _clean(self):
        # remove tmp file
        # os.remove(TMP_PARSED_USTS)
        pass

    def encode(self):
        lyric_indexs, durations, notenums, split_times_map = self._encode_x()
        y = self._encode_y(split_times_map)

        self._clean()

        return lyric_indexs, durations, notenums, y

    def _lyric_to_index(self, lyric: str):
        is_new = lyric not in self._phoneme_list
        if is_new:
            self._phoneme_list.append(lyric)
        return self._phoneme_list.index(lyric)

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

        print("parsing ust file...", ust_file)

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

        print("done parsing ust file", ust_file)
        return ret
