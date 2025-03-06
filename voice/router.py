import io
import os
import tempfile
import time
from .service import find_user_service, generate_speech_service
import av
from typing import Optional

# from pydub import AudioSegment
from dependencies import get_db
from sqlalchemy.orm import Session
from psycopg2.extensions import connection

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException,
    BackgroundTasks,
    Depends,
    Body,
)

voice_router = APIRouter(prefix="/voice", tags=["voice"])


@voice_router.get("/test")
async def test():
    return {"message": "Hello, World!"}


def clean_temp_file(file_path: str):
    """Remove temporary file"""
    try:
        os.unlink(file_path)
    except Exception as e:
        print(f"Error deleting temporary file {file_path}: {e}")


@voice_router.post("/process")
async def process(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_name: Optional[str] = Body(None),
    conn: connection = Depends(get_db),
):
    start = time.time()
    temp_audio_path = await save_upload_file_tmp(file)
    background_tasks.add_task(clean_temp_file, temp_audio_path)

    # # Check if the file's extension is wav
    # if not file.content_type.startswith("audio/"):
    #     return {"error": "The uploaded file is not an audio file."}
    # if not file.filename.endswith(".wav"):
    #     contents = convert_to_wav(contents)

    res = await find_user_service(audio_file_path=temp_audio_path,user_name=user_name, conn= conn,)
    lapse = time.time() - start
    return res, lapse


@voice_router.post("/tts")
async def generate_speech(
    text: str = Body(...),
    conn: connection = Depends(get_db),
):
    start = time.time()
    # Get the audio from the text
    audio = generate_speech_service(text, conn)
    lapse = time.time() - start
    return str(audio)




# def convert_to_wav(contents: bytes) -> bytes:
#     # Convert the contents to wav
#     audio = AudioSegment.from_file(io.BytesIO(contents))

#     # Create a BytesIO buffer for WAV output
#     wav_buffer = io.BytesIO()

#     # Export the audio as WAV to the buffer
#     audio.export(wav_buffer, format="wav")

#     return wav_buffer.getvalue()


async def save_upload_file_tmp(upload_file: UploadFile) -> str:
    """Save an upload file temporarily and return its path"""
    try:
        suffix = os.path.splitext(upload_file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await upload_file.read()
            tmp.write(content)
            return tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")
