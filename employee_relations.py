# Module: 員工關係 (ER)
def er_module():
    import streamlit as st
    st.header("員工關係 (ER)")
    if 'er' not in st.session_state:
        st.session_state.er = []
    emp = st.text_input("員工姓名 (申訴)")
    issue = st.text_area("申訴／意見內容")
    if st.button("提交申訴"):
        st.session_state.er.append({'emp': emp, 'issue': issue})
        st.success("已提交申訴／意見")
    st.subheader("申訴與意見記錄")
    for idx, e in enumerate(st.session_state.er):
        st.write(f"{idx+1}. {e['emp']} - {e['issue']}")