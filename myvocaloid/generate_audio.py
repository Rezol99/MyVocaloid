import numpy as np
import librosa
import soundfile as sf
from data_manager import DataManager


if __name__ == "__main__":

    manager = DataManager()
    x_train, x_test, y_train, y_test = manager.get_train_and_test_data()
    model = manager.load_model()

    predicted_mel_spectrogram = model.predict(x_test)
    print(f"Predicted mel spectrogram shape: {predicted_mel_spectrogram.shape}")

    def mel_to_audio(mel_spectrogram, sr=1024, n_iter=32):
        stft = librosa.feature.inverse.mel_to_stft(mel_spectrogram, sr=sr)
        audio = librosa.griffinlim(stft, n_iter=n_iter)
        return audio

    audio = mel_to_audio(predicted_mel_spectrogram[0]) 

    sf.write("./gen/generated_audio.wav", audio, 1024) 
