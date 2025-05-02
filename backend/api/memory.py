from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.session import SessionLocal
from utils.summary import summarize_old_chat_and_save, upsert_user_memory
from utils.memory_classification import classify_and_extract_memory

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/memory/summarize")
def summarize_old_chat_api(db: Session = Depends(get_db)):
    result = summarize_old_chat_and_save(db)
    return {"message": result}

class AutoMemoryInput(BaseModel):
    message: str

@router.post("/memory/auto-save")
def auto_save_memory(data: AutoMemoryInput, db: Session = Depends(get_db)):
    result = classify_and_extract_memory(data.message)
    if result:
        upsert_user_memory(
            db,
            user_id="singleton",
            category=result["category"],
            content=result["content"]
        )
        return {"message": "기억 저장 완료", "category": result["category"]}
    else:
        return {"message": "기억 저장 실패"}