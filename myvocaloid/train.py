from file_encoder import FileEncoder
from data_manager import DataManager
import numpy as np
import sys
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split

TARGET_DIR = "./thirdparty/「波音リツ」歌声データベースVer2/DATABASE"
OUTPUT_DIR = "./master/ust/json"


def build_model(input_shape, output_shape):
    model = models.Sequential()

    model.add(layers.Input(shape=input_shape))
    model.add(layers.LSTM(256, return_sequences=True))
    model.add(layers.Dropout(0.3))
    model.add(layers.LSTM(128, return_sequences=False))

    model.add(layers.Dense(512, activation='relu'))
    model.add(layers.Dropout(0.3))

    output_size = output_shape[0] * output_shape[1]
    model.add(layers.Dense(output_size, activation='linear'))

    model.add(layers.Reshape(output_shape))

    model.compile(optimizer='adam', loss='mse')
    return model

if __name__ == "__main__":
    need_encode = False

    if len(sys.argv) > 1:
        if sys.argv[1] == "--encode":
            need_encode = True
    
    manager = DataManager()

    if need_encode:
        encoder = FileEncoder(TARGET_DIR, OUTPUT_DIR)
        _, lyric_indexs, duration_indexs, notenum_indexs, y = encoder.encode()
        manager.save(lyric_indexs, duration_indexs, notenum_indexs, y)
    
    lyric_indexs, duration_indexs, notenum_indexs, y = manager.load()

    assert len(y) > 0 and len(lyric_indexs) > 0 and len(duration_indexs) > 0 and len(notenum_indexs) > 0

    print(f"lyric_indexs: {lyric_indexs.shape}")
    print(f"duration_indexs: {duration_indexs.shape}")
    print(f"notenum_indexs: {notenum_indexs.shape}")
    print(f"y: {y.shape}")

    x = np.stack([lyric_indexs, duration_indexs, notenum_indexs], axis=-1)

    x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.2, random_state=42)
    print(f"x_train: {x_train.shape}")
    print(f"y_train: {y_train.shape}")

    model = build_model(input_shape=x_train.shape[1:], output_shape=y_train.shape[1:])
    model.fit(x_train, y_train, validation_data=(x_val, y_val), epochs=50, batch_size=32)

    manager.save_model(model)
