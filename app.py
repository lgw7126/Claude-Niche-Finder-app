import streamlit as st
from naver_api import search_places, extract_coordinates
from public_api import search_stores_public
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
        public_api_key = st.secrets["PUBLIC_DATA_API_KEY"]
    except KeyError as e:
        st.error(f"API 키 설정 오류: {e} 키가 secrets.toml에 없습니다.")
        st.stop()

    with st.spinner("📊 상권 데이터를 수집 중입니다... (약 10~30초 소요)"):
        # 1. 네이버 API 조회
        naver_places = []
        coords = None
        try:
            naver_places = search_places(query, naver_client_id, naver_client_secret)
            coords = extract_coordinates(naver_places)
        except Exception as e:
            st.warning(f"네이버 API 일시 오류 (공공데이터로 계속 진행): {e}")

        # 2. 소상공인 공공데이터 API 조회
        public_places = []
        try:
            public_places = search_stores_public(query, public_api_key)
        except Exception as e:
            st.warning(f"공공데이터 API 일시 오류 (네이버 결과만 사용): {e}")

        # 3. 두 결과 합치기 (공공데이터 우선, 네이버로 중복 제거)
        public_titles = {p["title"].replace(" ", "") for p in public_places}
        naver_unique = [
            p for p in naver_places
            if p["title"].replace(" ", "") not in public_titles
        ]
        all_places = public_places + naver_unique

        if not all_places:
            st.warning("해당 지역/업종의 매장을 찾을 수 없습니다. 검색어를 바꿔 시도해보세요.")
            st.stop()

        try:
            analysis = analyze_market(all_places, query=query, api_key=gemini_api_key)
        except Exception as e:
            st.error(f"AI 분석 오류: {e}")
            st.stop()

    # 결과 표시
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 경쟁 매장 수", f"{len(all_places)}개")
    with col2:
        st.metric("공공데이터", f"{len(public_places)}개")
    with col3:
        st.metric("네이버 추가", f"{len(naver_unique)}개")

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
    st.info(analysis)
