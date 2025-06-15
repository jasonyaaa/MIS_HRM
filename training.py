# Module: 訓練與發展 (T&D)
def td_module():
    import streamlit as st
    st.header("訓練與發展 (T&D)")
    if 'trainings' not in st.session_state:
        st.session_state.trainings = []
    course = st.text_input("訓練課程名稱")
    feedback = st.text_area("初步回饋")
    if st.button("新增訓練記錄"):
        st.session_state.trainings.append({'course': course, 'feedback': feedback})
        st.success("已新增訓練記錄")
    st.subheader("訓練記錄")
    for idx, t in enumerate(st.session_state.trainings):
        st.write(f"{idx+1}. {t['course']} - {t['feedback']}")