"""
설문 참여 페이지 (로그인 후)
 - Tab 1 "설문 응시"        : AI의 교육적 효과 인식 10문항(5단 척도)에 응답 → survey_table 저장
 - Tab 2 "설문 결과 시각화" : 전체 요약, 문항별 응답 분포, 문항별 평균, 문항 상세, 통계표
차트는 Streamlit에 함께 설치되는 Altair를 사용합니다. (추가 설치 없음)
"""

import streamlit as st
import streamlit.components.v1 as components



def render():
    components.html(
        '<iframe style="border:1px #FFFFFF none" src="https://www.online-python.com/" title="iFrame" width="100%" height="1024px" scrolling="no" frameborder="no" allow="fullscreen"></iframe>',height=1040
    )

