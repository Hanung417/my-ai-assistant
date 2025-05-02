<div align="center">
  <h1>🤖 내 전용 AI 비서 만들기</h1>
  <p>React + Node.js 기반의 나만의 AI 비서 프로젝트</p>
  <img src="https://img.shields.io/badge/Status-In%20Progress-yellow.svg" alt="status" />
</div>

---

## 🧩 프로젝트 개요

‘내 전용 AI 비서 만들기’는 사용자의 일상과 업무를 도와주는 **개인화 AI Assistant**입니다.  
일정, 메모, 대화, 파일 검색 등 다양한 기능을 기억 기반으로 수행하며,  
**직접 생성한 캐릭터 UI**와 함께 친근한 사용자 경험을 제공합니다.

---

## 🛠️ 사용 기술

| 영역         | 기술 스택 |
|--------------|-----------|
| 프론트엔드   | `React`, `Three.js`, `TailwindCSS` |
| 백엔드       | `Node.js`, `Express`, `JWT`, `PostgreSQL`, `SQLite (초기)` |
| AI 기능      | `Stable Diffusion`, `LangChain`, `Vector DB (예정)` |
| API 연동     | `Google Calendar API`, `OpenWeather`, `News API (예정)` |
| 로컬 AI 실행 | `hakurei/waifu-diffusion`, `AUTOMATIC1111 UI` |
| 기타         | `dotenv`, `axios`, `nodemon` 등 |

---

## 📌 주요 기능

- 📅 **일정 관리**  
  └ Google Calendar 연동 및 자연어 질의 응답 기능

- 🧠 **Long-term Memory 기반 대화**  
  └ 이전 대화를 요약하여 기억하고 활용

- 💬 **캐릭터 UI 챗봇**  
  └ Sora 기반 2D 캐릭터와의 인터랙션

- 📝 **파일 및 메모 요약 / 검색 기능**

- 🌤️ **날씨 / 뉴스 확인 기능 (예정)**

---

## 🚧 진행 상황

- [x] Stable Diffusion 모델 선정 (`waifu-diffusion`)
- [x] JWT 기반 로그인 구현 (SQLite → PostgreSQL 전환 중)
- [x] Sora 스타일 캐릭터 생성 구조 설정
- [ ] Long-term Memory 자동 저장/요약 기능 개발
- [ ] Google Calendar 연동
- [ ] 프론트 UI 개발 (React + Three.js)
- [ ] 기억 기반 응답 로직 연결

---

## 📁 폴더 구조 (예시)

