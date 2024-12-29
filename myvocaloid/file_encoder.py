import glob
from typing import Any, Union
import json
from constants import PHONEME_LIST
import numpy as np


TMP_PARSED_USTS = "./tmp/parsed_usts.json"



class FileEncoder:
    def __init__(self, target_dir: str, min_pitch: float, max_pitch: float, output_dir: str):
        self.target_dir = target_dir
        self.min_pitch = min_pitch
        self.max_pitch = max_pitch
        self.output_dir = output_dir

    def encode(self):
        # generate parsed ust master
        self._generate_parsed_usts()

        with open(TMP_PARSED_USTS, "r") as f:
            parsed_usts = json.load(f)
        

        _names = []
        duration_indexs = []
        notenum_indexs = []
        lyric_indexs = []

        max_duration = 0

        for ust_data in parsed_usts["usts"]:
            song_name = ust_data["name"]
            ust = ust_data["data"]

            data  = dict()

            data["_name"] = song_name # for debugging
            data["notes"] = []

            _names.append(song_name)

            lyric_indexs_elem = []
            duration_indexs_elem = []
            notenum_indexs_elem = []

            for note in ust["notes"]:
                lyric_indexs_elem.append(self._lyric_to_index(note["lyric"]))
                duration_indexs_elem.append(note["duration"])
                notenum_indexs_elem.append(note["notenum"])
                max_duration = max(max_duration, note["duration"])
            
            lyric_indexs.append(lyric_indexs_elem)
            duration_indexs.append(duration_indexs_elem)
            notenum_indexs.append(notenum_indexs_elem)
        

        # normalize duration
        for duration_indexs_elem in duration_indexs:
            for elem in duration_indexs_elem:
                elem = np.log1p(elem) / np.log1p(max_duration)
                assert 0 <= elem <= 1, f"Invalid duration: {elem}"
        
        assert len(_names) == len(lyric_indexs) == len(duration_indexs) == len(notenum_indexs), "Invalid data length"

        print(f"Data length: {len(_names[0])}")
        print(f"note length example: {len(lyric_indexs[0])}")

        return _names, lyric_indexs, duration_indexs, notenum_indexs



    def _normalize_midi_pitch(self, midi_note):
        return (midi_note - self.min_pitch) / (self.max_pitch - self.min_pitch)

    def _lyric_to_index(self, lyric: str):
        return PHONEME_LIST.index(lyric)

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
