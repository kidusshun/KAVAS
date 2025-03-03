from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from voice.router import voice_router


app = FastAPI()

app.include_router(voice_router)
