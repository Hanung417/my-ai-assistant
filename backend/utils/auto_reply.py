import os
from dotenv import load_dotenv
from openai import OpenAI
from utils.context_info import get_context_data
from utils.intent_classifier import classify_intent

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_auto_reply_with_intent(message: str) -> str | None:
    """
    의미 기반 intent 분류를 통해 자동 응답 메시지를 생성합니다.
    intent는 '시간', '요일', '날씨', 그 외 '기타'입니다.
    """
    intent = classify_intent(message)
    context = get_context_data()
    time = context["time"]
    weather = context["weather"]
    city = context["location"]["city"]

    if intent == "시간":
        return f"지금은 {time['time']}입니다."
    elif intent == "요일":
        return f"오늘은 {time['weekday']}입니다."
    elif intent == "날씨":
        return (
            f"현재 {city}의 날씨는 {weather.get('sky', '정보 없음')}이고, "
            f"기온은 {weather.get('temperature', '')}, "
            f"강수확률은 {weather.get('rain_prob', '')}, "
            f"습도는 {weather.get('humidity', '')}입니다."
        )
    else:
        return None  # GPT로 넘길 질문

def style_reply_with_prompt(prompt: str, raw_answer: str) -> str:
    """
    사용자의 성향 prompt를 반영해 자동 응답 메시지를 GPT 스타일로 재작성합니다.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"다음 문장을 너의 말투로 자연스럽게 바꿔줘:\n\"{raw_answer}\""}
            ],
            temperature=0.7,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ 스타일링 오류:", e)
        return raw_answer
