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
    items = response.json().get("items", [])
    return [
        {
            "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
            "address": item.get("address", ""),
            "category": item.get("category", ""),
            "mapx": item.get("mapx", ""),
            "mapy": item.get("mapy", ""),
            "source": "네이버",
        }
        for item in items
    ]

def extract_coordinates(places: list[dict]) -> tuple[float, float] | None:
    """네이버 검색 결과에서 중심 좌표(WGS84)를 추출한다."""
    for p in places:
        mx, my = p.get("mapx", ""), p.get("mapy", "")
        if mx and my:
            lon = int(mx) / 1e7
            lat = int(my) / 1e7
            if 124 < lon < 132 and 33 < lat < 39:
                return lon, lat
    return None
