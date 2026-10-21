"""
로그인 후 랜딩페이지
 - 위쪽: 대시보드(Tailwind + Alpine.js)
 - 아래쪽: 첨부한 기존 app.py 소스를 최대한 그대로 유지
   (바뀐 점: data.csv 대신 SQLite(data_table)에 저장/조회, 중복 저장을 막기 위해 저장 버튼 추가)
"""
import streamlit as st

import db
import ui


def render():
    user = st.session_state.user
    ui.dashboard_hero(user, db.count_users(), db.count_data(), db.count_data(user["userid"]))

    # ======================= 기존 소스 시작 =======================
    st.title("This is my 1st web app")
    name = st.text_input('Name? : ', value=user["username"])
    if name == "":
        st.error('please input your name')
    else:
        col1, col2 = st.columns((4, 1))
        with col1:
            with st.expander(f'{name}님 여기는 content 입니다'):
                url = 'https://www.youtube.com/watch?v=MHShfgqrUWs'
                st.write('content....')
                st.video(url)
        with col2:
            with st.expander('Tips...'):
                st.write('tips...')

        col3, col4 = st.columns((4, 1))
        with col3:
            with st.expander('content'):
                age = st.number_input('Age? ', step=1)
                address = st.text_input('Adress? ')
                phone = st.text_input('Phone? ')

                # 기존: 값이 모두 채워지면 화면이 새로 그려질 때마다 data.csv에 계속 추가됨
                # 변경: [Save] 버튼을 눌렀을 때 한 번만 SQLite에 저장
                if st.button('Save', type="primary"):
                    if all([name, age, address, phone]):
                        db.insert_data(name, age, address, phone, user["userid"])
                        st.success('Successful Add')
                    else:
                        st.warning('Age, Adress, Phone을 모두 입력해 주세요.')
            with st.expander('Check my DB'):
                if st.button('Check my db'):
                    df = db.fetch_data_df()  # 기존: pd.read_csv('./data.csv', encoding="cp949")
                    st.write(df)
        with col4:
            with st.expander('Tips...'):
                st.write('tips...')
    # ======================= 기존 소스 끝 =========================
