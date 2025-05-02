from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_keywords_with_gpt(user_input: str, max_keywords: int = 5):
    prompt = f"""
다음 문장에서 핵심 키워드를 {max_keywords}개 이내로 추출해줘. 명사 중심으로, 쉼표로 구분해서 줘.
문장: "{user_input}"
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=50,
        )
        keywords_raw = response.choices[0].message.content.strip()
        keywords = [kw.strip() for kw in keywords_raw.split(",") if kw.strip()]
        return keywords
    except Exception as e:
        print("키워드 추출 오류:", e)
        return []