"""
app.py - Streamlit 웹앱 실행 파일
실행:  streamlit run app.py

흐름
 1) DB 준비 (myproject.db, user_table / data_table / survey_table 자동 생성)
 2) 세션 준비 (logged_in, user, page)
 3) 상단바(햄버거 ☰) + 좌측 슬라이드 메뉴
 4) 로그인 전/후에 따라 서로 다른 페이지를 보여줌
"""
import streamlit as st

st.set_page_config(
    page_title="MyProject",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",  # 처음에는 메뉴를 닫아 둠 → ☰ 버튼으로 열기
)

import auth  # noqa: E402
import db    # noqa: E402
import ui    # noqa: E402
from views import home, landing, login, profile, register, survey, pythonide  # noqa: E402

db.init_db()
auth.init_session()
ui.inject_css()

# 로그인 전/후에 접근할 수 있는 페이지
GUEST_PAGES = {"landing": landing, "register": register, "login": login}
MEMBER_PAGES = {"home": home, "survey": survey, "profile": profile}

# 접근 권한 확인: 로그인 안 했으면 회원 페이지 X, 로그인 했으면 가입/로그인 페이지 X
if auth.is_logged_in():
    if st.session_state.page not in MEMBER_PAGES:
        st.session_state.page = "home"
    pages = MEMBER_PAGES
else:
    if st.session_state.page not in GUEST_PAGES:
        st.session_state.page = "landing"
    pages = GUEST_PAGES

ui.render_navbar()
ui.render_sidebar()

# 페이지 이동 후 한 번 보여줄 메시지
flash = st.session_state.pop("flash", None)
if flash:
    kind, msg = flash
    st.toast(msg, icon="✅" if kind == "success" else "ℹ️")
    getattr(st, kind)(msg)


pages[st.session_state.page].render()
