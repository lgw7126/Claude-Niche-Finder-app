# 상권 체크 리포트 — 진행 현황 인수인계 문서

## 프로젝트 개요
- **앱 이름:** 상권 체크 리포트
- **목적:** 지역명+업종 입력 → 네이버 검색 API로 경쟁 매장 수집 → Gemini AI 상권 분석 → Streamlit 대시보드 표시
- **대상:** 예비 창업자 (소수 지인 공유용, 무료)
- **작업 디렉토리:** `C:\Users\kikin\Desktop\Claude-Niche-Finder-app`

---

## 기술 스택 (전부 무료)
| 역할 | 도구 |
|------|------|
| 앱 화면 | Streamlit |
| 가게 데이터 수집 | 네이버 검색 API |
| AI 분석 | Gemini API (gemini-1.5-flash) |
| 코드 저장 | GitHub |
| 인터넷 배포 | Streamlit Community Cloud |

---

## 완료된 작업

### ✅ 설계 완료
- 설계 문서: `docs/superpowers/specs/2026-06-23-sangkwon-check-report-design.md`
- 구현 계획: `docs/superpowers/plans/2026-06-23-sangkwon-check-report.md`

### ✅ Task 1 완료: 프로젝트 기반 설정
생성된 파일:
- `requirements.txt` — 패키지 목록 (streamlit, requests, google-generativeai, pytest)
- `.gitignore` — secrets.toml 등 제외
- `.streamlit/secrets.toml` — API 키 저장 (로컬 전용, git 비포함)
- 패키지 설치 완료 (`py -m pip install -r requirements.txt` 실행됨)

### ✅ 사용자 API 키 준비 완료
- 네이버 개발자센터: Client ID + Client Secret 발급 완료 (사용자 보관 중)
- Google AI Studio: Gemini API 키 발급 완료 (사용자 보관 중)
- `.streamlit/secrets.toml`에 실제 키 아직 미입력 → **Task 4 완료 후 입력 필요**

### ✅ Python 설치 완료
- Python 3.14.6 설치됨
- 중요: `streamlit` 명령 대신 **`py -m streamlit`** 사용해야 함 (PATH 미등록)
- 마찬가지로 pytest는 **`py -m pytest`** 사용

---

## 남은 작업

### 🔲 Task 2: 네이버 검색 API 모듈 (다음 단계)
생성할 파일:
- `naver_api.py`
- `tests/__init__.py` (빈 파일)
- `tests/test_naver_api.py`

### 🔲 Task 3: Gemini AI 분석 모듈
생성할 파일:
- `gemini_api.py`
- `tests/test_gemini_api.py`

### 🔲 Task 4: Streamlit 메인 앱
생성할 파일:
- `app.py`
- Task 4 완료 후 `.streamlit/secrets.toml`에 실제 API 키 입력 필요

### 🔲 Task 5: 배포 (사용자 직접 진행)
- GitHub push → Streamlit Community Cloud 연결
- `share.streamlit.io` 접속, GitHub 로그인, New app 생성

---

## 구현 계획 전체 내용 (새 대화에서 참고용)

### Task 2 상세

**`tests/test_naver_api.py`:**
```python
import pytest
from unittest.mock import patch, MagicMock
from naver_api import search_places

def test_search_places_returns_list():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {"title": "스타벅스 연남점", "address": "서울시 마포구", "category": "카페"},
            {"title": "블루보틀 연남", "address": "서울시 마포구", "category": "카페"},
        ]
    }
    with patch("naver_api.requests.get", return_value=mock_response):
        result = search_places("연남동 카페", client_id="test_id", client_secret="test_secret")
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["title"] == "스타벅스 연남점"

def test_search_places_empty_result():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": []}
    with patch("naver_api.requests.get", return_value=mock_response):
        result = search_places("없는동네 우주음식점", client_id="test_id", client_secret="test_secret")
    assert result == []

def test_search_places_api_error():
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = Exception("Unauthorized")
    with patch("naver_api.requests.get", return_value=mock_response):
        with pytest.raises(Exception):
            search_places("연남동 카페", client_id="bad_id", client_secret="bad_secret")
```

**`naver_api.py`:**
```python
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
```

테스트 실행: `py -m pytest tests/test_naver_api.py -v`
커밋: `git add naver_api.py tests/ && git commit -m "feat: add Naver search API module"`

---

### Task 3 상세

