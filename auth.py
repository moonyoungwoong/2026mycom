"""
auth.py - 비밀번호 해시, 회원가입/로그인 검증, 세션 관리
 - 비밀번호는 평문으로 저장하지 않고 PBKDF2-SHA256(+salt)로 해시해서 저장합니다.
   (표준 라이브러리 hashlib만 사용하므로 추가 설치가 필요 없습니다.)
"""
import hashlib
import hmac
import re
import secrets

import streamlit as st

import db

ITERATIONS = 200_000
USERID_RE = re.compile(r"^[A-Za-z0-9_]{4,20}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------------- 비밀번호 ----------------
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iters, salt, digest = stored.split("$")
        check = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(iters))
        return hmac.compare_digest(check.hex(), digest)
    except (ValueError, AttributeError):
        return False


# ---------------- 회원가입 / 로그인 ----------------
def register_user(userid, username, email, password, password2) -> tuple[bool, str]:
    userid, username, email = userid.strip(), username.strip(), email.strip()
    if not all([userid, username, email, password, password2]):
        return False, "모든 항목을 입력해 주세요."
    if not USERID_RE.match(userid):
        return False, "아이디는 영문, 숫자, 밑줄(_)로 4~20자여야 합니다."
    if not EMAIL_RE.match(email):
        return False, "이메일 형식이 올바르지 않습니다. 예: name@example.com"
    if len(password) < 8:
        return False, "비밀번호는 8자 이상이어야 합니다."
    if password != password2:
        return False, "비밀번호 확인이 일치하지 않습니다."
    if db.get_user(userid):
        return False, f"'{userid}'는 이미 사용 중인 아이디입니다. 다른 아이디를 입력해 주세요."
    if db.email_exists(email):
        return False, "이미 등록된 이메일입니다. 로그인 메뉴를 이용해 주세요."
    db.insert_user(userid, username, hash_password(password), email)
    return True, f"{username}님, 등록이 완료되었습니다. 로그인해 주세요."


def authenticate(userid: str, password: str):
    user = db.get_user(userid.strip())
    if user and verify_password(password, user["password"]):
        user.pop("password")  # 세션에는 비밀번호 해시를 담지 않음
        return user
    return None


# ---------------- 세션 관리 ----------------
def init_session() -> None:
    defaults = {"logged_in": False, "user": None, "page": "landing", "flash": None}
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def login(user: dict) -> None:
    st.session_state.logged_in = True
    st.session_state.user = user
    st.session_state.page = "home"
    st.session_state.flash = ("success", f"{user['username']}님, 환영합니다!")


def logout() -> None:
    name = (st.session_state.user or {}).get("username", "")
    for key in list(st.session_state.keys()):
        del st.session_state[key]  # 입력값 등 세션 전체 초기화
    init_session()
    st.session_state.flash = ("info", f"{name}님, 로그아웃되었습니다.")


def is_logged_in() -> bool:
    return bool(st.session_state.get("logged_in"))


def go(page: str) -> None:
    """사이드바 버튼 on_click 콜백용 페이지 이동"""
    st.session_state.page = page
