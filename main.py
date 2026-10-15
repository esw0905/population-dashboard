import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(
    page_title="동네별 인구 피라미드",
    page_icon="👨‍👩‍👧‍👦",
    layout="wide",
)

# 따뜻하고 친근한 스타일링을 위한 톤앤매너
st.title("👨‍👩‍👧‍👦 우리 동네 인구 피라미드")
st.markdown(
    "전국 읍·면·동의 성별·연령별 인구 구조를 시각적으로 확인해보세요!"
)


# Data Caching: 데이터를 매번 새로 불러오지 않고 캐시에 저장해 성능을 높입니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/population-dashboard/main/population_ts_yearly_gender.zip"
    # Zip 압축 형태의 CSV 파일 읽기
    df = pd.read_csv(url)

    # 데이터 내 가장 최신 연도만 추출
    latest_year = df["연도"].max()
    df_latest = df[df["연도"] == latest_year].copy()

    return df_latest, latest_year


# 데이터 로딩 실행
with st.spinner("데이터를 읽어오는 중입니다..."):
    df, latest_year = load_data()

st.caption(f"💡 현재 기준 데이터 연도: **{latest_year}년**")

# --- [1단계] 지역 선택 드롭다운 (시도 -> 시군구 -> 동) ---
st.subheader("📍 지역 선택")
col1, col2, col3 = st.columns(3)

with col1:
    sido_list = sorted(df["시도"].dropna().unique())
    selected_sido = st.selectbox("시·도 선택", sido_list)

# 선택한 시·도에 해당하는 시·군·구 목록 추출
df_sido = df[df["시도"] == selected_sido]
with col2:
    sigungu_list = sorted(df_sido["시군구"].dropna().unique())
    selected_sigungu = st.selectbox("시·군·구 선택", sigungu_list)

# 선택한 시·군·구에 해당하는 읍·면·동 목록 추출
df_sigungu = df_sido[df_sido["시군구"] == selected_sigungu]
with col3:
    dong_list = sorted(df_sigungu["동"].dropna().unique())
    selected_dong = st.selectbox("읍·면·동 선택", dong_list)

# 최종 선택된 동네의 1개 행 추출
target_row = df_sigungu[df_sigungu["동"] == selected_dong].iloc[0]

# --- [2단계] 나이 라벨 순서 구성 ---
# 0세부터 99세까지 + '100세 이상'
age_labels = [f"{i}세" for i in range(100)] + ["100세 이상"]

# 남/여 인구수 데이터 추출
male_pop = [target_row[f"남_{age}"] for age in age_labels]
female_pop = [target_row[f"여_{age}"] for age in age_labels]

# 인구 피라미드 형성을 위해 남자 인구수를 음수(-)로 변환
male_pop_neg = [-val for val in male_pop]

# --- [3단계] Plotly 가로 막대 그래프 생성 ---
fig = go.Figure()

# 남자 막대그래프 (왼쪽 방향)
fig.add_trace(
    go.Bar(
        y=age_labels,
        x=male_pop_neg,
        name="남자",
        orientation="h",
        marker=dict(color="#6B9AC4"),  # 차분하고 따뜻한 파란색 계열
        customdata=male_pop,  # 툴팁(마우스 오버)에는 양수 값 표시
        hovertemplate="%{y}<br>남자 인구: %{customdata:,}명<extra></extra>",
    )
)

# 여자 막대그래프 (오른쪽 방향)
fig.add_trace(
    go.Bar(
        y=age_labels,
        x=female_pop,
        name="여자",
        orientation="h",
        marker=dict(color="#E27D60"),  # 따뜻한 붉은/코랄 계열
        hovertemplate="%{y}<br>여자 인구: %{x:,}명<extra></extra>",
    )
)

# --- [4단계] 축 정렬 및 레이아웃 설정 ---
# 핵심 requirement: 세로축(y축)을 '0세'부터 '100세 이상' 순서 그대로 고정 (아래 -> 위)
fig.update_layout(
    title=dict(
        text=f"<b>{selected_sido} {selected_sigungu} {selected_dong}</b> 인구 피라미드 ({latest_year}년)",
        font=dict(size=20),
    ),
    barmode="overlay",  # 두 막대를 이어서 표현
    bargap=0.1,  # 막대 간격
    xaxis=dict(
        title="인구수 (명)",
        tickformat=",d",  # 천 단위 쉼표
        # x축 눈금을 모두 양수로 표현하기 위한 틱 설정
        tickvals=[
            -max(male_pop) if male_pop else 0,
            -(max(male_pop) // 2) if male_pop else 0,
            0,
            (max(female_pop) // 2) if female_pop else 0,
            max(female_pop) if female_pop else 0,
        ],
        ticktext=[
            f"{max(male_pop):,}",
            f"{max(male_pop)//2:,}",
            "0",
            f"{max(female_pop)//2:,}",
            f"{max(female_pop):,}",
        ],
    ),
    yaxis=dict(
        title="연령",
        type="category",  # 범주형 축 지정
        categoryorder="array",  # 순서를 배열 지정 방식으로 고정
        categoryarray=age_labels,  # 0세가 맨 아래, 100세 이상이 맨 위로 올라가도록 설정
    ),
    legend=dict(x=0.85, y=1.05, orientation="h"),
    height=800,  # 100개 이상의 나이 축이 답답하지 않도록 높이 확보
    template="plotly_white",
)

# 스트림릿 화면에 그래프 출력
st.plotly_chart(fig, use_container_width=True)

# 요약 정보 안내
total_male = sum(male_pop)
total_female = sum(female_pop)
total_pop = total_male + total_female

st.info(
    f"📊 **{selected_dong} Total Summary**: 총인구수 **{total_pop:,}명** "
    f"(남성: {total_male:,}명 / 여성: {total_female:,}명)"
)
