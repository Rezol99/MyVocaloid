import librosa
import soundfile as sf


SAMPLE_RATE = 16000
N_MELS = 128
N_FFT = 1024
HOP_LENGTH = 256


def load_audio(file_path, sr=SAMPLE_RATE):
    audio, _ = librosa.load(file_path, sr=sr)
    return audio

def save_audio(file_path, audio, sr=SAMPLE_RATE):
    sf.write(file_path, audio, sr)


def audio_to_mel(audio, sr=SAMPLE_RATE, n_mels=N_MELS, n_fft=N_FFT, hop_length=HOP_LENGTH):
    mel_spectrogram = librosa.feature.melspectrogram(
        y=audio, sr=sr, n_mels=n_mels, n_fft=n_fft , hop_length=hop_length
    )
    log_mel_spectrogram = librosa.power_to_db(mel_spectrogram)
    return log_mel_spectrogram

def mel_to_audio(log_mel_spec, sr=SAMPLE_RATE, n_iter=32, n_fft=N_FFT, hop_length=HOP_LENGTH):
    # メルスペクトログラムをパワースペクトログラムに変換
    power_mel = librosa.db_to_power(log_mel_spec)

    # メルスペクトログラムから直接音声を復元
    audio = librosa.feature.inverse.mel_to_audio(
        power_mel,
        sr=sr,
        n_fft=n_fft,
        hop_length=hop_length,
        n_iter=n_iter,
    )
    return audio