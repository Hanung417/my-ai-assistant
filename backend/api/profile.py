from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.session import SessionLocal
from crud.memory import upsert_user_memory

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PreferenceRequest(BaseModel):
    prompt: str  # 유저 ID 제거

@router.post("/profile/update-prompt")
def update_user_prompt(data: PreferenceRequest, db: Session = Depends(get_db)):
    upsert_user_memory(db, user_id="singleton", category="성향", content=data.prompt)
    return {"message": "성향이 저장되었습니다."}
