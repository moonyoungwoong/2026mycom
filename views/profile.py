"""내 정보 페이지"""
import streamlit as st

import db


def render():
    u = st.session_state.user
    st.title("내 정보")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        c1.markdown(f"**관리번호**  \n{u['id_num']}")
        c2.markdown(f"**아이디**  \n{u['userid']}")
        c1.markdown(f"**이름**  \n{u['username']}")
        c2.markdown(f"**이메일**  \n{u['email']}")
        c1.markdown(f"**가입일시**  \n{u['created_at']}")
        c2.markdown(f"**내가 입력한 데이터**  \n{db.count_data(u['userid'])}건")
