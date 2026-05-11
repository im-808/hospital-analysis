import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# 1. 페이지 설정 (제목, 레이아웃)
st.set_page_config(page_title="서울시 응급실 데이터 분석기", layout="wide")

# 2. 데이터베이스 파일 존재 여부 확인
import os

# 현재 app.py 파일 위치 기준 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 데이터베이스 파일 경로
db_path = os.path.join(BASE_DIR, 'emergency_analysis.db')

# DB 파일 존재 여부 확인
if not os.path.exists(db_path):
    st.error(f"🚨 '{db_path}' 파일이 같은 폴더에 없습니다.")
    st.stop()

# 3. 데이터베이스 연결 함수
def run_query(query):
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql(query, conn)

# --- 대시보드 화면 구성 ---

st.title("🚑 서울시 응급실 공공데이터 분석 대시보드")
st.markdown("""
공공데이터를 활용해 서울시 **응급실 이용 패턴**과 **구별 응급의료기관 현황**을 분석한 결과입니다.
""")

st.divider() # 구분선

# --- 차트 1: 월별 응급실 이용 패턴 ---
st.header("1. 월별 응급실 이용 패턴")

sql1 = """
SELECT 
    SUM("202107") as '07월', SUM("202108") as '08월', SUM("202109") as '09월',
    SUM("202110") as '10월', SUM("202111") as '11월', SUM("202112") as '12월'
FROM age_usage
"""
df1 = run_query(sql1)
# 시각화를 위해 가로 데이터를 세로로 변환 (T는 전치)
df1_melted = df1.T.reset_index()
df1_melted.columns = ['월', '이용량']

fig1 = px.line(df1_melted, x='월', y='이용량', markers=True, title="2021년 하반기 월별 총 이용량")
st.plotly_chart(fig1, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(sql1, language='sql')
    st.write("- **인사이트**: 2021년 하반기 중 특정 달에 이용객이 급증하는지 확인하여 계절적 요인을 파악할 수 있습니다.")
    st.write("- 모든 연령대의 월별 합계를 집계하여 전체적인 추세를 보여줍니다.")


# --- 차트 2: 연령별 평균 응급실 이용량 ---
st.header("2. 연령별 평균 응급실 이용량")

sql2 = """
SELECT age_group, 
       ("202107" + "202108" + "202109" + "202110" + "202111" + "202112") / 6.0 AS avg_usage
FROM age_usage
ORDER BY avg_usage DESC
"""
df2 = run_query(sql2)

fig2 = px.bar(df2, x='age_group', y='avg_usage', color='age_group', category_orders={
    "age_group": [
        "1세미만",
        "1 - 9세",
        "10 - 19세",
        "20 - 29세",
        "30 - 39세",
        "40 - 49세",
        "50 - 59세",
        "60 - 69세",
        "70 - 79세",
        "80세이상"
    ]
}, title="2021년 하반기 연령대별 평균 응급실 이용량")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(sql2, language='sql')
    st.write("- **인사이트**: 어떤 연령층이 응급실을 가장 많이 이용하는지 파악하여 타겟팅된 의료 서비스 계획을 세울 수 있습니다.")
    st.write("- 각 행(연령대)별로 6개월치 컬럼의 평균값을 계산하여 시각화했습니다.")


# --- 차트 3: 서울시 구별 응급의료기관 수 TOP 7 ---
st.header("3. 서울시 구별 응급의료기관 수 TOP 7")

sql3 = """
SELECT district as '자치구', COUNT(hospital_id) as '기관수'
FROM hospital_info
GROUP BY district
ORDER BY 기관수 DESC
LIMIT 7
"""
df3 = run_query(sql3)

fig3 = px.bar(df3, x='기관수', y='자치구', orientation='h', color='기관수', 
             color_continuous_scale='Viridis', title="서울시 내 응급의료기관이 많은 상위 7개 지역")
st.plotly_chart(fig3, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(sql3, language='sql')
    st.write("- **인사이트**: 의료 인프라가 집중된 지역을 확인할 수 있으며, 상대적으로 부족한 지역에 대한 추가 분석이 필요함을 시사합니다.")
    st.write("- `COUNT`와 `GROUP BY`를 활용해 자치구별 병원 수를 집계하고 상위 7위까지만 추출했습니다.")

st.caption("데이터 출처: 공공데이터 포털 / 분석도구: Streamlit, Plotly")
