"""로그인 페이지"""
import streamlit as st

import auth


def render():
    _, mid, _ = st.columns((1, 2, 1))
    with mid:
        st.title("로그인")
        st.caption("등록한 아이디와 비밀번호를 입력하세요.")
        with st.form("login_form"):
            userid = st.text_input("아이디", value=st.session_state.get("login_userid", ""))
            pw = st.text_input("비밀번호", type="password")
            submitted = st.form_submit_button("로그인", width="stretch")

        if submitted:
            if not userid or not pw:
                st.error("아이디와 비밀번호를 모두 입력해 주세요.")
            else:
                user = auth.authenticate(userid, pw)
                if user:
                    st.session_state.pop("login_userid", None)
                    auth.login(user)
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

        st.button("계정이 없나요? 사용자 등록", on_click=auth.go, args=("register",))
