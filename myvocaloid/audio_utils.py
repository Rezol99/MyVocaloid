import librosa
import soundfile as sf


SAMPLE_RATE = 1024
N_MELS = 128


def load_audio(file_path, sr=SAMPLE_RATE):
    audio, _ = librosa.load(file_path, sr=sr)
    return audio

def save_audio(file_path, audio, sr=SAMPLE_RATE):
    sf.write(file_path, audio, sr)


def mel_to_audio(mel_spectrogram, sr=SAMPLE_RATE, n_iter=32):
    stft = librosa.feature.inverse.mel_to_stft(mel_spectrogram, sr=sr)
    audio = librosa.griffinlim(stft, n_iter=n_iter)
    return audio

def audio_to_mel(audio, sr=SAMPLE_RATE, n_mels=N_MELS):
    mel_spectrogram = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=n_mels)
    return mel_spectrogram