import pyrubberband as pyrb
import librosa
import soundfile as sf
import numpy as np

def pitch_shift(
    voice_files: str,
    step: int
) -> np.ndarray:
    y, sr = librosa.load(voice_files, sr=None)

    print("pitch shifting...")
    y_pitch_shifted = pyrb.pitch_shift(y, sr, n_steps=step)
    print("pitch shift done")

    return y_pitch_shifted
