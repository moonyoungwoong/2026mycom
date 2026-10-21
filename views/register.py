"""사용자 등록 페이지 (user_table에 저장)"""
import streamlit as st

import auth


def render():
    _, mid, _ = st.columns((1, 2, 1))
    with mid:
        st.title("사용자 등록")
        st.caption("등록한 아이디와 비밀번호로 로그인합니다. 비밀번호는 암호화되어 저장됩니다.")
        with st.form("register_form", clear_on_submit=False):
            userid = st.text_input("아이디", placeholder="영문, 숫자, _ 4~20자")
            username = st.text_input("이름")
            email = st.text_input("이메일", placeholder="name@example.com")
            pw = st.text_input("비밀번호", type="password", placeholder="8자 이상")
            pw2 = st.text_input("비밀번호 확인", type="password")
            submitted = st.form_submit_button("등록하기", width="stretch")

        if submitted:
            ok, msg = auth.register_user(userid, username, email, pw, pw2)
            if ok:
                st.session_state.flash = ("success", msg)
                st.session_state.page = "login"
                st.session_state.login_userid = userid.strip()  # 로그인 화면에 아이디 미리 채우기
                st.rerun()
            else:
                st.error(msg)

        st.button("이미 계정이 있나요? 로그인", on_click=auth.go, args=("login",))
