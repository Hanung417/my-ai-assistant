# 📄 routers/chat.py — 모든 기능 통합본: 자동 요약 + 기억 기반 응답 포함

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from db.session import SessionLocal
from crud.memory import (
    get_recent_chat_messages,
    save_chat_message,
    get_user_memory,
    search_user_memory,
    upsert_user_memory,
)
from utils.keyword_extraction import extract_keywords_with_gpt
from utils.build_prompt import build_system_prompt
from utils.auto_reply import get_auto_reply_with_intent, style_reply_with_prompt
from utils.memory_classification import classify_and_extract_memory
from utils.memory_answer import search_memory_answer
from utils.summary import summarize_old_chat_and_save

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    system_prompt: str = "당신은 친근한 AI 비서입니다."

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/chat")
def generate_gpt_response(chat_request: ChatRequest, db: Session = Depends(get_db)) -> dict:
    try:
        user_id = "singleton"

        # ✅ 1. 기억 기반 질문이면 직접 응답
        memory_based_response = search_memory_answer(db, user_id, chat_request.message)
        if memory_based_response:
            return {"answer": memory_based_response}

        # ✅ 2. 의미 기반 자동응답
        auto_response = get_auto_reply_with_intent(chat_request.message)
        if auto_response:
            user_persona = get_user_memory(db, user_id, category="성향")
            system_prompt = user_persona.content if user_persona else chat_request.system_prompt
            styled_response = style_reply_with_prompt(system_prompt, auto_response)
            return {"answer": styled_response}

        # ✅ 3. 최근 대화 불러오기
        past_messages = get_recent_chat_messages(db, user_id, limit=10)
        messages = [{"role": m.role, "content": m.message} for m in reversed(past_messages)]

        # ✅ 4. 사용자 성향
        user_persona = get_user_memory(db, user_id, category="성향")
        base_prompt = user_persona.content if user_persona else chat_request.system_prompt

        # ✅ 5. long-term memory 요약
        long_memory = get_user_memory(db, user_id, category="대화요약")

        # ✅ 6. 키워드 추출 + 관련 기억 검색
        keywords = extract_keywords_with_gpt(chat_request.message)
        related_memories = []
        for kw in keywords:
            related_memories += search_user_memory(db, keyword=kw)

        # ✅ 7. system prompt 조립
        full_prompt = build_system_prompt(
            base_prompt=base_prompt,
            long_memory=long_memory,
            related_memories=related_memories
        )

        # ✅ 8. GPT 메시지 구성 및 호출
        messages.insert(0, {"role": "system", "content": full_prompt})
        messages.append({"role": "user", "content": chat_request.message})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.8,
            max_tokens=500,
        )
        gpt_answer = response.choices[0].message.content.strip()

        # ✅ 9. 대화 저장
        save_chat_message(db, user_id, "user", chat_request.message)
        save_chat_message(db, user_id, "assistant", gpt_answer)

        # ✅ 10. 사용자 입력 → 기억 자동 저장
        memory_data = classify_and_extract_memory(chat_request.message)
        if memory_data and memory_data["category"] != "기타":
            upsert_user_memory(
                db=db,
                user_id=user_id,
                category=memory_data["category"],
                content=memory_data["content"]
            )

        # ✅ 11. 일정량 이상 쌓이면 대화 요약
        if len(past_messages) >= 10:
            summarize_old_chat_and_save(db, user_id)

        return {"answer": gpt_answer}

    except Exception as e:
        print("❌ GPT 오류:", e)
        return {"answer": "Sorry, something went wrong. Please try again."}

