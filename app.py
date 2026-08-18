import os
import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="KEPCO-E&C & 김천 에너제틱 북-커넥트",
    page_icon="⚡",
    layout="wide"
)


# 2. 데이터 로드 함수 (캐싱 적용 및 상대 경로 자동 탐색)
@st.cache_data
def load_data():
    # app.py가 위치한 폴더 경로 자동 취득
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 1) app.py와 같은 폴더에 파일이 있는 경우
    file_main = os.path.join(current_dir, "김천_한전기술_통합도서_분석데이터.csv")
    file_mag = os.path.join(current_dir, "김천시립_정기간행물_분석데이터.csv")

    # 2) 만약 data 폴더 안에 넣은 경우를 대비한 예외 처리
    if not os.path.exists(file_main):
        file_main = os.path.join(current_dir, "data", "김천_한전기술_통합도서_분석데이터.csv")
        file_mag = os.path.join(current_dir, "data", "김천시립_정기간행물_분석데이터.csv")

    df_main = pd.read_csv(file_main)
    df_mag = pd.read_csv(file_mag)
    return df_main, df_mag


df_main, df_mag = load_data()

# 3. 사이드바 메뉴 구성
st.sidebar.title("⚡ KEPCO-E&C 북-커넥트")
st.sidebar.caption("한국전력기술 열린도서관 & 김천시 상생 독서 플랫폼")

menu = st.sidebar.radio(
    "메뉴 선택",
    [
        "1. 🔍 [열린 에너지] 원클릭 통합 장서 검색",
        "2. 🏆 [파워 셀렉션] 세종도서 인증관",
        "3. 📰 [테크 & 트렌드] 신간 및 정기간행물",
        "4. 📊 [데이터 랩] 혁신도시 독서자원 인포그래픽"
    ]
)

# -------------------------------------------------------------
# 메뉴 1: 원클릭 통합 장서 검색
# -------------------------------------------------------------
if menu == "1. 🔍 [열린 에너지] 원클릭 통합 장서 검색":
    st.header("⚡ [열린 에너지] 김천 혁신도시 통합 장서 그리드")
    st.markdown("한국전력기술 열린도서관과 김천시립도서관의 소장 도서를 원클릭으로 검색합니다.")

    col1, col2 = st.columns([3, 1])
    with col1:
        keyword = st.text_input("도서명 또는 저자명을 입력하세요", placeholder="예: 삼국지, 인공지능, 한강")
    with col2:
        source_filter = st.selectbox("보유 기관 필터", ["전체", "한전기술 & 김천시립 공동보유", "한전기술 단독보유", "김천시립 단독보유"])

    filtered_df = df_main.copy()
    if keyword:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(keyword, na=False, case=False) |
            filtered_df['author'].str.contains(keyword, na=False, case=False)
            ]
    if source_filter != "전체":
        filtered_df = filtered_df[filtered_df['holding_type'] == source_filter]

    st.write(f"🔍 검색 결과: **{len(filtered_df):,}** 건")

    # 표시용 데이터 가공
    display_cols = ['title', 'author', 'publisher', 'location_detail', 'holding_type', 'is_sejong']
    st.dataframe(
        filtered_df[display_cols].rename(columns={
            'title': '도서명',
            'author': '저자명',
            'publisher': '출판사',
            'location_detail': '비치 위치',
            'holding_type': '소장 구분',
            'is_sejong': '세종도서 인증'
        }),
        use_container_width=True,
        height=500
    )

# -------------------------------------------------------------
# 메뉴 2: 세종도서 인증관
# -------------------------------------------------------------
elif menu == "2. 🏆 [파워 셀렉션] 세종도서 인증관":
    st.header("🏆 [파워 셀렉션] 국가 공인 세종도서(우수도서) 컬렉션")
    st.markdown("한국출판문화산업진흥원이 선정한 우수 도서 중 김천 지역에 비치된 장서 목록입니다.")

    sejong_held = df_main[df_main['is_sejong'] == 'Y']

    # 상단 요약 카드
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("총 보유 세종도서", f"{len(sejong_held):,} 권")
    kpi2.metric("한전기술 열린도서관 보유", f"{len(sejong_held[sejong_held['source'] == 'KEPCO_E&C']):,} 권")
    kpi3.metric("김천시립도서관 보유", f"{len(sejong_held[sejong_held['source'] != 'KEPCO_E&C']):,} 권")

    st.divider()

    category_list = ["전체"] + list(sejong_held['sejong_category'].dropna().unique())
    selected_cat = st.selectbox("세종도서 분야 선택", category_list)

    if selected_cat != "전체":
        sejong_held = sejong_held[sejong_held['sejong_category'] == selected_cat]

    st.dataframe(
        sejong_held[['title', 'author', 'publisher', 'sejong_category', 'target_reader', 'location_detail']].rename(
            columns={
                'title': '도서명', 'author': '저자', 'publisher': '출판사',
                'sejong_category': '선정 분야', 'target_reader': '예상 독자', 'location_detail': '소장 위치'
            }),
        use_container_width=True,
        height=450
    )

# -------------------------------------------------------------
# 메뉴 3: 신간 및 정기간행물
# -------------------------------------------------------------
elif menu == "3. 📰 [테크 & 트렌드] 신간 및 정기간행물":
    st.header("📰 [테크 & 트렌드] 2026 최신 신간 & 정기간행물 지식 발전소")

    tab1, tab2 = st.tabs(["📚 2026 입고 신간 도서", "🗞️ 296종 정기간행물(잡지) 브라우저"])

    with tab1:
        new_books = df_main[df_main['source'] == 'GIMCHEON_NEW']
        st.write(f"최근 입고된 신간 도서 목록: **{len(new_books):,}** 권")
        st.dataframe(
            new_books[['title', 'author', 'publisher', 'call_no']].rename(columns={
                'title': '서명', 'author': '저작자', 'publisher': '발행자', 'call_no': '청구기호'
            }),
            use_container_width=True
        )

    with tab2:
        subject_list = ["전체"] + list(df_mag['주제'].dropna().unique())
        selected_sub = st.selectbox("간행물 주제 선택", subject_list)

        filtered_mag = df_mag if selected_sub == "전체" else df_mag[df_mag['주제'] == selected_sub]
        st.dataframe(
            filtered_mag[['제목', '주제', '기간', '비치장소', '도서관']],
            use_container_width=True
        )

# -------------------------------------------------------------
# 메뉴 4: 데이터 랩 (인포그래픽)
# -------------------------------------------------------------
elif menu == "4. 📊 [데이터 랩] 혁신도시 독서자원 인포그래픽":
    st.header("📊 [데이터 랩] 김천 혁신도시 독서 자원 융합 분석")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏢 기관별 소장 도서 분포")
        holding_counts = df_main['holding_type'].value_counts().reset_index()
        holding_counts.columns = ['구분', '도서수']

        fig1 = px.pie(
            holding_counts,
            values='도서수',
            names='구분',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        # 범례를 하단 중앙에 배치하고 여백 조정
        fig1.update_layout(
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=10, r=10, t=30, b=60)
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("🏆 세종도서 분야별 비치 비중")
        sejong_cats = df_main[df_main['is_sejong'] == 'Y']['sejong_category'].value_counts().reset_index()
        sejong_cats.columns = ['분야', '도서수']

        fig2 = px.bar(
            sejong_cats.head(10),
            x='분야',
            y='도서수',
            color='도서수',
            color_continuous_scale='Viridis'
        )
        fig2.update_layout(
            margin=dict(l=10, r=10, t=30, b=20),
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig2, use_container_width=True)