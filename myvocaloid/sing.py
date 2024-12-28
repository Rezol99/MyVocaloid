import soundfile as sf
from pithshifter import pitch_shift
from combine_audio import combine_audio

VOICE_DIR = "../thirdparty/ENUNU_波音リツVer2_1202/ENUNU_波音リツVer2_1202/単独音"


def find_voice_files(text: str) -> list:
    files = []
    for s in text:
        files.append(f"{VOICE_DIR}/{s}.wav")
    return files


def generate_sing_voice(files: list, shift_steps: list) -> list:
    assert len(files) == len(shift_steps)
    ret = None

    for i, f in enumerate(files):
        y = pitch_shift(f, shift_steps[i])
        if ret is not None:
            y = combine_audio(ret, y)
        ret = y

    return ret  # type: ignore


def main():
    text = input("Enter text: ")
    shift_steps = [i * 2 for i, _ in enumerate(text)]
    voice_files = find_voice_files(text)
    print("found voice files:", voice_files)
    print("concatenating...")
    generated = generate_sing_voice(voice_files, shift_steps)
    print("concatenated")

    sf.write("../gen/sing.wav", generated, 44100)


if __name__ == "__main__":
    main()
