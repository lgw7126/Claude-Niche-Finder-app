import anthropic

def analyze_market(places: list[dict], query: str, api_key: str) -> str:
    """수집된 매장 목록을 Claude에 보내 상권 분석 텍스트를 반환한다."""
    if not places:
        raise ValueError("매장 데이터가 없습니다")

    client = anthropic.Anthropic(api_key=api_key)

    places_text = "\n".join(
        f"- {p.get('title', '알 수 없음')} | 주소: {p.get('address', '')} | 카테고리: {p.get('category', '')}"
        for p in places
    )

    prompt = f"""당신은 소상공인 창업 컨설턴트입니다.
아래는 '{query}' 상권의 경쟁 매장 목록입니다:

{places_text}

**[1단계] 주요 매장 시그니처 메뉴 추정**
위 매장 중 대표적인 곳 5~10개를 골라, 매장 이름과 카테고리를 바탕으로 시그니처 메뉴나 특징을 추정해 표로 정리해주세요.
형식: 매장명 | 추정 시그니처 메뉴/특징

**[2단계] 상권 분석**
1. 경쟁 강도: 매장 수와 분포를 보고 경쟁이 치열한지 평가 (1~2문장)
2. 포지셔닝 제안: 신규 창업자가 어떤 차별화 전략을 쓸 수 있는지 (2~3문장)
3. 최종 결론: 이 상권에 창업을 추천하는지 비추천하는지 한 줄로 명확하게
"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
