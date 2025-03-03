import io
import torch
import torchaudio
from speechbrain.pretrained import SpeakerRecognition

import numpy as np
from scipy.signal import butter, lfilter


def normalize(audio, target_amplitude=0.9):
    max_val = np.max(np.abs(audio))
    if max_val > target_amplitude:
        audio *= target_amplitude / max_val
    return audio


def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype="band")
    y = lfilter(b, a, data)
    return y


speaker_model = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb", savedir="tmp_model"
)


def get_speaker_embedding(preprocessed_signal: torch.Tensor):
    embedding = speaker_model.encode_batch(preprocessed_signal)
    return embedding.squeeze().detach().cpu().numpy()


def preprocess_audio(audio_path: str, fs=16000):
    signal, _ = torchaudio.load(audio_path, backend="av")
    signal_np = signal.cpu().numpy().squeeze()

    cleaned_signal_np = bandpass_filter(signal_np, lowcut=300, highcut=3400, fs=fs)

    cleaned_signal_np = normalize(cleaned_signal_np)

    cleaned_signal = torch.from_numpy(cleaned_signal_np).unsqueeze(0)

    return cleaned_signal
