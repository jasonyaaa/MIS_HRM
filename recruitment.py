# Module: 招募與遴選 (R&S)
def rs_module():
    import streamlit as st
    st.header("招募與遴選 (R&S)")
    if 'candidates' not in st.session_state:
        st.session_state.candidates = []
    name = st.text_input("候選人姓名")
    position = st.text_input("應徵職位")
    if st.button("新增候選人"):
        st.session_state.candidates.append({'name': name, 'position': position})
        st.success("已新增候選人")
    st.subheader("候選人名單")
    for idx, c in enumerate(st.session_state.candidates):
        st.write(f"{idx+1}. {c['name']} - {c['position']}")