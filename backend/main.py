from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import chat, generate_character_image, profile, memory, calendar

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(generate_character_image.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(memory.router, prefix="/api")
app.include_router(calendar.router, prefix="/api")