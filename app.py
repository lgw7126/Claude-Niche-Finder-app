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
