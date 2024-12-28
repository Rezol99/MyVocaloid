import glob
from typing import Union
import json

TAREF_DIR = "../thirdparty/「波音リツ」歌声データベースVer2/DATABASE"

class FileEncoder:
    def __init__(self):
        pass

    def encode(self):
        pass

    def _get_all_songs(self):
        return glob.glob(f"{TAREF_DIR}/*")

    def _get_song_files(self, song_name):
        return glob.glob(f"{TAREF_DIR}/{song_name}/*")
    
    def _parse_key_value(self, line):
        print(f"parsing line: {line}")

        key, value = line.split("=")
        # strip whitespaces
        key = key.strip()
        value = value.strip()

        # empty value
        if value == "":
            return key, None

        # key lower case
        key = key.lower()

        return key, value
    
    def _endode_ust(self, song_name):
        files = self._get_song_files(song_name)
        ust_files = [f for f in files if f.endswith(".ust")]

        assert len(ust_files) == 1, f"ust file not found in {song_name}"
        ust_file = ust_files[0]

        with open(ust_file, "r", encoding="shift_jis") as f:
            # shift-jis encoding
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
                ret["notes"].append(tmp_note)
                tmp_note = dict()
                continue
            
            if is_setting:
                key, value = self._parse_key_value(line)
                ret["setting"][key] = value
            
            if is_notes:
                key, value = self._parse_key_value(line)
                if tmp_note is not None and value is not None:
                    tmp_note[key] = value
        
        print("done parsing ust file")
        return ret


if __name__ == "__main__":
    encoder = FileEncoder()
    res = encoder._endode_ust("WAVE")

    # utf-8 encoding dump
    print(json.dumps(res, indent=4, ensure_ascii=False))
    
