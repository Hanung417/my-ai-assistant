from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

# FastAPI router 객체 정의
router = APIRouter()

# 환경 변수에서 API 키 로드
load_dotenv()  # .env 파일에서 환경 변수 로드
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # 환경 변수에서 OpenAI API 키 가져오기

class ChatRequest(BaseModel):
    message: str
    system_prompt: str = "당신은 친근한 AI 비서입니다."  # 기본값 설정

@router.post("/chat")
def generate_gpt_response(chat_request: ChatRequest) -> dict:
    try:
        # 전달된 system_prompt 확인
        print("시스템 프롬프트:", chat_request.system_prompt)

        # GPT 모델을 사용하여 응답 생성 (openai.ChatCompletion.create 사용)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 사용할 GPT 모델
            messages=[
                {"role": "system", "content": chat_request.system_prompt},  # 시스템 메시지
                {"role": "user", "content": chat_request.message},  # 사용자 메시지
            ],
        temperature=0.8,
        max_tokens=500,
        )

        # 응답에서 GPT의 답변 추출
        gpt_answer = response.choices[0].message.content
        print("GPT 응답:", gpt_answer)

        return {"answer": gpt_answer}  # JSON 객체로 응답 반환

    except Exception as e:
        print("GPT 오류:", e)
        return {"answer": "Sorry, something went wrong. Please try again."}  # 오류 발생 시 JSON 응답
