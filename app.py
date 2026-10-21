# 이 파일은 streamlit webapp의 실행파일 app.py의 일부입니다.
# 사용자 로그인 시스템을 붙이려고 합니다.
# DB는 현재 data.csv 파일 기반으로 되어 있지만,
# 이것을 sqlite3를 사용해서 새로 개발하려고 합니다.
# DB name은 myproject.db로 합니다. check_same_thread를 설정합니다.
# 사용자 등록을 위한 테이블은 user_table로 합니다.
# user_table은 id_num(관리번호, primary key), userid, username, password, email, created_at로 합니다.
# 햄버그 메뉴를 추가해 주시고, 좌측 메뉴가 밀려서 열렸다가 닫히도록 합니다.
# 하위 메뉴는 사용자 등록, 로그인으로 합니다.
# 비로그인과 로그인 후의 세션 관리가 되어야 합니다. 따라서 로그인 전과 후에 랜딩페이지를 서로 다르게 합니다.
# 최신의 모던한 ui/ux를 적용합니다. tailwind, flexbox, alphine.js등 최신의 자바스크립트를 적용해주세요.
# 첨부한 기본이 되는 streamlit 소스를 최대한 유지하면서 코드를 완전하게 생성해주세요. 

import streamlit as st
st.title("This is my 1st web app")
name = st.text_input('Name? : ')
if name == "":
    st.error('please input your name')
else:
    col1, col2 = st.columns((4,1))
    with col1:
        with st.expander(f'{name}님 여기는 content 입니다'):
            url = 'https://www.youtube.com/watch?v=MHShfgqrUWs'
            st.write('content....')
            st.video(url)
    with col2:
        with st.expander('Tips...'):
            st.write('tips...')

    col3, col4 = st.columns((4,1))
    with col3:
        with st.expander('content'):
            age = st.number_input('Age? ', step=1)
            address = st.text_input('Adress? ')
            phone = st.text_input('Phone? ')

            if all([name, age, address, phone]):
                with open('data.csv','a') as f:
                    f.write(f'{name},{age},{address},{phone}\n')
                    f.close()
                st.success('Successful Add')
        with st.expander('Check my DB'):
            if st.button('Check my db'):
                import pandas as pd
                df = pd.read_csv('./data.csv',encoding="cp949")
                st.write(df)
    with col4:
        with st.expander('Tips...'):
            st.write('tips...')

