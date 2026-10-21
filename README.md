# MyProject - Streamlit 로그인 웹앱

## 실행 방법
```bash
pip install -r requirements.txt
streamlit run app.py
```
처음 실행하면 `myproject.db`가 자동으로 만들어지고, `data.csv`에 데이터가 있으면 한 번만 DB로 옮겨집니다.

## 디렉토리 구조
```
myproject/
├── app.py              # 실행 파일: 페이지 설정, 세션 확인, 로그인 전/후 라우팅
├── db.py               # SQLite3 (myproject.db, check_same_thread=False)
├── auth.py             # 비밀번호 해시, 회원가입/로그인 검증, 세션 관리
├── survey_items.py     # 설문 제목, 10개 문항, 5단 척도, 차트 색  ← 추가
├── mycom.sql           # user_table, survey_table 생성 SQL  ← 추가
├── ui.py               # CSS, 햄버거 상단바, 좌측 슬라이드 메뉴, Tailwind/Alpine 화면
├── views/
│   ├── __init__.py
│   ├── landing.py      # 로그인 전 랜딩페이지
│   ├── register.py     # 사용자 등록
│   ├── login.py        # 로그인
│   ├── home.py         # 로그인 후 랜딩페이지 (기존 app.py 소스 포함)
│   ├── survey.py       # 설문 참여: [설문 응시] [설문 결과 시각화] 탭  ← 추가
│   └── profile.py      # 내 정보
├── .streamlit/
│   └── config.toml     # 테마 색상
├── data.csv            # 기존 데이터 파일 (최초 1회 DB로 이전)
├── requirements.txt
├── .gitignore
└── myproject.db        # 실행 시 자동 생성
```

## 테이블
- user_table: id_num(PK), userid(UNIQUE), username, password(PBKDF2 해시), email, created_at
- data_table: id_num(PK), name, age, address, phone, owner_userid, created_at  ← 기존 data.csv 대체
- survey_table: id_num(PK), userid, q1~q10(1~5점), created_at(응답 일시)
  - 1 = 전혀 아니다, 2 = 아니다, 3 = 보통이다, 4 = 그렇다, 5 = 매우 그렇다
  - 1인 1응답: 다시 제출하면 기존 응답을 새 응답으로 수정하고 created_at도 새로 기록

## 설문 참여 메뉴
- 📝 설문 응시: AI의 교육적 효과에 대한 인식 10문항에 응답 (모든 문항 필수)
- 📊 설문 결과 시각화
  - 요약: 응답자 수, 전체 평균, 긍정 응답 비율, 최근 응답 시각
  - 문항별 응답 분포 (부정 ↔ 긍정 diverging 막대)
  - 문항별 평균 ± 표준편차
  - 문항 선택 → 응답 수, 평균, 표준편차, 중앙값, 긍정 비율, 보기별 막대그래프
  - 전체 통계표 + CSV 내려받기 (응답자 아이디는 포함하지 않음)
- 문항을 바꾸려면 survey_items.py의 QUESTIONS만 수정하면 됩니다.

## 참고
- Tailwind, Alpine.js는 CDN으로 불러오므로 인터넷 연결이 필요합니다.
- Streamlit 세션은 브라우저 탭 단위입니다. 새로고침(F5)하면 로그아웃 상태가 됩니다.
