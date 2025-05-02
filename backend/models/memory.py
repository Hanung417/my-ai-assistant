from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
from sqlalchemy import Enum

Base = declarative_base()

class MemoryCategory(str, enum.Enum):
    성향 = "성향"
    일정 = "일정"
    취향 = "취향"
    이름 = "이름"
    기억요약 = "기억요약"
    기타 = "기타"

# 1. 대화 메모리 (Short-term)
class ChatMemory(Base):
    __tablename__ = "chat_memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'system', 'user', 'assistant'
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# 2. 사용자 메모리 (Long-term)
class UserMemory(Base):
    __tablename__ = "user_memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    category = Column(Enum(MemoryCategory), nullable=False)
    content = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

