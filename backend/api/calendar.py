from fastapi import APIRouter, Request, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime
import pytz
import os

router = APIRouter()

SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRETS_FILE = "client_secret.json"
REDIRECT_URI = "http://localhost:8000/api/calendar/callback"

flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI
)

@router.get("/calendar/auth")
def auth():
    auth_url, _ = flow.authorization_url(prompt='consent')
    return RedirectResponse(auth_url)

@router.get("/calendar/callback")
def callback(request: Request):
    code = request.query_params['code']
    flow.fetch_token(code=code)
    credentials = flow.credentials
    with open("token.json", "w") as token:
        token.write(credentials.to_json())
    return {"message": "Google Calendar 연결 완료!"}

class CalendarEvent(BaseModel):
    title: str
    start_time: str  # ISO 8601
    end_time: str    # ISO 8601

@router.post("/calendar/add")
def add_event(event: CalendarEvent):
    try:
        if not os.path.exists("token.json"):
            return {"error": "인증된 사용자가 없습니다. 먼저 /calendar/auth 를 통해 로그인하세요."}

        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        service = build("calendar", "v3", credentials=creds)

        timezone = pytz.timezone("Asia/Seoul")
        start = timezone.localize(datetime.fromisoformat(event.start_time)).isoformat()
        end = timezone.localize(datetime.fromisoformat(event.end_time)).isoformat()

        body = {
            "summary": event.title,
            "start": {"dateTime": start, "timeZone": "Asia/Seoul"},
            "end": {"dateTime": end, "timeZone": "Asia/Seoul"},
        }

        print("[캘린더 등록 시도] ▶", body)
        result = service.events().insert(calendarId='primary', body=body).execute()
        print("[캘린더 응답] ▶", result)

        return {"message": f"일정 '{event.title}'이(가) 추가되었습니다!"}

    except Exception as e:
        print("❌ 캘린더 등록 오류:", e)
        return {"error": str(e)}

@router.get("/calendar/search")
def search_event(query: str = Query(...)):
    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        service = build("calendar", "v3", credentials=creds)

        now = datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime',
            q=query
        ).execute()

        events = events_result.get('items', [])
        if not events:
            return {"message": "일정이 없습니다.", "events": []}

        return {"message": "일정 검색 결과:", "events": events}

    except Exception as e:
        print("❌ 일정 검색 오류:", e)
        return {"error": str(e)}

@router.delete("/calendar/delete")
def delete_event(event_id: str):
    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        service = build("calendar", "v3", credentials=creds)

        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return {"message": f"일정이 삭제되었습니다."}

    except Exception as e:
        print("❌ 일정 삭제 오류:", e)
        return {"error": str(e)}

@router.put("/calendar/update")
def update_event(event_id: str, event: CalendarEvent):
    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        service = build("calendar", "v3", credentials=creds)

        timezone = pytz.timezone("Asia/Seoul")
        start = timezone.localize(datetime.fromisoformat(event.start_time)).isoformat()
        end = timezone.localize(datetime.fromisoformat(event.end_time)).isoformat()

        body = {
            "summary": event.title,
            "start": {"dateTime": start, "timeZone": "Asia/Seoul"},
            "end": {"dateTime": end, "timeZone": "Asia/Seoul"},
        }

        service.events().update(calendarId='primary', eventId=event_id, body=body).execute()
        return {"message": f"일정이 수정되었습니다."}

    except Exception as e:
        print("❌ 일정 수정 오류:", e)
        return {"error": str(e)}

@router.get("/calendar/range")
def list_events_range(start: str, end: str):
    if not os.path.exists("token.json"):
        return {"error": "인증된 사용자가 없습니다."}

    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("calendar", "v3", credentials=creds)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    formatted = []
    for e in events:
        start = e['start'].get('dateTime', e['start'].get('date'))
        title = e.get('summary', '제목 없음')
        formatted.append(f"{start} - {title}")
    return {"events": formatted}