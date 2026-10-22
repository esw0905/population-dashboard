import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="전국 고령화 단계구분도", layout="wide")

st.title("🗺️ 2026년 전국 시군구별 고령화율 단계구분도")
st.caption("전국 읍·면·동 인구 데이터를 기반으로 시군구별 65세 이상 고령인구 비율(%)을 시각화합니다.")

@st.cache_data
def load_data():
    # 1. 인구 데이터 불러오기 (2026년 6월 데이터 필터링)
    pop_url = "https://raw.githubusercontent.com/first2022-cyber/contents//main/population_ts_yearly_gender.zip"
    df = pd.read_csv(pop_url, compression='zip')
    
    # 2026년 데이터만 선택
    df_2026 = df[df['연도'] == 2026].copy()
    
    # 코드를 5자리 문자열(시군구 코드)로 변환
    df_2026['시군구코드'] = df_2026['코드'].astype(str).str.zfill(10).str[:5]
    
    # '계_'로 시작하는 컬럼 구분
    total_cols = [col for col in df_2026.columns if col.startswith('계_')]
    
    # 65세 이상 컬럼 추출 ('계_65세' ~ '계_100세 이상' 등)
    # 나이 숫자를 추출하여 65세 이상인 열을 선정
    senior_cols = []
    for col in total_cols:
        age_str = col.replace('계_', '').replace('세 이상', '').replace('세', '')
        if age_str.isdigit() and int(age_str) >= 65:
            senior_cols.append(col)
            
    # 시군구 코드로 그룹화하여 총인구 및 65세 이상 인구 합산
    agg_dict = {col: 'sum' for col in total_cols}
    df_sigungu = df_2026.groupby('시군구코드', as_index=False)[total_cols].sum()
    
    # 전체 인구 합 및 65세 이상 인구 합 계산
    df_sigungu['전체인구'] = df_sigungu[total_cols].sum(axis=1)
    df_sigungu['고령인구'] = df_sigungu[senior_cols].sum(axis=1)
    
    # 고령화율(%) 계산
    df_sigungu['고령화율'] = (df_sigungu['고령인구'] / df_sigungu['전체인구']) * 100
    df_sigungu['고령화율'] = df_sigungu['고령화율'].round(2)
    
    # 2. GeoJSON 경계 데이터 불러오기
    geojson_url = "
