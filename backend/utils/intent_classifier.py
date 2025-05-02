from openai import OpenAI
import os
import re
from dotenv import load_dotenv
from typing import Literal

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ 1차: 로컬 키워드 기반 빠른 intent 분류 (KoNLPy 없이 간단하게)
def fast_rule_based_intent(message: str) -> Literal["시간", "요일", "날씨", "기억", "기타"]:
    msg = re.sub(r"\s+", "", message.lower())  # 소문자 + 공백 제거

    if any(kw in msg for kw in ["몇시", "현재시간", "지금시간", "시간알려줘", "시각"]):
        return "시간"
    if "요일" in msg or "무슨요일" in msg:
        return "요일"
    if any(kw in msg for kw in ["날씨", "기온", "우산", "비올까", "비와", "날씨어때"]):
        return "날씨"
    return "기타"

# ✅ 2차: GPT 기반 intent 분류 (rule이 불확실할 때 보완)
def gpt_fallback_intent(message: str) -> str | None:
    prompt = f"""
다음 문장의 의도를 아래 중 하나로 분류해줘. 하나만 고르고 JSON으로 출력해.
- 시간
- 요일
- 날씨
- 기억
- 기타

문장: "{message}"
형식: {{ "intent": "날씨" }}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=50
        )
        import json
        return json.loads(response.choices[0].message.content)["intent"]
    except Exception as e:
        print("❌ GPT intent 분류 오류:", e)
        return None

# ✅ 통합 intent 분류 함수
def classify_intent(message: str) -> str:
    rule_intent = fast_rule_based_intent(message)
    if rule_intent != "기타":
        return rule_intent
    gpt_intent = gpt_fallback_intent(message)
    return gpt_intent or "기타"

