import glob
from typing import Any, Union
import json

TARGET_DIR = "../thirdparty/「波音リツ」歌声データベースVer2/DATABASE"

PHONEME_LIST = [
    "-",
    "br",
    "’あ",
    "’あっ",
    "’い",
    "’う",
    "’え",
    "’お",
    "あ",
    "あっ",
    "あー",
    "い",
    "いぇ",
    "いっ",
    "いー",
    "う",
    "うぃ",
    "うぇ",
    "うぉ",
    "うぉっ",
    "うっ",
    "うー",
    "え",
    "えっ",
    "えー",
    "お",
    "おっ",
    "おー",
    "か",
    "かっ",
    "が",
    "がっ",
    "き",
    "きぇ",
    "きっ",
    "きゃ",
    "きゅ",
    "きょ",
    "ぎ",
    "ぎぇ",
    "ぎぇー",
    "ぎっ",
    "ぎゃ",
    "ぎゅ",
    "ぎょ",
    "く",
    "くっ",
    "ぐ",
    "ぐっ",
    "け",
    "けっ",
    "げ",
    "げっ",
    "こ",
    "こっ",
    "ご",
    "さ",
    "さっ",
    "ざ",
    "し",
    "しぇ",
    "しっ",
    "しゃ",
    "しゅ",
    "しょ",
    "しょっ",
    "じ",
    "じぇ",
    "じぇー",
    "じっ",
    "じゃ",
    "じゃっ",
    "じゅ",
    "じょ",
    "す",
    "すぃ",
    "すっ",
    "ず",
    "ずぃ",
    "ずっ",
    "せ",
    "せっ",
    "ぜ",
    "ぜっ",
    "そ",
    "そっ",
    "ぞ",
    "ぞっ",
    "た",
    "たっ",
    "だ",
    "だっ",
    "ち",
    "ちぇ",
    "ちぇっ",
    "ちっ",
    "ちゃ",
    "ちゃっ",
    "ちゅ",
    "ちょ",
    "ちょっ",
    "ぢ",
    "っ",
    "つ",
    "つぁ",
    "つぃ",
    "つぇ",
    "つぉ",
    "つっ",
    "づ",
    "て",
    "てぃ",
    "てぇ",
    "てっ",
    "てゃ",
    "てゅ",
    "てょ",
    "で",
    "でぃ",
    "でぃっ",
    "でぇ",
    "でゃ",
    "でゅ",
    "でょ",
    "と",
    "とぅ",
    "とぅっ",
    "とっ",
    "ど",
    "どぅ",
    "どっ",
    "な",
    "なっ",
    "に",
    "にぇ",
    "にゃ",
    "にゅ",
    "にょ",
    "ぬ",
    "ね",
    "の",
    "のっ",
    "は",
    "はっ",
    "ば",
    "ばっ",
    "ぱ",
    "ぱっ",
    "ひ",
    "ひぇ",
    "ひっ",
    "ひゃ",
    "ひゃっ",
    "ひゅ",
    "ひょ",
    "び",
    "びぇ",
    "びぇー",
    "びゃ",
    "びゅ",
    "びょ",
    "ぴ",
    "ぴぇ",
    "ぴぇー",
    "ぴゃ",
    "ぴゅ",
    "ぴょ",
    "ふ",
    "ふぁ",
    "ふぃ",
    "ふぇ",
    "ふぉ",
    "ふゅ",
    "ぶ",
    "ぶっ",
    "ぷ",
    "へ",
    "べ",
    "べっ",
    "ぺ",
    "ほ",
    "ぼ",
    "ぼっ",
    "ぽ",
    "ま",
    "まっ",
    "み",
    "みぇ",
    "みっ",
    "みゃ",
    "みゅ",
    "みょ",
    "む",
    "むっ",
    "め",
    "めっ",
    "も",
    "もっ",
    "や",
    "やっ",
    "ゆ",
    "ゆっ",
    "よ",
    "よっ",
    "ら",
    "らっ",
    "り",
    "りぇ",
    "りっ",
    "りゃ",
    "りゅ",
    "りょ",
    "る",
    "るっ",
    "れ",
    "れっ",
    "ろ",
    "わ",
    "わっ",
    "ゐ",
    "ゑ",
    "を",
    "ん",
    "キ",
    "ク",
    "グ",
    "コ",
    "サ",
    "シ",
    "シュ",
    "ジ",
    "ス",
    "ズ",
    "タ",
    "チ",
    "ツ",
    "ト",
    "ドゥ",
    "ヒ",
    "フ",
    "ブ",
    "プ",
    "リ",
    "ル",
    "・",
    "・あ",
    "・あっ",
    "・い",
    "・いっ",
    "・う",
    "・え",
    "・お",
    "・ん",
]
MIN_PITCH = 30
MAX_PITCH = 100


class FileEncoder:
    def __init__(self):
        pass

    def encode(self):
        # generate parsed ust master
        self._genrate_parsed_ust_master()

        json_files = glob.glob("../master/ust/json/*.json")
        assert len(json_files) > 0, "json files not found"
        print(f"found {len(json_files)} json files")

        print("encoding lyrics to onehot and normalizing pitch...")
        for json_file in json_files:
            with open(json_file, "r") as f:
                parsed_ust = json.load(f)

            notes = parsed_ust["notes"]

            for note in notes:
                if "train_params" not in note:
                    note["train_params"] = dict()

                lyric = note["lyric"]
                onehot = self._lyric_to_onehot(lyric)

                note["train_params"]["lyric_onehot"] = onehot
                note_num = note["notenum"]
                normalized_pitch = self._normalize_midi_pitch(note_num)
                note["train_params"]["normalized_pitch"] = normalized_pitch

            with open(json_file, "w") as f:
                json.dump(parsed_ust, f, indent=4, ensure_ascii=False)
        print("done encoding lyrics and pitch")

    def _normalize_midi_pitch(
        self, midi_note, min_pitch=MIN_PITCH, max_pitch=MAX_PITCH
    ):
        return (midi_note - min_pitch) / (max_pitch - min_pitch)

    def _lyric_to_onehot(self, lyric: str):
        onehot = [0] * len(PHONEME_LIST)

        # mute is represented as "R"
        if lyric == "R":
            # return all zeros
            # TODO: check if this is correct
            return onehot

        for i, phoneme in enumerate(PHONEME_LIST):
            if phoneme == lyric:
                onehot[i] = 1

        assert sum(onehot) == 1, f"lyric {lyric} not found in phoneme list "

        return onehot

    def _genrate_parsed_ust_master(self):
        json_files = glob.glob("../master/ust/json/*")
        if len(json_files) > 0:
            print("json files already exist")
            return

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
