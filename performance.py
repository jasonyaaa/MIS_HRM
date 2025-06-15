import streamlit as st
import pandas as pd
from datetime import datetime

def initialize_session_state():
    if 'performance' not in st.session_state:
        st.session_state.performance = []

def kpi_module():
    initialize_session_state()
    
    st.title("績效管理 (KPI) - ST Engineering")
    
    menu = ["查看績效評估", "新增績效評估", "修改績效評估", "刪除績效評估"]
    choice = st.sidebar.selectbox("選擇操作", menu)
    
    if choice == "查看績效評估":
        st.header("績效評估列表")
        if st.session_state.performance:
            df = pd.DataFrame(st.session_state.performance)
            st.dataframe(df.style.set_properties(**{'text-align': 'left'}))
        else:
            st.write("目前沒有績效評估。")
    
    elif choice == "新增績效評估":
        st.header("新增績效評估")
        with st.form(key='add_performance_form'):
            emp = st.text_input("員工姓名")
            score = st.slider("績效分數", 0, 100, 50)
            comments = st.text_area("主管評語", placeholder="請輸入評語")
            submit_button = st.form_submit_button(label="提交")
        
        if submit_button:
            if emp.strip() == "":
                st.error("員工姓名不能為空！")
            else:
                new_performance = {
                    'emp': emp,
                    'score': score,
                    'comments': comments,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.performance.append(new_performance)
                st.success("已成功新增績效評估！")
    
    elif choice == "修改績效評估":
        st.header("修改績效評估")
        if st.session_state.performance:
            selected_index = st.selectbox(
                "選擇要修改的績效評估",
                range(len(st.session_state.performance)),
                format_func=lambda x: f"{st.session_state.performance[x]['emp']} - {st.session_state.performance[x]['score']}"
            )
            selected_performance = st.session_state.performance[selected_index]
            
            with st.form(key='edit_performance_form'):
                emp = st.text_input("員工姓名", value=selected_performance['emp'])
                score = st.slider("績效分數", 0, 100, selected_performance['score'])
                comments = st.text_area("主管評語", value=selected_performance['comments'])
                submit_button = st.form_submit_button(label="更新")
            
            if submit_button:
                if emp.strip() == "":
                    st.error("員工姓名不能為空！")
                else:
                    st.session_state.performance[selected_index] = {
                        'emp': emp,
                        'score': score,
                        'comments': comments,
                        'created_at': selected_performance['created_at'],
                        'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.success("已成功更新績效評估！")
        else:
            st.write("目前沒有績效評估可修改。")
    
    elif choice == "刪除績效評估":
        st.header("刪除績效評估")
        if st.session_state.performance:
            selected_index = st.selectbox(
                "選擇要刪除的績效評估",
                range(len(st.session_state.performance)),
                format_func=lambda x: f"{st.session_state.performance[x]['emp']} - {st.session_state.performance[x]['score']}"
            )
            if st.button("確認刪除"):
                del st.session_state.performance[selected_index]
                st.success("已成功刪除績效評估！")
        else:
            st.write("目前沒有績效評估可刪除。")

if __name__ == "__main__":
    kpi_module()