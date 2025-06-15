import streamlit as st
import pandas as pd
from datetime import datetime

def initialize_session_state():
    if 'er' not in st.session_state:
        st.session_state.er = []

def er_module():
    initialize_session_state()
    
    st.title("員工關係 (ER) - ST Engineering")
    
    menu = ["查看申訴/意見", "提交申訴/意見", "修改申訴/意見", "刪除申訴/意見"]
    choice = st.sidebar.selectbox("選擇操作", menu)
    
    if choice == "查看申訴/意見":
        st.header("申訴與意見記錄")
        if st.session_state.er:
            df = pd.DataFrame(st.session_state.er)
            st.dataframe(df.style.set_properties(**{'text-align': 'left'}))
        else:
            st.write("目前沒有申訴/意見。")
    
    elif choice == "提交申訴/意見":
        st.header("提交申訴/意見")
        with st.form(key='add_er_form'):
            emp = st.text_input("員工姓名 (可選)", placeholder="可匿名")
            issue = st.text_area("申訴/意見內容", placeholder="請輸入內容")
            submit_button = st.form_submit_button(label="提交")
        
        if submit_button:
            if issue.strip() == "":
                st.error("內容不能為空！")
            else:
                new_er = {
                    'emp': emp if emp.strip() != "" else "匿名",
                    'issue': issue,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.er.append(new_er)
                st.success("已成功提交申訴/意見！")
    
    elif choice == "修改申訴/意見":
        st.header("修改申訴/意見")
        if st.session_state.er:
            selected_index = st.selectbox(
                "選擇要修改的申訴/意見",
                range(len(st.session_state.er)),
                format_func=lambda x: f"{st.session_state.er[x]['emp']} - {st.session_state.er[x]['issue'][:20]}..."
            )
            selected_er = st.session_state.er[selected_index]
            
            with st.form(key='edit_er_form'):
                emp = st.text_input("員工姓名 (可選)", value=selected_er['emp'])
                issue = st.text_area("申訴/意見內容", value=selected_er['issue'])
                submit_button = st.form_submit_button(label="更新")
            
            if submit_button:
                if issue.strip() == "":
                    st.error("內容不能為空！")
                else:
                    st.session_state.er[selected_index] = {
                        'emp': emp if emp.strip() != "" else "匿名",
                        'issue': issue,
                        'created_at': selected_er['created_at'],
                        'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.success("已成功更新申訴/意見！")
        else:
            st.write("目前沒有申訴/意見可修改。")
    
    elif choice == "刪除申訴/意見":
        st.header("刪除申訴/意見")
        if st.session_state.er:
            selected_index = st.selectbox(
                "選擇要刪除的申訴/意見",
                range(len(st.session_state.er)),
                format_func=lambda x: f"{st.session_state.er[x]['emp']} - {st.session_state.er[x]['issue'][:20]}..."
            )
            if st.button("確認刪除"):
                del st.session_state.er[selected_index]
                st.success("已成功刪除申訴/意見！")
        else:
            st.write("目前沒有申訴/意見可刪除。")

if __name__ == "__main__":
    er_module()