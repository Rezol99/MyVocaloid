from typing import Optional
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model

MODEL_FILE = "data/model.keras"

LYRIC_INDEX_FILE = "data/npy/lyric_indexs.npy"
DURATION_INDEX_FILE = "data/npy/duration_indexs.npy"
NOTENUM_INDEX_FILE = "data/npy/notenum_indexs.npy"
Y_FILE = "data/npy/y.npy"

class DataManager:
    def __init__(self):
        self.lyric_indexs: Optional[np.ndarray] = None
        self.duration_indexs: Optional[np.ndarray] = None
        self.notenum_indexs: Optional[np.ndarray] = None
        self.y: Optional[np.ndarray] = None
    
    def save_model(self, model):
        model.save(MODEL_FILE)
    
    def load_model(self):
        return load_model(MODEL_FILE)

    def save(
        self,
        lyric_indexs: np.ndarray,
        duration_indexs: np.ndarray,
        notenum_indexs: np.ndarray,
        y: np.ndarray
    ):
        np.save(LYRIC_INDEX_FILE, lyric_indexs)
        np.save(DURATION_INDEX_FILE, duration_indexs)
        np.save(NOTENUM_INDEX_FILE, notenum_indexs)
        np.save(Y_FILE, y)

        self._update(lyric_indexs, duration_indexs, notenum_indexs, y)
    
    def load(self):
        lyric_indexs = np.load(LYRIC_INDEX_FILE)
        duration_indexs = np.load(DURATION_INDEX_FILE)
        notenum_indexs = np.load(NOTENUM_INDEX_FILE)
        y = np.load(Y_FILE)

        self._update(lyric_indexs, duration_indexs, notenum_indexs, y)

        return lyric_indexs, duration_indexs, notenum_indexs, y

    def _update(self, lyric_indexs, duration_indexs, notenum_indexs, y):
        self.lyric_indexs = lyric_indexs
        self.duration_indexs = duration_indexs
        self.notenum_indexs = notenum_indexs
        self.y = y
    
    def get_train_and_test_data(self):
        is_ready = self.lyric_indexs is not None and self.duration_indexs is not None and self.notenum_indexs is not None and self.y is not None
        if not is_ready:
            self.load()

        x = np.stack([self.lyric_indexs, self.duration_indexs, self.notenum_indexs], axis=-1) # type: ignore

        x_train, x_test, y_train, y_test = train_test_split(x, self.y, test_size=0.2, random_state=42)

        train_lyric, train_duration, train_notenum = x_train[..., 0], x_train[..., 1], x_train[..., 2]
        test_lyric, test_duration, test_notenum = x_test[..., 0], x_test[..., 1], x_test[..., 2]

        return (train_lyric, train_duration, train_notenum), (test_lyric, test_duration, test_notenum), y_train, y_test