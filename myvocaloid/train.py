from file_encoder import FileEncoder
from data_manager import DataManager
from audio_utils import SAMPLE_RATE, N_MELS
import numpy as np
import sys
import tensorflow as tf
from tensorflow.keras import layers, models, Model

TARGET_DIR = "../thirdparty/「波音リツ」歌声データベースVer2/DATABASE"
OUTPUT_DIR = "../master/ust/json"


if __name__ == "__main__":
    need_encode = True

    if len(sys.argv) > 1:
        if sys.argv[1] == "--encode":
            need_encode = True
    
    manager = DataManager()

    if need_encode:
        encoder = FileEncoder(TARGET_DIR, OUTPUT_DIR)
        names, lyric_indexs, durations, notenums, y = encoder.encode()
        manager.save(lyric_indexs, durations, notenums, names, y)
    
    lyric_indexs, duration_indexs, notenum_indexs, names, y = manager.load()

    assert len(y) > 0 and len(lyric_indexs) > 0 and len(duration_indexs) > 0 and len(notenum_indexs) > 0

    """
    print(f"lyric_indexs.shape: {lyric_indexs.shape}")
    print(f"lyric_indexs: {lyric_indexs}")
    print(f"duration_indexs.shape: {duration_indexs.shape}")
    print(f"duration_indexs: {duration_indexs}")
    print(f"notenum_indexs.shape: {notenum_indexs.shape}")
    print(f"notenum_indexs: {notenum_indexs}")
    print(f"y.shape: {y.shape}")
    print(f"y: {y}")

    print(f"train_lyric.shape: {train_lyric.shape}")
    print(f"train_duration.shape: {train_duration.shape}")
    print(f"train_notenum.shape: {train_notenum.shape}")
    print(f"y_train.shape: {y_train.shape}")
    print(f"test_lyric.shape: {test_lyric.shape}")
    print(f"test_duration.shape: {test_duration.shape}")
    print(f"test_notenum.shape: {test_notenum.shape}")
    print(f"y_test.shape: {y_test.shape}")
    
    """


    (train_lyric, train_duration, train_notenum), (test_lyric, test_duration, test_notenum), y_train, y_test = manager.get_train_and_test_data()
    assert train_lyric.shape[0] == train_duration.shape[0] == train_notenum.shape[0] == y_train.shape[0]
    assert test_lyric.shape[0] == test_duration.shape[0] == test_notenum.shape[0] == y_test.shape[0]

    emmbed_lyric_dim = np.max(lyric_indexs) + 1
    print(f"emmbed_lyric_dim: {emmbed_lyric_dim}")
    emmbed_duration_dim = np.max(duration_indexs) + 1
    print(f"emmbed_duration_dim: {emmbed_duration_dim}")
    emmbed_notenum_dim = np.max(notenum_indexs) + 1
    print(f"emmbed_notenum_dim: {emmbed_notenum_dim}")

    max_lyric_index = np.max(lyric_indexs)

    train_x = [train_lyric, train_duration, train_notenum]

    print("timestep", y_train.shape[1])
    print("y_train.shape", y_train.shape)
    print("y_train[0].shape[1:]", y_train[0].shape[1:])
    print("train_lyric.shape[1:]", train_lyric.shape[1:])


    lyric_input = tf.keras.Input(shape=train_lyric.shape[1:], name="lyric_input", dtype="float32")
    duration_input = tf.keras.Input(shape=train_duration.shape[1:], name="duration_input")
    notenum_input = tf.keras.Input(shape=train_notenum.shape[1:], name="notenum_input", dtype="float32")

    lyric_embedded = layers.Embedding(input_dim=max_lyric_index + 1, output_dim=128)(lyric_input)

    duration_reshaped = layers.Reshape((784, 1))(duration_input)
    notenum_reshaped = layers.Reshape((784, 1))(notenum_input)


    merged = layers.Concatenate()([lyric_embedded, duration_reshaped, notenum_reshaped])

    lstm_out = layers.LSTM(256, return_sequences=True)(merged)
    lstm_out = layers.LSTM(256, return_sequences=True)(lstm_out)

    pooled_out = layers.AveragePooling1D(pool_size=784 // 128)(lstm_out)[:, :128, :]
    
    output = layers.TimeDistributed(layers.Dense(13660, activation='linear'))(pooled_out)

    model = tf.keras.Model(
        [lyric_input, duration_input, notenum_input],
        outputs=output,
        name="vocaloid_model"
    )

    model.compile(
        optimizer='adam', 
        loss='mse',
        metrics=['mae']
    )

    model.fit(
       [train_lyric, train_duration, train_notenum],  # 入力データ（リスト形式）
        y_train,  # 出力データ
        batch_size=16,
        epochs=150,
       validation_split=0.2  # 20%を検証用データに分割
    )
    
   



    predictions = model.predict(
        [test_lyric, test_duration, test_notenum],  # 検証用データ
        batch_size=8
    )
    print("Predictions shape:", predictions.shape)

    model.save("../data/model.keras")