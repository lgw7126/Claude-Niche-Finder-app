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

# 구 이름 → signguCd (시군구코드 5자리)
GU_CODES = {
    "종로구": "11110",
    "중구": "11140",
    "용산구": "11170",
    "성동구": "11200",
    "광진구": "11215",
    "동대문구": "11230",
    "중랑구": "11260",
    "성북구": "11290",
    "강북구": "11305",
    "도봉구": "11320",
    "노원구": "11350",
    "은평구": "11380",
    "서대문구": "11410",
    "마포구": "11440",
    "양천구": "11470",
    "강서구": "11500",
    "구로구": "11530",
    "금천구": "11545",
    "영등포구": "11560",
    "동작구": "11590",
    "관악구": "11620",
    "서초구": "11650",
    "강남구": "11680",
    "송파구": "11710",
    "강동구": "11740",
}

# 동 이름 → 법정동코드 (10자리)
DONG_CODES = {
    "대흥동": "1144010900", "연남동": "1144011000", "서교동": "1144011500",
    "합정동": "1144011600", "망원동": "1144011700", "공덕동": "1144010100",
    "아현동": "1144010300", "도화동": "1144010400", "용강동": "1144010500",
    "상수동": "1144012000", "염리동": "1144010200", "신수동": "1144011200",
    "역삼동": "1168010100", "삼성동": "1168010200", "대치동": "1168010300",
    "압구정동": "1168010400", "청담동": "1168010600", "논현동": "1168010700",
    "신사동": "1168010800", "개포동": "1168011400",
    "인사동": "1111013600", "삼청동": "1111015300",
    "이태원동": "1117011000", "한남동": "1117011100",
    "성수동": "1204010100",
    "서초동": "1165010100", "반포동": "1165010400", "방배동": "1165010600",
    "잠실동": "1171010100", "마곡동": "1150010700",
}

# 동 이름 → 동이 속한 구 이름 (필터링에 사용)
DONG_TO_GU = {
    # 마포구
    "대흥동": "마포구", "연남동": "마포구", "서교동": "마포구",
    "합정동": "마포구", "망원동": "마포구", "공덕동": "마포구",
    "아현동": "마포구", "도화동": "마포구", "용강동": "마포구",
    "상수동": "마포구", "염리동": "마포구", "신수동": "마포구",
    "홍대": "마포구",
    # 강남구
    "역삼동": "강남구", "삼성동": "강남구", "대치동": "강남구",
    "압구정동": "강남구", "청담동": "강남구", "논현동": "강남구",
    "신사동": "강남구", "개포동": "강남구",
    # 종로구
    "인사동": "종로구", "삼청동": "종로구", "북촌": "종로구",
    # 용산구
    "이태원동": "용산구", "한남동": "용산구", "해방촌": "용산구",
    # 성동구
    "성수동": "성동구",
    # 서초구
    "서초동": "서초구", "반포동": "서초구", "방배동": "서초구",
    # 송파구
    "잠실동": "송파구",
    # 강서구
    "마곡동": "강서구",
}


def _find_gu(query: str):
    """쿼리에서 구 이름과 코드를 찾는다."""
    for gu_name, code in GU_CODES.items():
        if gu_name in query:
            return gu_name, code
    # 동 이름으로 구를 추론
    for dong_name, gu_name in DONG_TO_GU.items():
        if dong_name in query:
            return gu_name, GU_CODES[gu_name]
    return None, None


def _find_dong(query: str):
    """쿼리에서 동 이름을 찾는다."""
    for dong_name in DONG_TO_GU:
        if dong_name in query:
            return dong_name
    return None


def _get_industry_params(query: str) -> dict:
    for keyword, (lcs, mcs) in BUSINESS_KEYWORDS.items():
        if keyword in query:
            params = {"indsLclsCd": lcs}
            if mcs:
                params["indsMclsCd"] = mcs
            return params
    return {}


def search_stores_public(query: str, service_key: str, num_rows: int = 1000) -> list[dict]:
    """소상공인 공공데이터 API로 구 내 상가 목록을 반환한다."""
    gu_name, gu_code = _find_gu(query)
    if not gu_code:
        return []

    dong_name = _find_dong(query)

    # 동 코드가 있으면 동 단위로 직접 조회, 없으면 구 단위
    if dong_name and dong_name in DONG_CODES:
        div_id = "ldongCd"
        div_key = DONG_CODES[dong_name]
        filter_gu = gu_name
        filter_dong = None  # API가 동 단위로 가져오므로 추가 필터 불필요
    else:
        div_id = "signguCd"
        div_key = gu_code
        filter_gu = gu_name
        filter_dong = dong_name

    params = {
        "pageNo": 1,
        "numOfRows": num_rows,
        "divId": div_id,
        "key": div_key,
    }
    params.update(_get_industry_params(query))

    url = f"{PUBLIC_STORE_URL}?serviceKey={service_key}"
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    result_code = root.findtext(".//resultCode")
    if result_code != "00":
        return []

    results = []
    for item in root.findall(".//item"):
        name = item.findtext("bizesNm") or ""
        if not name:
            continue

        item_gu = item.findtext("signguNm") or ""
        item_dong = item.findtext("ldongNm") or ""

        if filter_gu and filter_gu not in item_gu:
            continue
        if filter_dong and filter_dong not in item_dong:
            continue

        address = item.findtext("lnoAdr") or item.findtext("rdnmAdr") or ""
        results.append({
            "title": name,
            "address": address,
            "category": item.findtext("indsSclsNm") or item.findtext("indsNm") or "",
            "source": "공공데이터",
        })

    return results
