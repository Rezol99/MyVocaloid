from file_encoder import FileEncoder
from data_manager import DataManager
import numpy as np
import sys
import tensorflow as tf
from tensorflow.keras import layers, models, Model

TARGET_DIR = "./thirdparty/「波音リツ」歌声データベースVer2/DATABASE"
OUTPUT_DIR = "./master/ust/json"


def build_model(max_lyric_index, input_shapes, y_shape):
    input_lyric = layers.Input(shape=input_shapes[0], name="lyric_input")
    input_duration = layers.Input(shape=input_shapes[1], name="duration_input")
    input_notenum = layers.Input(shape=input_shapes[2], name="notenum_input")

    embed_lyric = layers.Embedding(
        input_dim=max_lyric_index + 1,
        output_dim=128
    )(input_lyric)
    lstm_output = layers.LSTM(256, return_sequences=False)(embed_lyric)

    dense_duration = layers.Dense(32, activation="relu")(input_duration)  # (None, 32)
    dense_notenum = layers.Dense(32, activation="relu")(input_notenum)    # (None, 32)

    concat_layer = layers.Concatenate(axis=1)([lstm_output, dense_duration, dense_notenum])

    dense_output = layers.Dense(512, activation="relu")(concat_layer)  # (None, 512)

    final_output = layers.Dense(np.prod(y_shape), activation="linear")(dense_output)
    final_output = layers.Reshape(y_shape)(final_output)

    model = Model(
        inputs=[input_lyric, input_duration, input_notenum],
        outputs=final_output
    )
    model.compile(optimizer="adam", loss="mse")
    return model


if __name__ == "__main__":
    need_encode = False

    if len(sys.argv) > 1:
        if sys.argv[1] == "--encode":
            need_encode = True
    
    manager = DataManager()

    if need_encode:
        encoder = FileEncoder(TARGET_DIR, OUTPUT_DIR)
        _, lyric_indexs, durations, notenums, y = encoder.encode()
        manager.save(lyric_indexs, durations, notenums, y)
    
    lyric_indexs, duration_indexs, notenum_indexs, y = manager.load()

    assert len(y) > 0 and len(lyric_indexs) > 0 and len(duration_indexs) > 0 and len(notenum_indexs) > 0

    print(f"lyric_indexs.shape: {lyric_indexs.shape}")
    print(f"lyric_indexs: {lyric_indexs}")
    print(f"duration_indexs.shape: {duration_indexs.shape}")
    print(f"duration_indexs: {duration_indexs}")
    print(f"notenum_indexs.shape: {notenum_indexs.shape}")
    print(f"notenum_indexs: {notenum_indexs}")
    print(f"y.shape: {y.shape}")
    print(f"y: {y}")

    (train_lyric, train_duration, train_notenum), (test_lyric, test_duration, test_notenum), y_train, y_test = manager.get_train_and_test_data()

    print(f"train_lyric.shape: {train_lyric.shape}")
    print(f"train_duration.shape: {train_duration.shape}")
    print(f"train_notenum.shape: {train_notenum.shape}")
    print(f"y_train.shape: {y_train.shape}")
    print(f"test_lyric.shape: {test_lyric.shape}")
    print(f"test_duration.shape: {test_duration.shape}")
    print(f"test_notenum.shape: {test_notenum.shape}")
    print(f"y_test.shape: {y_test.shape}")

    assert train_lyric.shape[0] == train_duration.shape[0] == train_notenum.shape[0] == y_train.shape[0]
    assert test_lyric.shape[0] == test_duration.shape[0] == test_notenum.shape[0] == y_test.shape[0]

    input_shapes = [(lyric_indexs.shape[1],), (duration_indexs.shape[1],), (notenum_indexs.shape[1],)]

    emmbed_lyric_dim = np.max(lyric_indexs) + 1
    print(f"emmbed_lyric_dim: {emmbed_lyric_dim}")
    emmbed_duration_dim = np.max(duration_indexs) + 1
    print(f"emmbed_duration_dim: {emmbed_duration_dim}")
    emmbed_notenum_dim = np.max(notenum_indexs) + 1
    print(f"emmbed_notenum_dim: {emmbed_notenum_dim}")

    max_lyric_index = np.max(lyric_indexs)

    model = build_model(max_lyric_index, input_shapes, y_train[0].shape)
    model.summary()

    model.fit(
        [train_lyric, train_duration, train_notenum],
        y_train,
        batch_size=32,
        epochs=10,
        validation_data=([test_lyric, test_duration, test_notenum], y_test)
    )
