import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="동네별 인구 피라미드",
    page_icon="👨‍👩‍👧‍👦",
    layout="wide",
)

# 화면 상단 타이틀 및 설명
st.title("👨‍👩‍👧‍👦 우리 동네 인구 피라미드")
st.markdown(
    "전국 읍·면·동의 성별·연령별 인구 구조를 시각적으로 확인해보세요!"
)


# 데이터 로딩 함수 (캐싱 적용)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/first2022-cyber/contents/main/population_ts_yearly_gender.zip"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/110.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    df = pd.read_csv(io.BytesIO(response.content))

    # 데이터셋 내 가장 최신 연도만 추출
    latest_year = df["연도"].max()
    df_latest = df[df["연도"] == latest_year].copy()

    return df_latest, latest_year


# 데이터 불러오기 실행
try:
    with st.spinner("인구 데이터를 읽어오는 중입니다..."):
        df, latest_year = load_data()
    st.caption(f"💡 현재 기준 데이터 연도: **{latest_year}년**")
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# --- [1단계] 지역 선택 드롭다운 (시도 -> 시군구 -> 동) ---
st.subheader("📍 지역 선택")
col1, col2, col3 = st.columns(3)

with col1:
    sido_list = sorted(df["시도"].dropna().unique())
    selected_sido = st.selectbox("시·도 선택", sido_list)

df_sido = df[df["시도"] == selected_sido]

with col2:
    sigungu_list = sorted(df_sido["시군구"].dropna().unique())
    selected_sigungu = st.selectbox("시·군·구 선택", sigungu_list)

df_sigungu = df_sido[df_sido["시군구"] == selected_sigungu]

with col3:
    dong_list = sorted(df_sigungu["동"].dropna().unique())
    selected_dong = st.selectbox("읍·면·동 선택", dong_list)

# 선택된 동네 1개 행 추출
target_row = df_sigungu[df_sigungu["동"] == selected_dong].iloc[0]

# --- [2단계] 나이 라벨 순서 구성 및 데이터 추출 ---
age_labels = [f"{i}세" for i in range(100)] + ["100세 이상"]

male_pop = [target_row[f"남_{age}"] for age in age_labels]
female_pop = [target_row[f"여_{age}"] for age in age_labels]

# 왼쪽(남자) 배치를 위해 음수(-) 변환
male_pop_neg = [-val for val in male_pop]

# --- [3단계] Plotly 가로 막대 그래프 생성 ---
fig = go.Figure()

# 남자 막대그래프
fig.add_trace(
    go.Bar(
        y=age_labels,
        x=male_pop_neg,
        name="남자",
        orientation="h",
        marker=dict(color="#6B9AC4"),
        customdata=male_pop,
        hovertemplate="%{y}<br>남자 인구: %{customdata:,}명<extra></extra>",
    )
)

# 여자 막대그래프
fig.add_trace(
    go.Bar(
        y=age_labels,
        x=female_pop,
        name="여자",
        orientation="h",
        marker=dict(color="#E27D60"),
        hovertemplate="%{y}<br>여자 인구: %{x:,}명<extra></extra>",
    )
)

# 축 최대값 계산
max_male = max(male_pop) if male_pop else 0
max_female = max(female_pop) if female_pop else 0

# --- [4단계] 축 설정 및 레이아웃 고정 ---
fig.update_layout(
    title={
        "text": f"<b>{selected_sido} {selected_sigungu} {selected_dong}</b> 인구 피라미드 ({latest_year}년)",
        "font": {"size": 20},
    },
    barmode="overlay",
    bargap=0.1,
    xaxis={
        "title": "인구수 (명)",
        "tickformat": ",d",
        "tickvals": [-max_male, -max_male // 2, 0, max_female // 2, max_female],
        "ticktext": [
            f"{max_male:,}",
            f"{max_male//2:,}",
            "0",
            f"{max_female//2:,}",
            f"{max_female:,}",
        ],
    },
    yaxis={
        "title
