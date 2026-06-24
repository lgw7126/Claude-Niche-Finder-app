# 🏪 상권 체크 리포트

> **▶ 앱 바로 실행:** https://claude-niche-finder-app-bdo9keb8kmsbw6tg6cqfnw.streamlit.app

> **로컬 실행:** 터미널에서 아래 명령어 실행 후 http://localhost:8501 접속
> ```
> cd Desktop\Claude-Niche-Finder-app
> py -m streamlit run app.py
> ```

---

## 기획 의도

창업을 준비하는 소상공인이 특정 지역의 상권을 쉽고 빠르게 파악할 수 있도록 만든 AI 상권 분석 도구입니다.

- 지역명과 업종만 입력하면 경쟁 매장 현황을 자동 수집
- 카카오맵·네이버·공공데이터 3개 소스를 동시에 활용해 더 정확한 결과 제공
- Claude AI가 경쟁 강도, 차별화 전략, 창업 추천 여부를 분석해 리포트로 제공

---

## 사용 방법

1. 입력창에 **"지역명 + 업종"** 형태로 입력
   - 예: `마포구 대흥동 카페`, `한남동 베이커리`, `연남동 디저트`
2. **"리포트 생성하기"** 버튼 클릭
3. 약 10~30초 후 결과 확인:
   - 경쟁 매장 목록 (상호명, 주소, 카테고리)
   - AI 상권 분석 리포트 (경쟁 강도 / 포지셔닝 전략 / 창업 추천 여부)

---

## 기술 스택

| 역할 | 도구 |
|------|------|
| 앱 화면 | Streamlit |
| 매장 데이터 (주력) | 카카오 로컬 검색 API |
| 매장 데이터 (보조 1) | 네이버 지역 검색 API |
| 매장 데이터 (보조 2) | 소상공인 공공데이터 API |
| AI 분석 | Claude API (claude-haiku-4-5) |

---

## 파일 구조

```
app.py            — Streamlit 메인 앱
kakao_api.py      — 카카오 로컬 검색 API
naver_api.py      — 네이버 지역 검색 API
public_api.py     — 소상공인 공공데이터 API
gemini_api.py     — Claude AI 분석 모듈
requirements.txt  — 패키지 목록
.streamlit/
  secrets.toml    — API 키 (git 비포함)
```
