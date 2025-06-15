# Module: 人力資源規劃 (HRP)
def hrp_module():
    import streamlit as st
    st.header("人力資源規劃 (HRP)")
    if 'hrp' not in st.session_state:
        st.session_state.hrp = []
    year = st.number_input("年度", min_value=2023, max_value=2030, value=2025)
    demand = st.text_area("人力需求描述")
    if st.button("新增規劃需求"):
        st.session_state.hrp.append({'year': year, 'demand': demand})
        st.success("已新增規划需求")
    st.subheader("現有需求列表")
    for idx, item in enumerate(st.session_state.hrp):
        st.write(f"{idx+1}. {item['year']} - {item['demand']}")