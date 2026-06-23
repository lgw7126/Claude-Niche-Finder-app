# 상권 체크 리포트 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 지역명 + 업종을 입력하면 네이버 검색 API로 경쟁 매장 데이터를 수집하고 Gemini AI가 포지셔닝 분석 코멘트를 생성하는 Streamlit 대시보드 앱을 만든다.

**Architecture:** Streamlit 단일 페이지 앱. naver_api.py가 네이버 검색 API를 호출해 매장 목록을 반환하고, gemini_api.py가 해당 목록을 Gemini에 보내 분석 텍스트를 생성한다. app.py가 이 두 모듈을 조합해 화면을 렌더링한다. 데이터는 저장하지 않고 매번 새로 분석한다.

**Tech Stack:** Python 3.11+, Streamlit, requests, google-generativeai, pytest

---

## File Structure

```
Claude-Niche-Finder-app/
├── app.py                          # Streamlit 메인 앱 (UI + 흐름 조율)
├── naver_api.py                    # 네이버 검색 API 호출
├── gemini_api.py                   # Gemini AI 분석 호출
├── requirements.txt                # 패키지 의존성
├── .gitignore                      # secrets.toml 등 제외
├── .streamlit/
│   └── secrets.toml                # API 키 저장 (gitignore됨)
└── tests/
    ├── test_naver_api.py
    └── test_gemini_api.py
```

---

### Task 1: 프로젝트 기반 설정

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `.streamlit/secrets.toml`

- [ ] **Step 1: requirements.txt 작성**

```
streamlit>=1.35.0
requests>=2.31.0
google-generativeai>=0.7.0
pytest>=8.0.0
```

- [ ] **Step 2: .gitignore 작성**

```
.streamlit/secrets.toml
__pycache__/
.pytest_cache/
*.pyc
```

- [ ] **Step 3: .streamlit/secrets.toml 작성 (API 키 템플릿)**

아래 내용에서 각 값을 실제 발급받은 키로 교체한다:

```toml
NAVER_CLIENT_ID = "여기에_네이버_Client_ID_입력"
NAVER_CLIENT_SECRET = "여기에_네이버_Client_Secret_입력"
GEMINI_API_KEY = "여기에_Gemini_API_키_입력"
```

- [ ] **Step 4: 패키지 설치 확인**

Run: `pip install -r requirements.txt`
Expected: 에러 없이 설치 완료

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .gitignore
git commit -m "feat: project setup with dependencies"
```

(secrets.toml은 .gitignore에 의해 자동 제외됨 — 절대 커밋하지 않는다)

---

### Task 2: 네이버 검색 API 모듈

**Files:**
- Create: `naver_api.py`
- Create: `tests/test_naver_api.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_naver_api.py`:

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

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `pytest tests/test_naver_api.py -v`
Expected: `ImportError: No module named 'naver_api'`

- [ ] **Step 3: naver_api.py 구현**

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

- [ ] **Step 4: 테스트 통과 확인**

Run: `pytest tests/test_naver_api.py -v`
Expected: 3개 테스트 모두 PASS

- [ ] **Step 5: Commit**

```bash
git add naver_api.py tests/test_naver_api.py
git commit -m "feat: add Naver search API module"
```

---

### Task 3: Gemini AI 분석 모듈

**Files:**
- Create: `gemini_api.py`
- Create: `tests/test_gemini_api.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_gemini_api.py`:

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

- [ ] **Step 2: 테스트 실행해서 실패 확인**

Run: `pytest tests/test_gemini_api.py -v`
Expected: `ImportError: No module named 'gemini_api'`

- [ ] **Step 3: gemini_api.py 구현**

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

- [ ] **Step 4: 테스트 통과 확인**

Run: `pytest tests/test_gemini_api.py -v`
Expected: 2개 테스트 모두 PASS

- [ ] **Step 5: Commit**

```bash
git add gemini_api.py tests/test_gemini_api.py
git commit -m "feat: add Gemini AI analysis module"
```

---

### Task 4: Streamlit 메인 앱

**Files:**
- Create: `app.py`

- [ ] **Step 1: app.py 작성**

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

    # 요약 카드
    col1, col2 = st.columns(2)
    with col1:
        st.metric("분석된 경쟁 매장 수", f"{len(places)}개")
    with col2:
        categories = [p.get("category", "") for p in places if p.get("category")]
        top_category = max(set(categories), key=categories.count) if categories else "알 수 없음"
        st.metric("주요 업종", top_category)

    # 경쟁 매장 표
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

    # AI 분석
    st.subheader("🤖 AI 상권 분석 리포트")
    st.info(analysis)
```

- [ ] **Step 2: 로컬에서 앱 실행 테스트**

Run: `streamlit run app.py`
Expected: 브라우저에서 `http://localhost:8501` 자동 오픈. 검색창과 버튼이 보임.

"연남동 카페" 입력 후 "리포트 생성하기" 클릭 → 스피너 후 매장 표와 AI 분석 텍스트가 표시되면 성공.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add Streamlit main app"
```

---

### Task 5: GitHub Push 및 Streamlit Cloud 배포

**Files:**
- 변경 없음 (배포 설정만)

- [ ] **Step 1: GitHub에 전체 코드 Push**

```bash
git push origin main
```

Expected: GitHub 저장소에 모든 파일이 올라감 (.streamlit/secrets.toml 제외 확인)

- [ ] **Step 2: Streamlit Community Cloud 배포**

1. 브라우저에서 `share.streamlit.io` 접속
2. **"Sign in with GitHub"** 클릭 → GitHub 계정 로그인
3. **"New app"** 버튼 클릭
4. **Repository:** `Claude-Niche-Finder-app` 선택
5. **Branch:** `main`
6. **Main file path:** `app.py`
7. **"Advanced settings"** 클릭 → **"Secrets"** 탭에서 아래 내용 입력:

```toml
NAVER_CLIENT_ID = "여기에_실제_Client_ID"
NAVER_CLIENT_SECRET = "여기에_실제_Client_Secret"
GEMINI_API_KEY = "여기에_실제_Gemini_API_키"
```

8. **"Deploy!"** 클릭
9. 약 2~3분 후 `https://[앱이름].streamlit.app` 형태의 URL 생성됨

- [ ] **Step 3: 배포된 앱 동작 확인**

생성된 URL 접속 → "연남동 카페" 검색 → 결과 정상 표시 확인

---

## 전체 테스트 실행

```bash
pytest tests/ -v
```

Expected:
```
tests/test_naver_api.py::test_search_places_returns_list PASSED
tests/test_naver_api.py::test_search_places_empty_result PASSED
tests/test_naver_api.py::test_search_places_api_error PASSED
tests/test_gemini_api.py::test_analyze_market_returns_string PASSED
tests/test_gemini_api.py::test_analyze_market_empty_places PASSED
5 passed
```
