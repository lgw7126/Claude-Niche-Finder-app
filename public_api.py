import requests
import xml.etree.ElementTree as ET

PUBLIC_STORE_URL = "https://apis.data.go.kr/B553077/api/open/sdsc2/storeListInDong"

# 업종 키워드 → (indsLclsCd, indsMclsCd)
BUSINESS_KEYWORDS = {
    "카페": ("I2", "I212"),
    "커피": ("I2", "I212"),
    "베이커리": ("I2", "I210"),
    "빵집": ("I2", "I210"),
    "제과": ("I2", "I210"),
    "한식": ("I2", "I201"),
    "중식": ("I2", "I202"),
    "일식": ("I2", "I203"),
    "양식": ("I2", "I204"),
    "분식": ("I2", "I205"),
    "치킨": ("I2", "I211"),
    "피자": ("I2", "I207"),
    "식당": ("I2", None),
    "음식점": ("I2", None),
}

# 주요 동 이름 → 법정동코드 (dongCd)
DONG_CODES = {
    # 마포구
    "대흥동": "1144010900", "연남동": "1144011000", "서교동": "1144011500",
    "합정동": "1144011600", "망원동": "1144011700", "공덕동": "1144010100",
    "아현동": "1144010300", "도화동": "1144010400", "용강동": "1144010500",
    "토정동": "1144010600", "마포동": "1144010700", "창전동": "1144010800",
    "노고산동": "1144011100", "신수동": "1144011200", "현석동": "1144011300",
    "구수동": "1144011400", "상수동": "1144012000", "염리동": "1144010200",
    # 강남구
    "역삼동": "1168010100", "삼성동": "1168010200", "대치동": "1168010300",
    "압구정동": "1168010400", "청담동": "1168010600", "논현동": "1168010700",
    "신사동": "1168010800", "개포동": "1168011400", "세곡동": "1168011700",
    # 홍대
    "홍대": "1144011500",
    # 종로구
    "인사동": "1111010900", "삼청동": "1111011500", "북촌": "1111011500",
    # 용산구
    "이태원동": "1117011000", "한남동": "1117011100", "해방촌": "1117010900",
    # 성동구
    "성수동": "1204010100",
    # 서초구
    "서초동": "1165010100", "반포동": "1165010400", "방배동": "1165010600",
    # 송파구
    "잠실동": "1171010100",
    # 강서구
    "마곡동": "1150010700",
}


def _get_dong_code(query: str) -> str | None:
    for dong_name, code in DONG_CODES.items():
        if dong_name in query:
            return code
    return None


def _get_industry_params(query: str) -> dict:
    for keyword, (lcs, mcs) in BUSINESS_KEYWORDS.items():
        if keyword in query:
            params = {"indsLclsCd": lcs}
            if mcs:
                params["indsMclsCd"] = mcs
            return params
    return {}


def search_stores_public(query: str, service_key: str, num_rows: int = 100) -> list[dict]:
    """소상공인 공공데이터 API로 동 내 상가 목록을 반환한다."""
    dong_code = _get_dong_code(query)
    if not dong_code:
        return []

    params = {
        "pageNo": 1,
        "numOfRows": num_rows,
        "divId": "dongCd",
        "key": dong_code,
    }
    params.update(_get_industry_params(query))

    url = f"{PUBLIC_STORE_URL}?serviceKey={service_key}"
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    result_code = root.findtext(".//resultCode")
    if result_code != "00":
        return []

    return [
        {
            "title": item.findtext("bizesNm") or "",
            "address": item.findtext("lnnoAdres") or item.findtext("rdnmadr") or "",
            "category": item.findtext("indsNm") or "",
            "source": "공공데이터",
        }
        for item in root.findall(".//item")
        if item.findtext("bizesNm")
    ]
