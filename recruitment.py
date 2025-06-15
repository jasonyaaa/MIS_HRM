import streamlit as st
import pandas as pd
from datetime import datetime

def initialize_session_state():
    if 'candidates' not in st.session_state:
        st.session_state.candidates = []

def rs_module():
    initialize_session_state()
    
    st.title("招募與遴選 (R&S) - ST Engineering")
    
    menu = ["查看候選人", "新增候選人", "修改候選人", "刪除候選人"]
    choice = st.sidebar.selectbox("選擇操作", menu)
    
    if choice == "查看候選人":
        st.header("候選人名單")
        if st.session_state.candidates:
            df = pd.DataFrame(st.session_state.candidates)
            st.dataframe(df.style.set_properties(**{'text-align': 'left'}))
        else:
            st.write("目前沒有候選人。")
    
    elif choice == "新增候選人":
        st.header("新增候選人")
        with st.form(key='add_candidate_form'):
            name = st.text_input("姓名")
            position = st.text_input("應徵職位")
            resume = st.text_area("簡歷", placeholder="請輸入簡歷內容")
            submit_button = st.form_submit_button(label="提交")
        
        if submit_button:
            if name.strip() == "" or position.strip() == "":
                st.error("姓名和職位不能為空！")
            else:
                new_candidate = {
                    'name': name,
                    'position': position,
                    'resume': resume,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.candidates.append(new_candidate)
                st.success("已成功新增候選人！")
    
    elif choice == "修改候選人":
        st.header("修改候選人")
        if st.session_state.candidates:
            selected_index = st.selectbox(
                "選擇要修改的候選人",
                range(len(st.session_state.candidates)),
                format_func=lambda x: f"{st.session_state.candidates[x]['name']} - {st.session_state.candidates[x]['position']}"
            )
            selected_candidate = st.session_state.candidates[selected_index]
            
            with st.form(key='edit_candidate_form'):
                name = st.text_input("姓名", value=selected_candidate['name'])
                position = st.text_input("應徵職位", value=selected_candidate['position'])
                resume = st.text_area("簡歷", value=selected_candidate['resume'])
                submit_button = st.form_submit_button(label="更新")
            
            if submit_button:
                if name.strip() == "" or position.strip() == "":
                    st.error("姓名和職位不能為空！")
                else:
                    st.session_state.candidates[selected_index] = {
                        'name': name,
                        'position': position,
                        'resume': resume,
                        'created_at': selected_candidate['created_at'],
                        'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.success("已成功更新候選人！")
        else:
            st.write("目前沒有候選人可修改。")
    
    elif choice == "刪除候選人":
        st.header("刪除候選人")
        if st.session_state.candidates:
            selected_index = st.selectbox(
                "選擇要刪除的候選人",
                range(len(st.session_state.candidates)),
                format_func=lambda x: f"{st.session_state.candidates[x]['name']} - {st.session_state.candidates[x]['position']}"
            )
            if st.button("確認刪除"):
                del st.session_state.candidates[selected_index]
                st.success("已成功刪除候選人！")
        else:
            st.write("目前沒有候選人可刪除。")

if __name__ == "__main__":
    rs_module()