**`tests/test_gemini_api.py`:**
```python
import pytest
from unittest.mock import patch, MagicMock
from gemini_api import analyze_market

SAMPLE_PLACES = [
    {"title": "스타벅스 연남점", "address": "서울시 마포구 연남동", "category": "카페"},
    {"title": "블루보틀 연남", "address": "서울시 마포구 연남동", "category": "카페"},
    {"title": "이디야 연남점", "address": "서울시 마포구 연남동", "category": "카페"},
]

def test_analyze_market_returns_string():
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "경쟁 강도 높음. 프리미엄 포지셔닝 추천."
    mock_model.generate_content.return_value = mock_response
    with patch("gemini_api.genai.GenerativeModel", return_value=mock_model):
        with patch("gemini_api.genai.configure"):
            result = analyze_market(SAMPLE_PLACES, query="연남동 카페", api_key="test_key")
    assert isinstance(result, str)
    assert len(result) > 0

def test_analyze_market_empty_places():
    with pytest.raises(ValueError, match="매장 데이터가 없습니다"):
        analyze_market([], query="연남동 카페", api_key="test_key")
```

**`gemini_api.py`:**
```python
import google.generativeai as genai

def analyze_market(places: list[dict], query: str, api_key: str) -> str:
    """수집된 매장 목록을 Gemini에 보내 상권 분석 텍스트를 반환한다."""
    if not places:
        raise ValueError("매장 데이터가 없습니다")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

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

    response = model.generate_content(prompt)
    return response.text
```

테스트 실행: `py -m pytest tests/test_gemini_api.py -v`
커밋: `git add gemini_api.py tests/test_gemini_api.py && git commit -m "feat: add Gemini AI analysis module"`

---

### Task 4 상세

**`app.py`:**
```python
import streamlit as st
from naver_api import search_places
from gemini_api import analyze_market

st.set_page_config(page_title="상권 체크 리포트", page_icon="🏪", layout="wide")
st.title("🏪 상권 체크 리포트")
st.caption("지역명과 업종을 입력하면 AI가 상권을 분석해드립니다.")

query = st.text_input(
    label="분석할 상권과 업종을 입력하세요",
    placeholder="예: 연남동 카페, 한남동 베이커리, 홍대 디저트",
)

if st.button("리포트 생성하기", type="primary", disabled=not query):
    try:
        naver_client_id = st.secrets["NAVER_CLIENT_ID"]
        naver_client_secret = st.secrets["NAVER_CLIENT_SECRET"]
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError as e:
        st.error(f"API 키 설정 오류: {e} 키가 secrets.toml에 없습니다.")
        st.stop()

    with st.spinner("📊 상권 데이터를 분석 중입니다... (약 10~30초 소요)"):
        try:
            places = search_places(query, naver_client_id, naver_client_secret)
        except Exception as e:
            st.error(f"네이버 API 오류: {e}")
            st.stop()

        if not places:
            st.warning("해당 지역/업종의 매장을 찾을 수 없습니다. 검색어를 바꿔 시도해보세요.")
            st.stop()

        try:
            analysis = analyze_market(places, query=query, api_key=gemini_api_key)
        except Exception as e:
            st.error(f"AI 분석 오류: {e}")
            st.stop()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("분석된 경쟁 매장 수", f"{len(places)}개")
    with col2:
        categories = [p.get("category", "") for p in places if p.get("category")]
        top_category = max(set(categories), key=categories.count) if categories else "알 수 없음"
        st.metric("주요 업종", top_category)

    st.subheader("📋 경쟁 매장 목록")
    table_data = [
        {
            "상호명": p.get("title", "").replace("<b>", "").replace("</b>", ""),
            "주소": p.get("address", ""),
            "카테고리": p.get("category", ""),
        }
        for p in places
    ]
    st.dataframe(table_data, use_container_width=True)

    st.subheader("🤖 AI 상권 분석 리포트")
    st.info(analysis)
```

로컬 테스트: `py -m streamlit run app.py`
커밋: `git add app.py && git commit -m "feat: add Streamlit main app"`

---

## 새 대화 시작 시 전달할 메시지 (복사해서 붙여넣기)

> HANDOFF.md 파일을 읽고 상권 체크 리포트 프로젝트를 이어서 진행해줘. Task 2부터 시작해. 사용자는 비개발자 왕초보이고 한국어로 소통해. 설명은 쉽게, 사용자 액션이 필요하면 단계별로 한 번에 설명해.

---

## 주요 주의사항
- pytest/streamlit 실행 시 `py -m pytest`, `py -m streamlit run app.py` 사용 (streamlit 단독 명령 안 됨)
- `.streamlit/secrets.toml`은 절대 git에 올리지 않는다
- secrets.toml에 실제 API 키 입력은 app.py 완성 후 진행
