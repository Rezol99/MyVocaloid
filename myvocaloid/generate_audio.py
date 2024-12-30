from data_manager import DataManager
from audio_utils import mel_to_audio, save_audio
import numpy as np


if __name__ == "__main__":
    manager = DataManager()
    print("Loading test data...")
    (train_lyric, train_duration, train_notenum), (test_lyric, test_duration, test_notenum), y_train, y_test = manager.get_train_and_test_data()
    x_test = np.stack([test_lyric, test_duration, test_notenum], axis=-1)
    print(f"Test data shapes: {[(x.shape) for x in x_test]}")
    model = manager.load_model()

    predicted_mel_spectrogram = model.predict(x_test)
    print(f"Predicted mel spectrogram shape: {predicted_mel_spectrogram.shape}")

    for i in range(1, 10):
        audio = mel_to_audio(predicted_mel_spectrogram[i])
        save_audio(f"./gen/generated_audio_{i}.wav", audio)
        print(f"Generated audio saved as generated_audio_{i}.wav")

