import requests

NAVER_SEARCH_URL = "https://openapi.naver.com/v1/search/local.json"

def search_places(query: str, client_id: str, client_secret: str, display: int = 15) -> list[dict]:
    """네이버 지역 검색 API로 매장 목록을 반환한다."""
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    params = {"query": query, "display": display, "sort": "comment"}
    response = requests.get(NAVER_SEARCH_URL, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("items", [])
