
# compensation.py — 完整增強版 C&B 模組，包含持久化、日誌、美化及創意功能
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os
import uuid

DATA_FILE = "comp_data.json"
LOG_FILE = "comp_logs.json"

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
    st.session_state.setdefault('comp', load_json(DATA_FILE))
    st.session_state.setdefault('comp_logs', load_json(LOG_FILE))
    st.session_state.setdefault('last_updated', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# -------------------- 日誌記錄 --------------------
def log_action(action, details):
    entry = {
        'id': str(uuid.uuid4()),
        'action': action,
        'details': details,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.comp_logs.append(entry)
    save_json(LOG_FILE, st.session_state.comp_logs)

# -------------------- 基本 CRUD 功能 --------------------
def view_compensation():
    st.header("📋 薪酬福利記錄")
    st.write(f"最後更新：{st.session_state.last_updated}")
    df = pd.DataFrame(st.session_state.comp)
    if df.empty:
        st.info("目前沒有薪酬記錄。")
        return
    # 搜尋與篩選
    kw = st.text_input("🔍 搜尋員工 (姓名)")
    if kw:
        df = df[df['emp'].str.contains(kw, case=False)]
    year_options = ['全部'] + sorted(df['created_at'].str[:4].unique().tolist())
    y = st.selectbox("按年度篩選", year_options)
    if y != '全部':
        df = df[df['created_at'].str.startswith(y)]
    st.dataframe(df)
    # 下載按鈕
    json_str = json.dumps(st.session_state.comp, ensure_ascii=False, indent=2)
    st.download_button(
        label="Download Compensation Data (JSON)",
        data=json_str,
        file_name="comp_data.json",
        mime="application/json"
    )
def add_compensation():
    st.header("🆕 新增薪酬福利記錄")
    with st.form("form_add"):
        emp = st.text_input("員工姓名")
        salary = st.number_input("月薪", min_value=0, step=1000)
        bonus = st.number_input("獎金", min_value=0, step=500)
        benefits = st.text_area("福利明細")
        submit = st.form_submit_button("提交")
    if submit:
        if not emp.strip():
            st.error("員工姓名不可為空。")
        else:
            entry = {
                'id': str(uuid.uuid4()),
                'emp': emp,
                'salary': salary,
                'bonus': bonus,
                'total': salary + bonus,
                'benefits': benefits,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.comp.append(entry)
            save_json(DATA_FILE, st.session_state.comp)
            log_action("新增薪酬", f"{emp} - {entry['total']}")
            st.success("薪酬記錄新增成功！")

def edit_compensation():
    st.header("✏️ 修改薪酬福利記錄")
    if not st.session_state.comp:
        st.info("無可修改記錄。")
        return
    opts = {f"{c['emp']} - {c['total']}": c for c in st.session_state.comp}
    key = st.selectbox("選擇記錄", list(opts.keys()))
    c = opts[key]
    with st.form("form_edit"):
        emp = st.text_input("員工姓名", c['emp'])
        salary = st.number_input("月薪", min_value=0, value=c['salary'], step=1000)
        bonus = st.number_input("獎金", min_value=0, value=c['bonus'], step=500)
        benefits = st.text_area("福利明細", c['benefits'])
        submit = st.form_submit_button("更新")
    if submit:
        c.update({
            'emp': emp,
            'salary': salary,
            'bonus': bonus,
            'total': salary + bonus,
            'benefits': benefits,
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_json(DATA_FILE, st.session_state.comp)
        log_action("修改薪酬", f"{emp} - {c['total']}")
        st.success("薪酬記錄已更新！")

def delete_compensation():
    st.header("🗑️ 刪除薪酬福利記錄")
    if not st.session_state.comp:
        st.info("無可刪除記錄。")
        return
    opts = {f"{c['emp']} - {c['total']}": c for c in st.session_state.comp}
    key = st.selectbox("選擇記錄", list(opts.keys()))
    if st.button("確認刪除"):
        st.session_state.comp = [c for c in st.session_state.comp if c['id'] != opts[key]['id']]
        save_json(DATA_FILE, st.session_state.comp)
        log_action("刪除薪酬", key)
        st.success("薪酬記錄已刪除！")

# -------------------- 創意功能 --------------------
def batch_delete():
    st.subheader("🔁 批量刪除記錄")
    df = pd.DataFrame(st.session_state.comp)
    if df.empty:
        st.info("無資料可批次刪除。")
        return
    sels = st.multiselect("選擇要刪除的記錄", df['emp'] + ' - ' + df['total'].astype(str))
    if st.button("執行批次刪除"):
        for key in sels:
            emp = key.split(' - ')[0]
            st.session_state.comp = [c for c in st.session_state.comp if c['emp'] != emp]
            log_action("批量刪除薪酬", emp)
        save_json(DATA_FILE, st.session_state.comp)
        st.success("批次刪除完成！")

def import_data():
    st.subheader("📂 導入薪酬資料 (JSON)")
    up = st.file_uploader("上傳 JSON", type=["json"])
    if up:
        data = json.load(up)
        if isinstance(data, list):
            st.session_state.comp.extend(data)
            save_json(DATA_FILE, st.session_state.comp)
            log_action("導入資料", f"{len(data)} 條記錄")
            st.success("資料導入成功！")
        else:
            st.error("格式錯誤！")

def analytics():
    st.subheader("📊 薪酬福利分析")
    df = pd.DataFrame(st.session_state.comp)
    if df.empty:
        st.info("無資料分析。")
        return
    avg_salary = df['salary'].mean()
    avg_bonus = df['bonus'].mean()
    avg_total = df['total'].mean()
    st.metric("平均月薪", f"{avg_salary:.0f}")
    st.metric("平均獎金", f"{avg_bonus:.0f}")
    st.metric("平均總薪", f"{avg_total:.0f}")
    st.subheader("薪資分佈")
    fig, ax = plt.subplots()
    df['salary'].plot(kind='hist', bins=10, ax=ax)
    ax.set_xlabel("月薪")
    st.pyplot(fig)
    # 下載按鈕
    json_str = df.to_json(orient="records", force_ascii=False, indent=2)
    st.download_button(
        label="Download Analysis Data (JSON)",
        data=json_str,
        file_name="comp_analysis.json",
        mime="application/json"
    )

def view_logs():
    st.subheader("📜 操作日誌")
    df = pd.DataFrame(st.session_state.comp_logs)
    if df.empty:
        st.info("目前無日誌記錄。")
    else:
        st.dataframe(df)
        # 下載按鈕
        json_str = json.dumps(st.session_state.comp_logs, ensure_ascii=False, indent=2)
        st.download_button(
            label="Download Logs (JSON)",
            data=json_str,
            file_name="comp_logs.json",
            mime="application/json"
        )

# -------------------- 主入口 --------------------
def cb_module():
    initialize_session_state()
    st.title("📌 薪酬與福利 (C&B) - ST Engineering")
    st.sidebar.title("功能選單")
    choice = st.sidebar.radio("請選擇操作", [
        "查看薪酬記錄", "新增薪酬記錄", "修改薪酬記錄", "刪除薪酬記錄",
        "批量刪除", "導入資料", "薪酬分析", "查看日誌"
    ])

    if choice == "查看薪酬記錄": view_compensation()
    elif choice == "新增薪酬記錄": add_compensation()
    elif choice == "修改薪酬記錄": edit_compensation()
    elif choice == "刪除薪酬記錄": delete_compensation()
    elif choice == "批量刪除": batch_delete()
    elif choice == "導入資料": import_data()
    elif choice == "薪酬分析": analytics()
    elif choice == "查看日誌": view_logs()

# 供 main.py 匯入
__all__ = ["cb_module"]
