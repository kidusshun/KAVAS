import os
import torch
import torchaudio
from pyannote.audio import Model, Inference
from pydub import AudioSegment
import httpx

import numpy as np
from scipy.signal import butter, lfilter

from dotenv import load_dotenv
from kokoro import KPipeline
import tempfile

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")


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



model = Model.from_pretrained("pyannote/wespeaker-voxceleb-resnet34-LM")
inference = Inference(model, window="whole")

pipeline = KPipeline(lang_code='a')


def preprocess_audio_in_memory(audio_path: str):
    # Step 1: Convert to 16kHz Mono WAV format
    audio = convert_audio_in_memory(input_file=audio_path)

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        temp_path = temp_file.name
        audio.export(temp_path, format="wav")
        return temp_path


def convert_audio_in_memory(input_file):
    """Convert audio to 16kHz mono WAV format for Pyannote"""
    audio = AudioSegment.from_file(input_file)
    return audio.set_frame_rate(16000).set_channels(1)


def pyannote_embed_audio(audio_path):
    return inference(audio_path)


async def whisper_transcribe(audio_path: str):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            with open(audio_path, "rb") as file:
                files = {"file": (file.name, file, "audio/m4a")}
                response = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                    },
                    data={
                        "model": "whisper-large-v3-turbo",
                        "response_format": "verbose_json",
                    },
                    files=files,
                )
                return response.json()
    except Exception as e:
        raise e


def generate_speech(text:str) -> bytes:
    generator = pipeline(
        text, voice='af_bella', # <= change voice here
        speed=1, split_pattern=r'\n+'
    )

    result = list(generator)

    return result[0].output.audio.cpu().numpy().tobytes()
        