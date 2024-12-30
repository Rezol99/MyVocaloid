from data_manager import DataManager
from audio_utils import mel_to_audio, save_audio


if __name__ == "__main__":
    manager = DataManager()
    x_train, x_test, y_train, y_test = manager.get_train_and_test_data()
    model = manager.load_model()

    predicted_mel_spectrogram = model.predict(x_test)
    print(f"Predicted mel spectrogram shape: {predicted_mel_spectrogram.shape}")

    audio = mel_to_audio(predicted_mel_spectrogram[0]) 

    save_audio("./gen/generated_audio.wav", audio)
