from pydantic import BaseModel
from uuid import UUID


class TranscriptionResponse(BaseModel):
    userid: UUID
    transcription: str
