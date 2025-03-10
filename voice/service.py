import uuid
from .repository import identify_user, add_user_to_db
from .utils import (
    pyannote_embed_audio,
    whisper_transcribe,
    generate_speech,
    preprocess_audio_in_memory,
)
from .types import TranscriptionResponse
import httpx
from psycopg2.extensions import connection


async def find_user_service(*,audio_file_path: str,user_name:str | None, conn: connection,) -> TranscriptionResponse:
    # preprocess
    # preprocessed_audio_path = preprocess_audio_in_memory(audio_file_path)
    
    
    # speechbrain version
    # processed_audio = preprocess_audio(audio_path=audio_file_path)
    # embedded_voice = get_speaker_embedding(processed_audio)

    # pyannote version
    embedded_voice = pyannote_embed_audio(audio_path=audio_file_path)

    response = await whisper_transcribe(audio_path=audio_file_path)

    transcription = response["text"]

    user_id = identify_user(embedded_voice, conn=conn)
    if not user_id:
        user_id = add_user_to_db(embedded_voice,user_name, conn=conn)

    response = TranscriptionResponse(userid=uuid.UUID(user_id), transcription=transcription)
    return response


def generate_speech_service(text: str) -> bytes:
    text = text.replace('\n', '')

    return generate_speech(text)


