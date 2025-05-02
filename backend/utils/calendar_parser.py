from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_schedule_from_text(text: str) -> dict | None:
    system_prompt = (
    "너는 일정 추출 도우미야. 사용자가 입력한 문장에서 일정 제목(title), 시작 시간(start_time), 종료 시간(end_time)을 추출해. \n"
    "시간은 반드시 'YYYY-MM-DDTHH:MM:SS' 형식의 ISO 8601로 작성해. \n"
    "title은 10자 이내로 간결하게 뽑아. 종료 시간은 시작 시간 기준 +1시간이야. \n"
    "절대로 설명하지 말고 아래와 같이 JSON만 출력해:\n"
    "{\"title\": \"예비군 훈련\", \"start_time\": \"2025-05-09T09:00:00\", \"end_time\": \"2025-05-09T10:00:00\"}"
)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()
    try:
        import json
        return json.loads(content)
    except:
        return None
