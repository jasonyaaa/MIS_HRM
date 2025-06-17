# performance.py — 完整增強版 KPI 模組，包含持久化、日誌與美化，並新增創意功能
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os
import uuid

DATA_FILE = "kpi_data.json"
LOG_FILE = "kpi_logs.json"

# -------------------- 檔案 I/O --------------------
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -------------------- Session 初始化 --------------------
def initialize_session_state():
    if 'performance' not in st.session_state:
        st.session_state.performance = load_json(DATA_FILE)
    if 'kpi_logs' not in st.session_state:
        st.session_state.kpi_logs = load_json(LOG_FILE)
    if 'last_updated' not in st.session_state:
        st.session_state.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -------------------- 日誌記錄 --------------------
def log_action(action, details):
    entry = {
        'id': str(uuid.uuid4()),
        'action': action,
        'details': details,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.kpi_logs.append(entry)
    save_json(LOG_FILE, st.session_state.kpi_logs)

# -------------------- 核心 CRUD --------------------
def view_performance():
    st.header("📋 績效評估列表")
    st.write(f"最後更新：{st.session_state.last_updated}")
    df = pd.DataFrame(st.session_state.performance)
    if df.empty:
        st.info("目前沒有績效評估。")
        return
    # 搜尋員工
    kw = st.text_input("🔍 搜尋員工 (姓名)")
    if kw:
        df = df[df['emp'].str.contains(kw, case=False)]
    st.dataframe(df)
    # 下載按鈕
    json_str = json.dumps(st.session_state.performance, ensure_ascii=False, indent=2)
    st.download_button(
        label="Download Performance Data (JSON)",
        data=json_str,
        file_name="performance.json",
        mime="application/json"
    )

def add_performance():
    st.header("🆕 新增績效評估")
    with st.form("form_add"):
        emp = st.text_input("員工姓名")
        score = st.slider("績效分數", 0, 100, 50)
        goal_rate = st.slider("目標完成率 (%)", 0, 100, 75)
        comments = st.text_area("主管評語")
        submit = st.form_submit_button("提交")
    if submit:
        if not emp.strip():
            st.error("員工姓名不可為空。")
        else:
            entry = {
                'id': str(uuid.uuid4()),
                'emp': emp,
                'score': score,
                'goal_rate': goal_rate,
                'comments': comments,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.performance.append(entry)
            save_json(DATA_FILE, st.session_state.performance)
            log_action("新增績效", f"{emp} - {score}")
            st.success("績效評估新增成功！")

def edit_performance():
    st.header("✏️ 修改績效評估")
    if not st.session_state.performance:
        st.info("無可修改的績效評估。")
        return
    opts = {f"{p['emp']} - {p['score']}": p for p in st.session_state.performance}
    sel = st.selectbox("選擇評估項目", list(opts.keys()))
    p = opts[sel]
    with st.form("form_edit"):
        emp = st.text_input("員工姓名", p['emp'])
        score = st.slider("績效分數", 0, 100, p['score'])
        goal_rate = st.slider("目標完成率 (%)", 0, 100, p.get('goal_rate',75))
        comments = st.text_area("主管評語", p['comments'])
        submit = st.form_submit_button("更新")
    if submit:
        p.update({
            'emp': emp,
            'score': score,
            'goal_rate': goal_rate,
            'comments': comments,
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_json(DATA_FILE, st.session_state.performance)
        log_action("修改績效", f"{emp} - {score}")
        st.success("績效評估已更新！")

def delete_performance():
    st.header("🗑️ 刪除績效評估")
    if not st.session_state.performance:
        st.info("無可刪除的績效評估。")
        return
    opts = {f"{p['emp']} - {p['score']}": p for p in st.session_state.performance}
    sel = st.selectbox("選擇評估項目", list(opts.keys()))
    if st.button("確認刪除"):
        st.session_state.performance = [p for p in st.session_state.performance if p['id'] != opts[sel]['id']]
        save_json(DATA_FILE, st.session_state.performance)
        log_action("刪除績效", sel)
        st.success("績效評估已刪除！")

# -------------------- 創意功能 --------------------
def batch_delete():
    st.subheader("🔁 批量刪除績效評估")
    df = pd.DataFrame(st.session_state.performance)
    if df.empty:
        st.info("無項目可批刪。")
        return
    sels = st.multiselect("選擇要刪除的項目", list(df['emp'] + ' - ' + df['score'].astype(str)))
    if st.button("執行批量刪除"):
        for key in sels:
            emp = key.split(' - ')[0]
            st.session_state.performance = [p for p in st.session_state.performance if p['emp'] != emp]
            log_action("批量刪除績效", emp)
        save_json(DATA_FILE, st.session_state.performance)
        st.success("批量刪除完成！")

def import_data():
    st.subheader("📂 導入績效資料 (JSON)")
    up = st.file_uploader("上傳 JSON", type=["json"])
    if up:
        data = json.load(up)
        if isinstance(data, list):
            st.session_state.performance.extend(data)
            save_json(DATA_FILE, st.session_state.performance)
            log_action("導入資料", f"{len(data)} 條")
            st.success("導入成功！")
        else:
            st.error("格式錯誤！")

def analytics():
    st.subheader("📊 績效分析儀表板")
    df = pd.DataFrame(st.session_state.performance)
    if df.empty:
        st.info("無資料分析。")
        return
    avg_score = df['score'].mean()
    avg_goal = df['goal_rate'].mean()
    st.metric("平均分數", f"{avg_score:.1f}")
    st.metric("平均完成率", f"{avg_goal:.1f}%")
    st.subheader("分數分佈")
    st.bar_chart(df['score'].value_counts().sort_index())
    # 下載按鈕
    json_str = df.to_json(orient="records", force_ascii=False, indent=2)
    st.download_button(
        label="Download Analysis Data (JSON)",
        data=json_str,
        file_name="performance_analysis.json",
        mime="application/json"
    )

def view_logs():
    st.subheader("📜 操作日誌")
    df = pd.DataFrame(st.session_state.kpi_logs)
    if df.empty:
        st.info("無日誌記錄。")
    else:
        st.dataframe(df)
        # 下載按鈕
        json_str = json.dumps(st.session_state.kpi_logs, ensure_ascii=False, indent=2)
        st.download_button(
            label="Download Logs (JSON)",
            data=json_str,
            file_name="kpi_logs.json",
            mime="application/json"
        )

# -------------------- 主入口 --------------------
def kpi_module():
    initialize_session_state()
    st.title("📌 績效管理 (KPI) - ST Engineering")
    st.sidebar.title("功能選單")
    choice = st.sidebar.radio("請選擇操作", [
        "查看績效評估", "新增績效評估", "修改績效評估", "刪除績效評估",
        "批量刪除", "導入資料", "績效分析", "查看日誌"
    ])

    if choice == "查看績效評估": view_performance()
    elif choice == "新增績效評估": add_performance()
    elif choice == "修改績效評估": edit_performance()
    elif choice == "刪除績效評估": delete_performance()
    elif choice == "批量刪除": batch_delete()
    elif choice == "導入資料": import_data()
    elif choice == "績效分析": analytics()
    elif choice == "查看日誌": view_logs()

# 供 main.py 匯入
__all__ = ["kpi_module"]
