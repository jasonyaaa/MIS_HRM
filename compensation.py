# Module: 薪酬與福利 (C&B)
def cb_module():
    import streamlit as st
    st.header("薪酬與福利 (C&B)")
    if 'comp' not in st.session_state:
        st.session_state.comp = []
    emp = st.text_input("員工姓名 (薪酬)")
    salary = st.number_input("月份薪資", min_value=0)
    benefits = st.text_area("福利明細")
    if st.button("記錄薪酬"):
        st.session_state.comp.append({'emp': emp, 'salary': salary, 'benefits': benefits})
        st.success("已記錄薪酬與福利")
    st.subheader("薪酬福利記錄")
    for idx, c in enumerate(st.session_state.comp):
        st.write(f"{idx+1}. {c['emp']} - 薪資: {c['salary']} - 福利: {c['benefits']}")