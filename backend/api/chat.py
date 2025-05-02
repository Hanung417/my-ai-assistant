from fastapi import APIRouter, Depends
from pydantic import BaseModel
from openai import OpenAI
import os
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import dateutil.parser
import locale
import pytz

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
from utils.calendar_parser import extract_schedule_from_text

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

        # ✅ 일정 삭제 요청 감지
        if any(kw in chat_request.message for kw in ["일정 삭제", "일정 취소", "삭제해줘", "취소해줘"]):
            try:
                keyword = chat_request.message.replace("일정", "").replace("삭제", "").replace("취소", "").strip()
                search = requests.get("http://localhost:8000/api/calendar/search", params={"query": keyword}).json()
                events = search.get("events", [])
                if not events:
                    return {"answer": "삭제할 일정을 찾지 못했어요."}
                event_id = events[0]['id']
                requests.delete("http://localhost:8000/api/calendar/delete", params={"event_id": event_id})
                return {"answer": f"'{events[0]['summary']}' 일정을 삭제했어요."}
            except Exception as e:
                print("❌ 일정 삭제 오류:", e)
                return {"answer": "일정 삭제 중 문제가 발생했어요."}

        # ✅ 일정 수정 요청 감지
        if any(kw in chat_request.message for kw in ["일정 수정", "일정 변경", "시간 바꿔", "시간 변경"]):
            try:
                schedule_data = extract_schedule_from_text(chat_request.message)
                if not schedule_data:
                    return {"answer": "어떤 일정인지 찾을 수 없어요. 제목과 시간을 명확히 말씀해주세요."}
                search = requests.get("http://localhost:8000/api/calendar/search", params={"query": schedule_data['title']}).json()
                events = search.get("events", [])
                if not events:
                    return {"answer": "수정할 일정을 찾지 못했어요."}
                event_id = events[0]['id']
                requests.put(
                    f"http://localhost:8000/api/calendar/update?event_id={event_id}",
                    json=schedule_data
                )
                return {"answer": f"'{schedule_data['title']}' 일정을 수정했어요."}
            except Exception as e:
                print("❌ 일정 수정 오류:", e)
                return {"answer": "일정 수정 중 문제가 발생했어요."}

        # ✅ 이번 주/다음 주 일정 조회
        if any(kw in chat_request.message for kw in ["이번 주 일정", "다음 주 일정", "일정 보여줘"]):
            try:
                tz = pytz.timezone("Asia/Seoul")
                now = datetime.now(tz)

                if "다음 주" in chat_request.message:
                    this_monday = now - timedelta(days=now.weekday())
                    next_monday = this_monday + timedelta(days=7)
                    next_sunday = next_monday + timedelta(days=6)
                    start = next_monday.replace(hour=0, minute=0, second=0, microsecond=0)
                    end = next_sunday.replace(hour=23, minute=59, second=59, microsecond=0)
                else:
                    start = now
                    end = now + timedelta(days=7)

                res = requests.get("http://localhost:8000/api/calendar/range", params={"start": start.isoformat(), "end": end.isoformat()})
                events = res.json().get("events", [])
                if not events:
                    return {"answer": "해당 주간에는 등록된 일정이 없습니다."}
                formatted_events = []
                for e in events:
                    raw_time, title = e.split(" - ")
                    dt = dateutil.parser.parse(raw_time)
                    time_str = dt.strftime("%m월 %d일 %p %I:%M").replace("AM", "오전").replace("PM", "오후")
                    formatted_events.append(f"• {time_str} - {title}")

                # GPT 연계 요약
                gpt_messages = [
                    {"role": "system", "content": f"다음은 사용자의 주간 일정입니다:\n" + "\n".join(formatted_events) + "\n이 일정들을 요약하고 중요한 일정이 있으면 강조해주세요."},
                    {"role": "user", "content": chat_request.message}
                ]
                gpt_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=gpt_messages,
                    temperature=0.8,
                    max_tokens=500,
                )
                return {"answer": gpt_response.choices[0].message.content.strip()}

            except Exception as e:
                print("❌ 주간 일정 조회 오류:", e)
                return {"answer": "일정을 불러오는 데 문제가 생겼어요."}


        # ✅ 오늘/내일/모레 일정 조회
        if any(kw in chat_request.message for kw in ["오늘 일정", "내일 일정", "모레 일정"]):
            tz = pytz.timezone("Asia/Seoul")
            now = datetime.now(tz)
            target_date = None
            if "오늘" in chat_request.message:
                target_date = now
            elif "내일" in chat_request.message:
                target_date = now + timedelta(days=1)
            elif "모레" in chat_request.message:
                target_date = now + timedelta(days=2)

            if target_date:
                try:
                    start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    end = start + timedelta(days=1)
                    res = requests.get("http://localhost:8000/api/calendar/range", params={"start": start.isoformat(), "end": end.isoformat()})
                    events = res.json().get("events", [])
                    if not events:
                        return {"answer": f"{chat_request.message.split('일정')[0]}은 등록된 일정이 없습니다."}
                    formatted_events = []
                    for e in events:
                        raw_time, title = e.split(" - ")
                        dt = dateutil.parser.parse(raw_time)
                        time_str = dt.strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")
                        formatted_events.append(f"• {time_str} - {title}")

                    # GPT 연계 답변
                    gpt_messages = [
                        {"role": "system", "content": f"다음은 사용자의 일정입니다:\n" + "\n".join(formatted_events) + "\n이 일정 외에 추천도 해주세요."},
                        {"role": "user", "content": chat_request.message}
                    ]
                    gpt_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=gpt_messages,
                        temperature=0.8,
                        max_tokens=500,
                    )
                    return {"answer": gpt_response.choices[0].message.content.strip()}
                except Exception as e:
                    print("❌ 일정 범위 조회 오류:", e)
                    return {"answer": "일정을 불러오는 데 문제가 생겼어요."}

        # ✅ 일정 등록 요청
        if any(kw in chat_request.message for kw in ["일정 등록", "일정 추가", "일정 넣어", "약속 잡아", "예약 해줘"]):
            schedule_data = extract_schedule_from_text(chat_request.message)
            print("[GPT 일정 추출 결과]", schedule_data)
            if schedule_data:
                res = requests.post("http://localhost:8000/api/calendar/add", json=schedule_data)
                if res.status_code == 200:
                    upsert_user_memory(
                        db=db,
                        user_id=user_id,
                        category="일정",
                        content=f"{schedule_data['start_time']}에 '{schedule_data['title']}' 일정이 있었어요."
                    )
                    return {"answer": f"'{schedule_data['title']}' 일정을 등록했어요!"}
                else:
                    return {"answer": "일정을 등록하는 데 문제가 생겼어요."}

        # ✅ 기억 기반 응답
        memory_based_response = search_memory_answer(db, user_id, chat_request.message)
        if memory_based_response:
            return {"answer": memory_based_response}

        # ✅ 의미 기반 자동응답
        auto_response = get_auto_reply_with_intent(chat_request.message)
        if auto_response:
            user_persona = get_user_memory(db, user_id, category="성향")
            system_prompt = user_persona.content if user_persona else chat_request.system_prompt
            styled_response = style_reply_with_prompt(system_prompt, auto_response)
            return {"answer": styled_response}

        # ✅ 최근 대화 불러오기
        past_messages = get_recent_chat_messages(db, user_id, limit=10)
        messages = [{"role": m.role, "content": m.message} for m in reversed(past_messages)]

        # ✅ 사용자 성향
        user_persona = get_user_memory(db, user_id, category="성향")
        base_prompt = user_persona.content if user_persona else chat_request.system_prompt

        # ✅ long-term memory 요약
        long_memory = get_user_memory(db, user_id, category="대화요약")

        # ✅ 관련 기억 검색
        keywords = extract_keywords_with_gpt(chat_request.message)
        related_memories = []
        for kw in keywords:
            related_memories += search_user_memory(db, keyword=kw)

        # ✅ GPT 호출
        full_prompt = build_system_prompt(base_prompt, long_memory, related_memories)
        messages.insert(0, {"role": "system", "content": full_prompt})
        messages.append({"role": "user", "content": chat_request.message})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.8,
            max_tokens=500,
        )
        gpt_answer = response.choices[0].message.content.strip()

        # ✅ 대화 저장
        save_chat_message(db, user_id, "user", chat_request.message)
        save_chat_message(db, user_id, "assistant", gpt_answer)

        # ✅ 기억 저장
        memory_data = classify_and_extract_memory(chat_request.message)
        if memory_data and memory_data["category"] != "기타":
            upsert_user_memory(db, user_id, memory_data["category"], memory_data["content"])

        # ✅ 대화 요약
        if len(past_messages) >= 10:
            summarize_old_chat_and_save(db, user_id)

        return {"answer": gpt_answer}

    except Exception as e:
        print("❌ GPT 오류:", e)
        return {"answer": "Sorry, something went wrong. Please try again."}