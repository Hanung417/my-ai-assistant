from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import chat, generate_character_image  # ✅ 여기 있어야 함

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React용 CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(generate_character_image.router, prefix="/api")  # ✅ 반드시 포함