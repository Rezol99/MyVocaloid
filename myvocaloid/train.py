from file_encoder import FileEncoder
import numpy as np
import sys
import tensorflow as tf

TARGET_DIR = "./thirdparty/「波音リツ」歌声データベースVer2/DATABASE"
OUTPUT_DIR = "./master/ust/json"

LYRIC_INDEX_FILE = "data/npy/lyric_indexs.npy"
DURATION_INDEX_FILE = "data/npy/duration_indexs.npy"
NOTENUM_INDEX_FILE = "data/npy/notenum_indexs.npy"
Y_FILE = "data/npy/y.npy"

if __name__ == "__main__":
    need_encode = False

    if len(sys.argv) > 1:
        if sys.argv[1] == "--encode":
            need_encode = True

    if need_encode:
        encoder = FileEncoder(TARGET_DIR, OUTPUT_DIR)
        _names, lyric_indexs, duration_indexs, notenum_indexs, y = encoder.encode()

        np.save(LYRIC_INDEX_FILE, lyric_indexs)
        np.save(DURATION_INDEX_FILE, duration_indexs)
        np.save(NOTENUM_INDEX_FILE, notenum_indexs)
        np.save(Y_FILE, y)

    lyric_indexs = np.load(LYRIC_INDEX_FILE)
    duration_indexs = np.load(DURATION_INDEX_FILE)
    notenum_indexs = np.load(NOTENUM_INDEX_FILE)
    y = np.load(Y_FILE)

    print(f"lyric_indexs: {lyric_indexs.shape}")
    print(f"duration_indexs: {duration_indexs.shape}")
    print(f"notenum_indexs: {notenum_indexs.shape}")
    print(f"y: {y.shape}")
