import numpy as np

def combine_audio(
    audio1: np.ndarray,
    audio2: np.ndarray
) -> np.ndarray:
    return np.concatenate((audio1, audio2), axis=None)