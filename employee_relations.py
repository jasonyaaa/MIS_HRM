
# employee_relations.py — 完整增強版 ER 模組，包含持久化、日誌、美化及進階創意功能
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os
import uuid

DATA_FILE = "er_data.json"
LOG_FILE = "er_logs.json"

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
    st.session_state.setdefault('er', load_json(DATA_FILE))
    st.session_state.setdefault('er_logs', load_json(LOG_FILE))
    st.session_state.setdefault('last_updated', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# -------------------- 日誌記錄 --------------------
def log_action(action, details):
    entry = {'id': str(uuid.uuid4()), 'action': action, 'details': details,
             'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    st.session_state.er_logs.append(entry)
    save_json(LOG_FILE, st.session_state.er_logs)

# -------------------- 核心 CRUD --------------------
def view_er():
    st.header("📋 申訴與意見列表")
    st.write(f"最後更新：{st.session_state.last_updated}")
    df = pd.DataFrame(st.session_state.er)
    if df.empty:
        st.info("目前無任何申訴/意見。")
        return
    # 搜尋與過濾
    kw = st.text_input("🔍 關鍵字搜尋 (內容)")
    if kw:
        df = df[df['issue'].str.contains(kw, case=False)]
    anon = st.checkbox("僅顯示匿名提交")
    if anon:
        df = df[df['emp']=='匿名']
    st.dataframe(df)
    # 下載按鈕
    json_str = json.dumps(st.session_state.er, ensure_ascii=False, indent=2)
    st.download_button(
        label="Download ER Data (JSON)",
        data=json_str,
        file_name="er_data.json",
        mime="application/json"
    )

def submit_er():
    st.header("✉️ 提交申訴/意見")
    with st.form("form_add"):
        emp = st.text_input("員工姓名 (可留空)")
        category = st.selectbox("類別", ["工作環境", "薪酬福利", "管理風格", "其他"])
        issue = st.text_area("內容描述")
        urgency = st.slider("緊急程度 (1-5)",1,5,3)
        submit = st.form_submit_button("提交")
    if submit:
        if not issue.strip(): st.error("內容不可為空。")
        else:
            entry = {'id':str(uuid.uuid4()), 'emp':emp.strip() or '匿名',
                     'category':category, 'urgency':urgency,
                     'issue':issue, 'created_at':datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            st.session_state.er.append(entry)
            save_json(DATA_FILE, st.session_state.er)
            log_action("提交意見", f"{entry['id']}")
            st.success("已成功提交！")

def edit_er():
    st.header("✏️ 修改申訴/意見")
    if not st.session_state.er:
        st.info("無可修改項目。")
        return
    opts = {f"{e['emp']} | {e['category']} | {e['issue'][:20]}": e for e in st.session_state.er}
    sel = st.selectbox("選擇項目", list(opts.keys()))
    e = opts[sel]
    with st.form("form_edit"):
        emp = st.text_input("員工姓名", e['emp'])
        category = st.selectbox("類別", ["工作環境","薪酬福利","管理風格","其他"], index=["工作環境","薪酬福利","管理風格","其他"].index(e['category']))
        urgency = st.slider("緊急程度 (1-5)",1,5,e['urgency'])
        issue = st.text_area("內容描述", e['issue'])
        submit = st.form_submit_button("更新")
    if submit:
        if not issue.strip(): st.error("內容不可為空。")
        else:
            e.update({'emp':emp.strip() or '匿名','category':category,'urgency':urgency,'issue':issue,
                      'updated_at':datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            save_json(DATA_FILE, st.session_state.er)
            log_action("修改意見", sel)
            st.success("更新成功！")

def delete_er():
    st.header("🗑️ 刪除申訴/意見")
    if not st.session_state.er:
        st.info("無可刪除項目。")
        return
    opts = {f"{e['emp']} | {e['category']} | {e['issue'][:20]}": e for e in st.session_state.er}
    sel = st.selectbox("選擇刪除項目", list(opts.keys()))
    if st.button("確認刪除"):
        st.session_state.er = [x for x in st.session_state.er if x['id']!=opts[sel]['id']]
        save_json(DATA_FILE, st.session_state.er)
        log_action("刪除意見", sel)
        st.success("刪除成功！")

# -------------------- 創意功能 --------------------
def batch_delete_er():
    st.subheader("🔁 批量刪除意見")
    df = pd.DataFrame(st.session_state.er)
    if df.empty:
        st.info("無資料可批刪。")
        return
    sels = st.multiselect("選擇要刪除的項目", df.index.astype(str))
    if st.button("執行批次刪除"):
        for idx in sorted(map(int,sels), reverse=True):
            log_action("批量刪除意見", st.session_state.er[idx]['id'])
            del st.session_state.er[idx]
        save_json(DATA_FILE, st.session_state.er)
        st.success("批次刪除完成！")



def analytics_er():
    st.subheader("📊 申訴/意見分析")
    df = pd.DataFrame(st.session_state.er)
    if df.empty:
        st.info("無資料可分析。")
        return
    st.metric("總提交數", len(df))
    st.metric("匿名提交比例", f"{(df['emp']=='匿名').mean()*100:.1f}%")
    st.subheader("各類別比例")
    st.bar_chart(df['category'].value_counts())
    # 下載按鈕
    json_str = df.to_json(orient="records", force_ascii=False, indent=2)
    st.download_button(
        label="Download Analysis Data (JSON)",
        data=json_str,
        file_name="er_analysis.json",
        mime="application/json"
    )


def view_logs_er():
    st.subheader("📜 操作日誌")
    df = pd.DataFrame(st.session_state.er_logs)
    if df.empty:
        st.info("無日誌記錄。")
    else:
        st.dataframe(df)
        # 下載按鈕
        json_str = json.dumps(st.session_state.er_logs, ensure_ascii=False, indent=2)
        st.download_button(
            label="Download Logs (JSON)",
            data=json_str,
            file_name="er_logs.json",
            mime="application/json"
        )

# -------------------- 主入口 --------------------
def er_module():
    initialize_session_state()
    st.title("📌 員工關係 (ER) - ST Engineering")
    st.sidebar.title("功能選單")
    choice = st.sidebar.radio("請選擇操作", [
        "查看申訴/意見", "提交申訴/意見", "修改申訴/意見", "刪除申訴/意見",
        "批量刪除", "意見分析", "查看日誌"
    ])

    if choice == "查看申訴/意見": view_er()
    elif choice == "提交申訴/意見": submit_er()
    elif choice == "修改申訴/意見": edit_er()
    elif choice == "刪除申訴/意見": delete_er()
    elif choice == "批量刪除": batch_delete_er()

    elif choice == "意見分析": analytics_er()
    elif choice == "查看日誌": view_logs_er()

# 供 main.py 匯入
__all__ = ["er_module"]

