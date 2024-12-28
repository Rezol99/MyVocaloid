import glob
from typing import Any, Union
import json

TARGET_DIR = "../thirdparty/「波音リツ」歌声データベースVer2/DATABASE"

class FileEncoder:
    def __init__(self):
        pass

    def encode(self):
        paths = self._get_all_song_paths()
        for path in paths:
            usts = glob.glob(f"{path}/*.ust")
            assert len(usts) == 1, f"ust file not found in {path}"
            ust = usts[0]
            parsed_ust = self._parse_ust(ust)
            name = path.split("/")[-1]

            json_path = f"../master/ust/json/{name}.json"
            with open(json_path, "w") as f:
                json.dump(parsed_ust, f, indent=4, ensure_ascii=False)

    def _get_all_song_paths(self):
        return glob.glob(f"{TARGET_DIR}/*")

    def _get_song_files(self, song_name):
        return glob.glob(f"{TARGET_DIR}/{song_name}/*")
    
    def _parse_key_value(self, line):
        print(f"parsing line: {line}")

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


if __name__ == "__main__":
    encoder = FileEncoder()
    encoder.encode()
    