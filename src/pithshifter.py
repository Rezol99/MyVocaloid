import glob
import pyrubberband as pyrb
import librosa
import soundfile as sf

VOICE_FILES = "../thirdparty/ENUNU_波音リツVer2_1202/ENUNU_波音リツVer2_1202/単独音/*wav"

if __name__ == '__main__':
    voice_files = glob.glob(VOICE_FILES)

    first_voice_file = voice_files[0]
    y, sr = librosa.load(first_voice_file, sr=None)

    print("pitch shifting...")
    # ピッチを変更（例: 2半音上げる）
    y_pitch_shifted = pyrb.pitch_shift(y, sr, n_steps=2)
    print("pitch shift done")

    print("save file...")
    sf.write("../gen/pitch_shfted.wav", y_pitch_shifted, sr)
    print("save done")
