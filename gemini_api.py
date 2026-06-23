from google import genai

def analyze_market(places: list[dict], query: str, api_key: str) -> str:
    """수집된 매장 목록을 Gemini에 보내 상권 분석 텍스트를 반환한다."""
    if not places:
        raise ValueError("매장 데이터가 없습니다")

    client = genai.Client(api_key=api_key)

    places_text = "\n".join(
        f"- {p.get('title', '알 수 없음')} | 주소: {p.get('address', '')} | 카테고리: {p.get('category', '')}"
        for p in places
    )

    prompt = f"""당신은 소상공인 창업 컨설턴트입니다.
아래는 '{query}' 상권의 경쟁 매장 목록입니다:

{places_text}

다음 3가지를 간결하게 한국어로 분석해주세요:
1. 경쟁 강도: 매장 수와 분포를 보고 경쟁이 치열한지 평가 (1~2문장)
2. 포지셔닝 제안: 신규 창업자가 어떤 차별화 전략을 쓸 수 있는지 (2~3문장)
3. 최종 결론: 이 상권에 창업을 추천하는지 비추천하는지 한 줄로 명확하게
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text
