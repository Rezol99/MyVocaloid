from data_manager import DataManager
from audio_utils import mel_to_audio, save_audio
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    manager = DataManager()
    print("Loading test data...")
    (train_lyric, train_duration, train_notenum), (test_lyric, test_duration, test_notenum), y_train, y_test = manager.get_train_and_test_data()
    x_test = np.stack([test_lyric, test_duration, test_notenum], axis=-1)
    print(f"Test data shapes: {[(x.shape) for x in x_test]}")
    model = manager.load_model()

    predicted_mel_spectrogram = model.predict(x_test)
    print(f"Predicted mel spectrogram shape: {predicted_mel_spectrogram.shape}")

    train_x_first = x_test[0]
    train_y_first = y_train[0]
    plt.plot(train_y_first)
    plt.title("Original Mel Spectrogram")
    plt.show()

    # test first plot
    test_x_first = x_test[0]
    test_y_first = predicted_mel_spectrogram[0]
    plt.plot(test_y_first)
    plt.title("Predicted Mel Spectrogram")
    plt.show()

    # mel spectrogram plot
    generated = mel_to_audio(predicted_mel_spectrogram[0])
    plt.plot(generated)
    plt.title("Generated Audio")
    plt.show()


    


    
    

