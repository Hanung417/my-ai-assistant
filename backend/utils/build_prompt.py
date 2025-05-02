from utils.context_info import get_current_time_info, get_kma_weather
from typing import List, Optional
from models.memory import UserMemory

def build_system_prompt(
    base_prompt: str,
    long_memory: Optional[UserMemory] = None,
    related_memories: Optional[List[UserMemory]] = None,
    nx: int = 60,
    ny: int = 127
) -> str:
    # 1. 시간 및 날씨 정보
    time_info = get_current_time_info()
    weather_info = get_kma_weather(nx=nx, ny=ny)

    time_weather_context = f"""
[🕒 현재 시간 및 날씨 정보]
오늘은 {time_info['date']} ({time_info['weekday']})이며, 현재 시각은 {time_info['time']}입니다.
현재 날씨는 {weather_info.get('sky', '정보 없음')}, 기온은 {weather_info.get('temperature', '')},
강수확률은 {weather_info.get('rain_prob', '')}, 습도는 {weather_info.get('humidity', '')}입니다.
"""

    # 2. 장기 기억
    long_memory_text = long_memory.content if long_memory else "없음"

    # 3. 관련 기억
    rag_context = "\n".join({m.content for m in related_memories}) if related_memories else "없음"

    # 4. 최종 프롬프트 조합
    full_prompt = f"""{base_prompt}

{time_weather_context.strip()}

[📌 장기 기억 요약]
{long_memory_text}

[📎 관련 기억]
{rag_context}
"""
    return full_prompt.strip()
