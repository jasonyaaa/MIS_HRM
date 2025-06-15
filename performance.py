# Module: 績效管理 (KPI)
def kpi_module():
    import streamlit as st
    st.header("績效管理 (KPI)")
    if 'performance' not in st.session_state:
        st.session_state.performance = []
    emp = st.text_input("員工姓名")
    score = st.slider("績效分數", 0, 100, 50)
    comments = st.text_area("主管評語")
    if st.button("新增績效評估"):
        st.session_state.performance.append({'emp': emp, 'score': score, 'comments': comments})
        st.success("已新增績效評估")
    st.subheader("績效評估列表")
    for idx, p in enumerate(st.session_state.performance):
        st.write(f"{idx+1}. {p['emp']} - 分數: {p['score']} - 評語: {p['comments']}")