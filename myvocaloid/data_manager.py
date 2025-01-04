from typing import Optional
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model

MODEL_FILE = "../data/model.keras"

LYRIC_INDEX_FILE = "../data/npy/lyric_indexs.npy"
DURATION_INDEX_FILE = "../data/npy/duration_indexs.npy"
NOTENUM_INDEX_FILE = "../data/npy/notenum_indexs.npy"
NAMES_FILE = "../data/json/names.json"
Y_FILE = "../data/npy/y.npy"

class DataLoader:
    @staticmethod
    def load():
        lyric_indexs = np.load(LYRIC_INDEX_FILE)
        duration_indexs = np.load(DURATION_INDEX_FILE)
        notenum_indexs = np.load(NOTENUM_INDEX_FILE)
        y = np.load(Y_FILE)
        model = load_model(MODEL_FILE)

        return lyric_indexs, duration_indexs, notenum_indexs, y, model

class DataManager:
    def __init__(
        self, 
        lyric_indexs,
        duration_indexs,
        notenum_indexs,
        y,
        model
    ):
        self.lyric_indexs = lyric_indexs
        self.duration_indexs = duration_indexs
        self.notenum_indexs = notenum_indexs
        self.y = y
        model.save(MODEL_FILE)


    def save(self):
        np.save(LYRIC_INDEX_FILE, self.lyric_indexs)
        np.save(DURATION_INDEX_FILE, self.duration_indexs)
        np.save(NOTENUM_INDEX_FILE, self.notenum_indexs)
        np.save(Y_FILE, self.y)

    def update(self, lyric_indexs, duration_indexs, notenum_indexs, names, y):
        self.lyric_indexs = lyric_indexs
        self.duration_indexs = duration_indexs
        self.notenum_indexs = notenum_indexs
        self.names = names
        self.y = y

        self.save()
    