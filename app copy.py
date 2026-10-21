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

    # 웹 컨텐츠 설계는 title(제목), box, message(내용) 세개만 있으면 됨
    # 아코디언 박스, 

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

#dbms로 로그인하는 것을 해볼것임