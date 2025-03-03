from .repository import identify_user, add_user_to_db
from .utils import preprocess_audio, get_speaker_embedding
from sqlalchemy.orm import Session


def find_user_service(audio_file_path: str, db: Session):
    processed_audio = preprocess_audio(audio_path=audio_file_path)
    embedded_voice = get_speaker_embedding(processed_audio)

    user = identify_user(embedded_voice, db)
    if user == "Unknown":
        user = add_user_to_db(embedded_voice, db)
    return user
