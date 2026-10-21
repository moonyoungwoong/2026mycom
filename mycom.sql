-- mycom.sql : myproject.db 테이블 생성 SQL
-- (앱 실행 시 db.py의 init_db()가 같은 내용으로 자동 생성하므로 직접 실행하지 않아도 됩니다)
-- 직접 실행:  sqlite3 myproject.db < mycom.sql

-- 1) 사용자 등록 테이블
CREATE TABLE IF NOT EXISTS user_table (
    id_num     INTEGER PRIMARY KEY AUTOINCREMENT,   -- 관리번호
    userid     TEXT    NOT NULL UNIQUE,             -- 로그인 아이디
    username   TEXT    NOT NULL,                    -- 이름
    password   TEXT    NOT NULL,                    -- 해시된 비밀번호
    email      TEXT    NOT NULL,
    created_at TEXT    NOT NULL                     -- 가입 일시 (YYYY-MM-DD HH:MM:SS)
);

-- 2) 설문 응답 테이블 : AI의 교육적 효과에 대한 인식 (5단 척도)
--    1 = 전혀 아니다, 2 = 아니다, 3 = 보통이다, 4 = 그렇다, 5 = 매우 그렇다
CREATE TABLE IF NOT EXISTS survey_table (
    id_num     INTEGER PRIMARY KEY AUTOINCREMENT,   -- 관리번호
    userid     TEXT    NOT NULL,                    -- 응답한 사용자 (user_table.userid)
    q1  INTEGER NOT NULL CHECK (q1  BETWEEN 1 AND 5),
    q2  INTEGER NOT NULL CHECK (q2  BETWEEN 1 AND 5),
    q3  INTEGER NOT NULL CHECK (q3  BETWEEN 1 AND 5),
    q4  INTEGER NOT NULL CHECK (q4  BETWEEN 1 AND 5),
    q5  INTEGER NOT NULL CHECK (q5  BETWEEN 1 AND 5),
    q6  INTEGER NOT NULL CHECK (q6  BETWEEN 1 AND 5),
    q7  INTEGER NOT NULL CHECK (q7  BETWEEN 1 AND 5),
    q8  INTEGER NOT NULL CHECK (q8  BETWEEN 1 AND 5),
    q9  INTEGER NOT NULL CHECK (q9  BETWEEN 1 AND 5),
    q10 INTEGER NOT NULL CHECK (q10 BETWEEN 1 AND 5),
    created_at TEXT    NOT NULL,                    -- 응답 일시 (YYYY-MM-DD HH:MM:SS)
    FOREIGN KEY (userid) REFERENCES user_table(userid)
);
