import requests

KAKAO_LOCAL_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"


def search_places_kakao(query: str, api_key: str, max_results: int = 45) -> list[dict]:
    """카카오 로컬 검색 API로 매장 목록을 반환한다. 최대 45개."""
    headers = {"Authorization": f"KakaoAK {api_key}"}
    results = []

    for page in range(1, 4):  # 페이지당 15개 × 3페이지 = 최대 45개
        params = {"query": query, "size": 15, "page": page}
        response = requests.get(KAKAO_LOCAL_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        documents = data.get("documents", [])
        if not documents:
            break
        for doc in documents:
            results.append({
                "title": doc.get("place_name", ""),
                "address": doc.get("address_name", ""),
                "category": doc.get("category_name", ""),
                "source": "카카오",
            })
        if data.get("meta", {}).get("is_end"):
            break

    return results
