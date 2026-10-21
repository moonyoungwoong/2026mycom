import streamlit as st

st.title("This is my first web")

col1, col2 = st.columns((4,1))

with col1:
    with st.expander("content"):
        url = 'https://www.youtube.com/watch?v=fkxtHbB25h4&list=RDZ83Oz5vFQns&index=2'
        st.write('이곳은 컨텐츠를 소개하는 공간입니다.')
        st.video(url)
with col2:
    with st.expander('tips'):
        st.video(url)

col3, col4 = st.columns((4,1))
with col3:
    with st.expander('데이터를 입력 받을 것'):
            name = st.text_input("이름을 입력하세요: ")
            phone = st.text_input("전화번호를 입력하세요: ")
            age = st.number_input("나이를 입력하세요 :")

            if all([name,phone,age]):
                 with open('data2.csv','a') as f:
                      f.write(f'{name},{phone},{age}\n')
                      f.close()
                    
                    
    with st.expander('Check my data'):
         st.button('Check my data')

with col4:
    with st.expander('practice2'):
        st.write('bye')




