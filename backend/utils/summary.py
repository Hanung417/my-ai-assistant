from openai import OpenAI
import os
from dotenv import load_dotenv
from crud.memory import get_old_chat_messages, upsert_user_memory

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_old_chat_and_save(db, user_id="singleton"):
    old_messages = get_old_chat_messages(db, user_id=user_id)
    if not old_messages:
        return "요약할 메시지가 없습니다."

    # 요약할 메시지를 하나의 문자열로 결합
    full_text = "\n".join(
        [f"{m.role.upper()}: {m.message}" for m in old_messages]
    )

    # GPT에 요약 요청
    prompt = f"""
다음 대화 기록을 1~2문단으로 요약해줘. 사용자의 감정 상태, 일정, 주요 관심사를 중심으로 간결하게 정리해줘.

{full_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300,
        )
        summary = response.choices[0].message.content.strip()

        # user_memory에 저장
        upsert_user_memory(db, user_id, category="대화요약", content=summary)
        return "요약 저장 완료"
    except Exception as e:
        print("요약 중 오류:", e)
        return "요약 실패"