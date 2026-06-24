import streamlit as st
from naver_api import search_places, extract_coordinates
from public_api import search_stores_public
from kakao_api import search_places_kakao
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
        claude_api_key = st.secrets["CLAUDE_API_KEY"]
        public_api_key = st.secrets["PUBLIC_DATA_API_KEY"]
        kakao_api_key = st.secrets["KAKAO_API_KEY"]
    except KeyError as e:
        st.error(f"API 키 설정 오류: {e} 키가 secrets.toml에 없습니다.")
        st.stop()

    with st.spinner("📊 상권 데이터를 수집 중입니다... (약 10~30초 소요)"):
        # 1. 카카오 API 조회 (주력 - 최대 45개)
        kakao_places = []
        try:
            kakao_places = search_places_kakao(query, kakao_api_key)
        except Exception as e:
            st.warning(f"카카오 API 오류: {e}")

        # 2. 네이버 API 조회
        naver_places = []
        try:
            naver_places = search_places(query, naver_client_id, naver_client_secret)
        except Exception as e:
            st.warning(f"네이버 API 오류: {e}")

        # 3. 공공데이터 API 조회
        public_places = []
        try:
            public_places = search_stores_public(query, public_api_key)
        except Exception as e:
            st.warning(f"공공데이터 API 오류: {e}")

        # 4. 세 결과 합치기 (중복 제거, 카카오 우선)
        seen = {p["title"].replace(" ", "") for p in kakao_places}
        naver_unique = [p for p in naver_places if p["title"].replace(" ", "") not in seen]
        seen.update(p["title"].replace(" ", "") for p in naver_unique)
        public_unique = [p for p in public_places if p["title"].replace(" ", "") not in seen]
        all_places = kakao_places + naver_unique + public_unique

        if not all_places:
            st.warning("해당 지역/업종의 매장을 찾을 수 없습니다. 검색어를 바꿔 시도해보세요.")
            st.stop()

        try:
            analysis = analyze_market(all_places, query=query, api_key=claude_api_key)
        except Exception as e:
            st.error(f"AI 분석 오류: {e}")
            st.stop()

    # 결과 표시
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 경쟁 매장 수", f"{len(all_places)}개")
    with col2:
        st.metric("카카오", f"{len(kakao_places)}개")
    with col3:
        st.metric("네이버 추가", f"{len(naver_unique)}개")
    with col4:
        st.metric("공공데이터 추가", f"{len(public_unique)}개")

    st.subheader("📋 경쟁 매장 목록")
    table_data = [
        {
            "상호명": p.get("title", ""),
            "주소": p.get("address", ""),
            "카테고리": p.get("category", ""),
            "출처": p.get("source", ""),
        }
        for p in all_places
    ]
    st.dataframe(table_data, use_container_width=True)

    st.subheader("🤖 AI 상권 분석 리포트")
    st.markdown(analysis)
