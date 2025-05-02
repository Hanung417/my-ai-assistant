from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_and_extract_memory(user_input: str):
    prompt = f"""
다음 문장을 보고, 이 문장이 어떤 카테고리에 해당하는지 분류해줘.
category는 아래 중 하나로만 골라줘:
- 성향
- 일정
- 취향
- 이름
- 기억요약
- 기타

형식은 아래와 같이 JSON으로만 출력해줘:
{{"category": "...", "content": "..."}}

문장: "{user_input}"
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=100,
        )
        import json
        data = response.choices[0].message.content.strip()
        result = json.loads(data)
        return result
    except Exception as e:
        print("❌ 기억 분류 오류:", e)
        return None
