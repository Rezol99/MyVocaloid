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


def split_audio(audio, ms, sr=SAMPLE_RATE):
    """
    音声ファイルを指定したミリ秒（ms）で分割し、先頭部分と残り部分を返す関数。
    
    Args:
        file_path (str): 音声ファイルのパス。
        ms (float): 分割する時間（ミリ秒単位）。
        sr (int): サンプリング周波数（デフォルト: 22050）。
        
    Returns:
        tuple: (先頭部分の音声, 残り部分の音声, サンプリング周波数)
    """
    # ミリ秒をサンプル数に変換
    num_samples = int(sr * (ms / 1000))
    
    # 先頭部分と残り部分に分割
    audio_head = audio[:num_samples]
    audio_tail = audio[num_samples:]
    
    return audio_head, audio_tail