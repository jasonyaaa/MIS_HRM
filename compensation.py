import streamlit as st
import pandas as pd
from datetime import datetime

def initialize_session_state():
    if 'comp' not in st.session_state:
        st.session_state.comp = []

def cb_module():
    initialize_session_state()
    
    st.title("薪酬與福利 (C&B) - ST Engineering")
    
    menu = ["查看薪酬記錄", "新增薪酬記錄", "修改薪酬記錄", "刪除薪酬記錄"]
    choice = st.sidebar.selectbox("選擇操作", menu)
    
    if choice == "查看薪酬記錄":
        st.header("薪酬記錄列表")
        if st.session_state.comp:
            df = pd.DataFrame(st.session_state.comp)
            st.dataframe(df.style.set_properties(**{'text-align': 'left'}))
        else:
            st.write("目前沒有薪酬記錄。")
    
    elif choice == "新增薪酬記錄":
        st.header("新增薪酬記錄")
        with st.form(key='add_comp_form'):
            emp = st.text_input("員工姓名")
            salary = st.number_input("月份薪資", min_value=0)
            benefits = st.text_area("福利明細", placeholder="請輸入福利內容")
            submit_button = st.form_submit_button(label="提交")
        
        if submit_button:
            if emp.strip() == "":
                st.error("員工姓名不能為空！")
            else:
                new_comp = {
                    'emp': emp,
                    'salary': salary,
                    'benefits': benefits,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.comp.append(new_comp)
                st.success("已成功新增薪酬記錄！")
    
    elif choice == "修改薪酬記錄":
        st.header("修改薪酬記錄")
        if st.session_state.comp:
            selected_index = st.selectbox(
                "選擇要修改的薪酬記錄",
                range(len(st.session_state.comp)),
                format_func=lambda x: f"{st.session_state.comp[x]['emp']} - {st.session_state.comp[x]['salary']}"
            )
            selected_comp = st.session_state.comp[selected_index]
            
            with st.form(key='edit_comp_form'):
                emp = st.text_input("員工姓名", value=selected_comp['emp'])
                salary = st.number_input("月份薪資", min_value=0, value=selected_comp['salary'])
                benefits = st.text_area("福利明細", value=selected_comp['benefits'])
                submit_button = st.form_submit_button(label="更新")
            
            if submit_button:
                if emp.strip() == "":
                    st.error("員工姓名不能為空！")
                else:
                    st.session_state.comp[selected_index] = {
                        'emp': emp,
                        'salary': salary,
                        'benefits': benefits,
                        'created_at': selected_comp['created_at'],
                        'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.success("已成功更新薪酬記錄！")
        else:
            st.write("目前沒有薪酬記錄可修改。")
    
    elif choice == "刪除薪酬記錄":
        st.header("刪除薪酬記錄")
        if st.session_state.comp:
            selected_index = st.selectbox(
                "選擇要刪除的薪酬記錄",
                range(len(st.session_state.comp)),
                format_func=lambda x: f"{st.session_state.comp[x]['emp']} - {st.session_state.comp[x]['salary']}"
            )
            if st.button("確認刪除"):
                del st.session_state.comp[selected_index]
                st.success("已成功刪除薪酬記錄！")
        else:
            st.write("目前沒有薪酬記錄可刪除。")

if __name__ == "__main__":
    cb_module()