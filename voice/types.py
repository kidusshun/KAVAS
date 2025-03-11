from pydantic import BaseModel
from uuid import UUID


class TranscriptionResponse(BaseModel):
    userid: UUID |None
    transcription: str |None

class STTRequest(BaseModel):
    text:str