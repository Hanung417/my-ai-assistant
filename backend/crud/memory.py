from sqlalchemy.orm import Session
from models.memory import ChatMemory, UserMemory
from datetime import datetime, timedelta

def save_chat_message(db: Session, user_id: str, role: str, message: str):
    chat = ChatMemory(user_id=user_id, role=role, message=message, created_at=datetime.utcnow())
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

def get_recent_chat_messages(db: Session, user_id: str, limit: int = 10):
    return (
        db.query(ChatMemory)
        .filter(ChatMemory.user_id == user_id)
        .order_by(ChatMemory.created_at.desc())
        .limit(limit)
        .all()
    )

def upsert_user_memory(db: Session, user_id: str, category: str, content: str):
    existing = (
        db.query(UserMemory)
        .filter(UserMemory.user_id == user_id, UserMemory.category == category)
        .first()
    )
    if existing:
        existing.content = content
        existing.updated_at = datetime.utcnow()
    else:
        memory = UserMemory(user_id=user_id, category=category, content=content)
        db.add(memory)
    db.commit()

def get_user_memory(db: Session, user_id: str, category: str):
    return (
        db.query(UserMemory)
        .filter(UserMemory.user_id == user_id, UserMemory.category == category)
        .first()
    )
    
def search_user_memory(db: Session, keyword: str, limit: int = 5):
    return (
        db.query(UserMemory)
        .filter(UserMemory.content.contains(keyword))  # SQLite LIKE 검색
        .order_by(UserMemory.updated_at.desc())
        .limit(limit)
        .all()
    )

def get_old_chat_messages(db: Session, user_id: str, days_ago: int = 3):
    threshold = datetime.utcnow() - timedelta(days=days_ago)
    return (
        db.query(ChatMemory)
        .filter(ChatMemory.user_id == user_id, ChatMemory.created_at < threshold)
        .order_by(ChatMemory.created_at)
        .all()
    )
    
def get_all_user_memory(db, user_id: str):
    return db.query(UserMemory).filter(UserMemory.user_id == user_id).all()