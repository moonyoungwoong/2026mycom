"""
db.py - SQLite3 데이터베이스 모듈
 - DB 파일: myproject.db (app.py와 같은 폴더에 자동 생성)
 - check_same_thread=False : Streamlit은 여러 스레드에서 스크립트를 실행하므로 필수
 - user_table : 사용자 등록 테이블
 - data_table : 기존 data.csv(name, age, address, phone)를 대체하는 테이블
 - survey_table : AI 교육 효과 인식 설문 응답(q1~q10, 5단 척도) 테이블 (mycom.sql 참고)
"""
import csv
import sqlite3
import threading
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from survey_items import QCOLS

BASE_DIR = Path(__file__).resolve().parent
DB_NAME = BASE_DIR / "myproject.db"
CSV_PATH = BASE_DIR / "data.csv"

_lock = threading.Lock()  # 여러 세션이 동시에 쓰기 할 때를 대비한 잠금


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@st.cache_resource
def get_connection() -> sqlite3.Connection:
    """앱 전체에서 하나의 연결을 공유합니다."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    with _lock:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_table (
                id_num     INTEGER PRIMARY KEY AUTOINCREMENT,  -- 관리번호
                userid     TEXT    NOT NULL UNIQUE,            -- 로그인 아이디
                username   TEXT    NOT NULL,                   -- 이름
                password   TEXT    NOT NULL,                   -- 해시된 비밀번호
                email      TEXT    NOT NULL,
                created_at TEXT    NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS data_table (
                id_num       INTEGER PRIMARY KEY AUTOINCREMENT,
                name         TEXT,
                age          INTEGER,
                address      TEXT,
                phone        TEXT,
                owner_userid TEXT,     -- 입력한 사용자 (csv에서 옮긴 데이터는 NULL)
                created_at   TEXT
            )
            """
        )
        q_cols = ",\n".join(
            f"                {q} INTEGER NOT NULL CHECK ({q} BETWEEN 1 AND 5)" for q in QCOLS
        )
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS survey_table (
                id_num     INTEGER PRIMARY KEY AUTOINCREMENT,  -- 관리번호
                userid     TEXT    NOT NULL,                   -- 응답한 사용자
{q_cols},
                created_at TEXT    NOT NULL,                   -- 응답 일시
                FOREIGN KEY (userid) REFERENCES user_table(userid)
            )
            """
        )
        conn.commit()
    _migrate_csv_once()


def _migrate_csv_once() -> None:
    """data_table이 비어 있고 data.csv가 있으면 기존 데이터를 한 번만 옮겨옵니다."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM data_table").fetchone()[0]
    if count > 0 or not CSV_PATH.exists():
        return
    rows = []
    for enc in ("utf-8-sig", "cp949"):
        try:
            with open(CSV_PATH, encoding=enc, newline="") as f:
                reader = csv.reader(f, skipinitialspace=True)
                next(reader, None)  # 헤더(name, age, address, phone) 건너뛰기
                rows = [r for r in reader if len(r) >= 4 and r[0].strip()]
            break
        except UnicodeDecodeError:
            continue
    if not rows:
        return
    with _lock:
        conn.executemany(
            "INSERT INTO data_table (name, age, address, phone, owner_userid, created_at) "
            "VALUES (?, ?, ?, ?, NULL, ?)",
            [(r[0], _to_int(r[1]), r[2], r[3], now_str()) for r in rows],
        )
        conn.commit()


def _to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


# ---------------- user_table ----------------
def get_user(userid: str):
    row = get_connection().execute(
        "SELECT * FROM user_table WHERE userid = ?", (userid,)
    ).fetchone()
    return dict(row) if row else None


def email_exists(email: str) -> bool:
    row = get_connection().execute(
        "SELECT 1 FROM user_table WHERE lower(email) = lower(?)", (email,)
    ).fetchone()
    return row is not None


def insert_user(userid, username, password_hash, email) -> None:
    conn = get_connection()
    with _lock:
        conn.execute(
            "INSERT INTO user_table (userid, username, password, email, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (userid, username, password_hash, email, now_str()),
        )
        conn.commit()


def count_users() -> int:
    return get_connection().execute("SELECT COUNT(*) FROM user_table").fetchone()[0]


# ---------------- data_table (기존 data.csv 대체) ----------------
def insert_data(name, age, address, phone, owner_userid) -> None:
    conn = get_connection()
    with _lock:
        conn.execute(
            "INSERT INTO data_table (name, age, address, phone, owner_userid, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, int(age), address, phone, owner_userid, now_str()),
        )
        conn.commit()


def fetch_data_df() -> pd.DataFrame:
    return pd.read_sql_query(
        "SELECT id_num, name, age, address, phone, owner_userid, created_at "
        "FROM data_table ORDER BY id_num",
        get_connection(),
    )


def count_data(owner_userid: str | None = None) -> int:
    conn = get_connection()
    if owner_userid is None:
        return conn.execute("SELECT COUNT(*) FROM data_table").fetchone()[0]
    return conn.execute(
        "SELECT COUNT(*) FROM data_table WHERE owner_userid = ?", (owner_userid,)
    ).fetchone()[0]


# ---------------- survey_table (AI 교육 효과 인식 설문) ----------------
def get_my_survey(userid: str):
    """해당 사용자의 가장 최근 응답 (없으면 None)"""
    row = get_connection().execute(
        "SELECT * FROM survey_table WHERE userid = ? ORDER BY id_num DESC LIMIT 1", (userid,)
    ).fetchone()
    return dict(row) if row else None


def save_survey(userid: str, answers: dict) -> str:
    """설문 저장. 처음이면 INSERT, 이미 응답했으면 UPDATE(1인 1응답 유지).
    created_at에는 응답한 현재 날짜와 시간을 저장합니다."""
    conn = get_connection()
    values = [int(answers[q]) for q in QCOLS]
    ts = now_str()
    with _lock:
        mine = conn.execute(
            "SELECT id_num FROM survey_table WHERE userid = ? ORDER BY id_num DESC LIMIT 1", (userid,)
        ).fetchone()
        if mine:
            sets = ", ".join(f"{q} = ?" for q in QCOLS)
            conn.execute(
                f"UPDATE survey_table SET {sets}, created_at = ? WHERE id_num = ?",
                (*values, ts, mine[0]),
            )
        else:
            cols = ", ".join(QCOLS)
            marks = ", ".join("?" for _ in QCOLS)
            conn.execute(
                f"INSERT INTO survey_table (userid, {cols}, created_at) VALUES (?, {marks}, ?)",
                (userid, *values, ts),
            )
        conn.commit()
    return ts


def fetch_survey_df() -> pd.DataFrame:
    """통계용 응답 데이터 (사용자 아이디는 제외)"""
    cols = ", ".join(QCOLS)
    return pd.read_sql_query(
        f"SELECT id_num, {cols}, created_at FROM survey_table ORDER BY id_num",
        get_connection(),
    )
