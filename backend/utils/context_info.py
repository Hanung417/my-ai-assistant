import requests
import os
from datetime import datetime, timedelta
import math
from dotenv import load_dotenv

load_dotenv()

# 1. 현재 시간 정보
def get_current_time_info():
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "weekday": now.strftime("%A")
    }

# 2. 사용자 위치 추정 (IP 기반)
def get_user_location():
    try:
        res = requests.get("http://ip-api.com/json")
        data = res.json()
        return {
            "city": data.get("city", "Seoul"),
            "lat": float(data["lat"]),
            "lon": float(data["lon"])
        }
    except Exception as e:
        print("위치 정보 조회 실패:", e)
        return {
            "city": "Seoul",
            "lat": 37.5665,
            "lon": 126.9780
        }

# 3. 위경도 → 기상청 격자(nx, ny)
def latlon_to_xy(lat, lon):
    RE = 6371.00877
    GRID = 5.0
    SLAT1 = 30.0
    SLAT2 = 60.0
    OLON = 126.0
    OLAT = 38.0
    XO = 43
    YO = 136
    DEGRAD = math.pi / 180.0

    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = (sf ** sn * math.cos(slat1)) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / (ro ** sn)

    ra = math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / (ra ** sn)
    theta = lon * DEGRAD - olon
    if theta > math.pi: theta -= 2.0 * math.pi
    if theta < -math.pi: theta += 2.0 * math.pi
    theta *= sn

    x = int(ra * math.sin(theta) + XO + 0.5)
    y = int(ro - ra * math.cos(theta) + YO + 0.5)

    return x, y

# 4. 기상청 날씨 정보 조회
def get_kma_weather(nx: int, ny: int):
    service_key = os.getenv("KMA_API_KEY")
    if not service_key:
        return {"error": "기상청 API 키가 설정되어 있지 않습니다."}

    now = datetime.now()
    base_date = now.strftime("%Y%m%d")
    base_time = (now - timedelta(hours=1)).strftime("%H") + "00"

    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        "serviceKey": service_key,
        "pageNo": "1",
        "numOfRows": "1000",
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        items = data['response']['body']['items']['item']
        result = {}
        for item in items:
            if item['fcstTime'] != base_time:
                continue
            category = item['category']
            value = item['fcstValue']
            if category == "TMP":
                result["temperature"] = value + "°C"
            elif category == "SKY":
                result["sky"] = {"1": "맑음", "3": "구름 많음", "4": "흐림"}.get(value, "정보 없음")
            elif category == "POP":
                result["rain_prob"] = value + "%"
            elif category == "REH":
                result["humidity"] = value + "%"
        return result if result else {"error": "예보 데이터 없음"}
    except Exception as e:
        return {"error": str(e)}

# ✅ 최종 통합: GPT system prompt용 context 반환
def get_context_data():
    time_info = get_current_time_info()
    location = get_user_location()
    nx, ny = latlon_to_xy(location["lat"], location["lon"])
    weather = get_kma_weather(nx, ny)

    return {
        "time": time_info,
        "location": location,
        "weather": weather,
        "nx": nx,
        "ny": ny
    }

