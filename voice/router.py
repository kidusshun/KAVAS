import io
import os
import tempfile
import time
from .service import find_user_service
from pydub import AudioSegment
from database.db import get_db
from sqlalchemy.orm import Session

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException,
    BackgroundTasks,
    Depends,
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
    db: Session = Depends(get_db),
):
    start = time.time()
    temp_audio_path = await save_upload_file_tmp(file)
    background_tasks.add_task(clean_temp_file, temp_audio_path)

    # # Check if the file's extension is wav
    # if not file.content_type.startswith("audio/"):
    #     return {"error": "The uploaded file is not an audio file."}
    # if not file.filename.endswith(".wav"):
    #     contents = convert_to_wav(contents)

    res = find_user_service(temp_audio_path, db)
    lapse = time.time() - start
    return res, lapse
    return {"filename": file.filename, "content_type": file.content_type}


def convert_to_wav(contents: bytes) -> bytes:
    # Convert the contents to wav
    audio = AudioSegment.from_file(io.BytesIO(contents))

    # Create a BytesIO buffer for WAV output
    wav_buffer = io.BytesIO()

    # Export the audio as WAV to the buffer
    audio.export(wav_buffer, format="wav")

    return wav_buffer.getvalue()


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
