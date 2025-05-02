from crud.memory import get_all_user_memory

def search_memory_answer(db, user_id: str, user_input: str) -> str | None:
    keywords = ["취향", "좋아", "싫어", "성향", "기억", "내가 뭐"]
    if not any(kw in user_input for kw in keywords):
        return None

    memories = get_all_user_memory(db, user_id)
    memory_texts = "\n".join([f"- [{m.category}] {m.content}" for m in memories if m.category != "대화요약"])

    if not memory_texts.strip():
        return "아직 저장된 기억이 없어요."

    return f"당신에 대해 기억하고 있는 내용이에요:\n{memory_texts}"