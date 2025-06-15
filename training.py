import streamlit as st
import pandas as pd
from datetime import datetime

def initialize_session_state():
    if 'trainings' not in st.session_state:
        st.session_state.trainings = []

def td_module():
    initialize_session_state()
    
    st.title("訓練與發展 (T&D) - ST Engineering")
    
    menu = ["查看訓練課程", "新增訓練課程", "修改訓練課程", "刪除訓練課程"]
    choice = st.sidebar.selectbox("選擇操作", menu)
    
    if choice == "查看訓練課程":
        st.header("訓練課程列表")
        if st.session_state.trainings:
            df = pd.DataFrame(st.session_state.trainings)
            st.dataframe(df.style.set_properties(**{'text-align': 'left'}))
        else:
            st.write("目前沒有訓練課程。")
    
    elif choice == "新增訓練課程":
        st.header("新增訓練課程")
        with st.form(key='add_training_form'):
            course = st.text_input("課程名稱")
            description = st.text_area("課程描述", placeholder="請輸入課程內容")
            submit_button = st.form_submit_button(label="提交")
        
        if submit_button:
            if course.strip() == "":
                st.error("課程名稱不能為空！")
            else:
                new_training = {
                    'course': course,
                    'description': description,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.trainings.append(new_training)
                st.success("已成功新增訓練課程！")
    
    elif choice == "修改訓練課程":
        st.header("修改訓練課程")
        if st.session_state.trainings:
            selected_index = st.selectbox(
                "選擇要修改的訓練課程",
                range(len(st.session_state.trainings)),
                format_func=lambda x: f"{st.session_state.trainings[x]['course']}"
            )
            selected_training = st.session_state.trainings[selected_index]
            
            with st.form(key='edit_training_form'):
                course = st.text_input("課程名稱", value=selected_training['course'])
                description = st.text_area("課程描述", value=selected_training['description'])
                submit_button = st.form_submit_button(label="更新")
            
            if submit_button:
                if course.strip() == "":
                    st.error("課程名稱不能為空！")
                else:
                    st.session_state.trainings[selected_index] = {
                        'course': course,
                        'description': description,
                        'created_at': selected_training['created_at'],
                        'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.success("已成功更新訓練課程！")
        else:
            st.write("目前沒有訓練課程可修改。")
    
    elif choice == "刪除訓練課程":
        st.header("刪除訓練課程")
        if st.session_state.trainings:
            selected_index = st.selectbox(
                "選擇要刪除的訓練課程",
                range(len(st.session_state.trainings)),
                format_func=lambda x: f"{st.session_state.trainings[x]['course']}"
            )
            if st.button("確認刪除"):
                del st.session_state.trainings[selected_index]
                st.success("已成功刪除訓練課程！")
        else:
            st.write("目前沒有訓練課程可刪除。")

if __name__ == "__main__":
    td_module()