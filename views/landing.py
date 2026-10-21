"""로그인 전 랜딩페이지"""
import streamlit as st

import auth
import db
import ui


def render():
    ui.guest_hero(db.count_users())
    c1, c2, _ = st.columns((1, 1, 3))
    c1.button("사용자 등록하기", type="primary", width="stretch",
              on_click=auth.go, args=("register",))
    c2.button("로그인", width="stretch", on_click=auth.go, args=("login",))
