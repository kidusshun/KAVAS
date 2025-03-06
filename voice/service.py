from .repository import identify_user, add_user_to_db
from .utils import (
    preprocess_audio,
    get_speaker_embedding,
    pyannote_embed_audio,
    whisper_transcribe,
    generate_speech,
)
from sqlalchemy.orm import Session
from .types import TranscriptionResponse
import httpx



async def find_user_service(*,audio_file_path: str,user_name:str | None, db: Session,) -> TranscriptionResponse:
    # speechbrain version
    # processed_audio = preprocess_audio(audio_path=audio_file_path)
    # embedded_voice = get_speaker_embedding(processed_audio)

    # pyannote version
    embedded_voice = pyannote_embed_audio(audio_path=audio_file_path)

    response = await whisper_transcribe(audio_path=audio_file_path)

    print(response)

    transcription = response["text"]

    user_id = identify_user(embedded_voice, db)
    if not user_id:
        user_id = add_user_to_db(embedded_voice,user_name, db)

    response = TranscriptionResponse(userid=user_id, transcription=transcription)
    return response


def generate_speech_service(text: str, db: Session) -> bytes:
    text = text.replace('\n', '')

    return generate_speech(text)


