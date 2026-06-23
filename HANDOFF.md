# 상권 체크 리포트 — 진행 현황 인수인계 문서

## 프로젝트 개요
- **앱 이름:** 상권 체크 리포트
- **목적:** 지역명+업종 입력 → 소상공인 공공데이터 + 네이버 API로 경쟁 매장 수집 → Gemini AI 상권 분석 → Streamlit 대시보드 표시
- **작업 디렉토리:** `C:\Users\kikin\Desktop\Claude-Niche-Finder-app`

---

## 기술 스택
| 역할 | 도구 |
|------|------|
| 앱 화면 | Streamlit |
| 매장 데이터 1 (주력) | 소상공인시장진흥공단 상가(상권)정보 API (data.go.kr) |
| 매장 데이터 2 (보조) | 네이버 검색 API |
| AI 분석 | Gemini API (gemini-2.5-flash) |
| 코드 저장 | GitHub |
| 인터넷 배포 | Streamlit Community Cloud |

---

## API 키 현황 (.streamlit/secrets.toml에 저장됨)
- `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` — 네이버 개발자센터
- `GEMINI_API_KEY` — Google AI Studio
- `PUBLIC_DATA_API_KEY` — data.go.kr 일반 인증키 (소상공인 API 활용신청 승인 완료)

---

## 완료된 작업

### ✅ Task 1: 프로젝트 기반 설정
### ✅ Task 2: 네이버 검색 API 모듈 (`naver_api.py`)
### ✅ Task 3: Gemini AI 분석 모듈 (`gemini_api.py`) — gemini-2.5-flash 사용
### ✅ Task 4: Streamlit 메인 앱 (`app.py`)
### ✅ 소상공인 공공데이터 API 추가 (`public_api.py`)

---

## 현재 파일 구조
```
app.py              — Streamlit 메인 앱
naver_api.py        — 네이버 지역검색 API (보조)
public_api.py       — 소상공인 공공데이터 API (주력, 동 코드 기반)
gemini_api.py       — Gemini AI 분석
requirements.txt    — 패키지 목록
.streamlit/secrets.toml — API 키 (git 비포함)
tests/              — 테스트 파일
```

---

## 남은 문제 (다음 세션에서 해결 필요)

### 🔲 공공데이터 API 연동 마무리
**증상:** `search_stores_public()` 함수는 완성됐으나 서버 캐시 문제로 앱에서 아직 0개 반환 중

**해결책:** 서버 재시작 후 테스트 필요
```
py -m streamlit run app.py --server.headless true
```

**public_api.py 핵심 로직:**
- 엔드포인트: `storeListInDong` (동 코드 기반)
- `divId=dongCd`, `key=법정동코드(10자리)`
- 업종코드: 카페=I2/I212, 한식=I2/I201, 베이커리=I2/I210 등
- `DONG_CODES` 딕셔너리에 주요 동 이름→코드 매핑 내장

**테스트 확인됨:** `py debug_api.py` 로 마포구 대흥동 카페 100개 정상 반환 확인

### 🔲 Task 5: 배포
- GitHub push → Streamlit Community Cloud 연결
- `share.streamlit.io` 접속, GitHub 로그인, New app 생성
- 배포 시 secrets.toml 내용을 Streamlit Cloud 환경변수로 입력 필요

---

## 주요 주의사항
- pytest/streamlit 실행: `py -m pytest`, `py -m streamlit run app.py`
- `.streamlit/secrets.toml`은 절대 git에 올리지 않는다
- 공공데이터 API는 serviceKey를 URL에 직접 삽입해야 함 (requests params로 넘기면 이중인코딩 오류)
- Gemini 모델: `gemini-2.5-flash` (gemini-1.5-flash는 새 SDK에서 미지원)

---

## 새 대화 시작 시 전달할 메시지

> HANDOFF.md 파일을 읽고 상권 체크 리포트 프로젝트를 이어서 진행해줘. 공공데이터 API 연동 마무리부터 시작해. 사용자는 비개발자 왕초보이고 한국어로 소통해. 설명은 쉽게, 사용자 액션이 필요하면 단계별로 한 번에 설명해.
