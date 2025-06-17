# hr_planning.py — 完整增強版 HRP 模組，包含日曆、批次、視覺化分析與日誌功能
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
import json
import os
import uuid

DATA_FILE = "hrp_data.json"
LOG_FILE = "hrp_logs.json"
CALENDAR_FILE = "hrp_calendar.json"

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
    if 'hrp_data' not in st.session_state:
        st.session_state.hrp_data = load_json(DATA_FILE)
    if 'hrp_logs' not in st.session_state:
        st.session_state.hrp_logs = load_json(LOG_FILE)
    if 'hrp_calendar' not in st.session_state:
        st.session_state.hrp_calendar = load_json(CALENDAR_FILE)
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
    st.session_state.hrp_logs.append(entry)
    save_json(LOG_FILE, st.session_state.hrp_logs)

# -------------------- 各功能區 --------------------
def view_data():
    st.header("📋 現有人力資源規劃需求")
    df = pd.DataFrame(st.session_state.hrp_data)
    if df.empty:
        st.info("目前沒有任何規劃需求。")
        return
    years = sorted(df['year'].unique())
    filter_year = st.selectbox("按年度篩選", ["全部"] + years)
    if filter_year != "全部":
        df = df[df['year'] == int(filter_year)]
    st.dataframe(df)
    # 下載按鈕
    json_str = json.dumps(st.session_state.hrp_data, ensure_ascii=False, indent=2)
    st.download_button(
        label="Download HRP Data (JSON)",
        data=json_str,
        file_name="hrp_data.json",
        mime="application/json"
    )

def add_entry():
    st.header("🆕 新增人力資源規劃需求")
    with st.form("form_add", clear_on_submit=True):
        year = st.number_input("年度", 2023, 2030, 2025)
        department = st.text_input("部門")
        position = st.text_input("職位")
        demand_desc = st.text_area("人力需求描述")
        deadline = st.date_input("需求完成期限", min_value=date.today())
        notes = st.text_area("備註")
        calendar_note = st.text_area("日曆提醒內容", "請安排招聘會議")
        submit = st.form_submit_button("提交")
    if submit:
        if not demand_desc:
            st.error("需求描述不可為空。")
            return
        entry = {
            'id': str(uuid.uuid4()),
            'year': year,
            'department': department,
            'position': position,
            'demand': demand_desc,
            'deadline': deadline.strftime("%Y-%m-%d"),
            'notes': notes,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.hrp_data.append(entry)
        save_json(DATA_FILE, st.session_state.hrp_data)

        # 同步日曆提醒
        cal = {
            'entry_id': entry['id'],
            'date': deadline.strftime("%Y-%m-%d"),
            'note': calendar_note
        }
        st.session_state.hrp_calendar.append(cal)
        save_json(CALENDAR_FILE, st.session_state.hrp_calendar)

        log_action("新增需求", f"{entry['year']} {entry['department']} - {entry['position']}")
        st.success("新增成功，並已同步日曆提醒。")

def edit_entry():
    st.header("✏️ 修改人力資源規劃需求")
    options = {f"{e['year']} | {e['department']} - {e['position']}": e for e in st.session_state.hrp_data}
    if not options:
        st.info("無可編輯的需求。")
        return
    key = st.selectbox("選擇條目", list(options.keys()))
    entry = options[key]
    with st.form("form_edit"):
        year = st.number_input("年度", 2023, 2030, entry['year'])
        department = st.text_input("部門", entry['department'])
        position = st.text_input("職位", entry['position'])
        demand_desc = st.text_area("人力需求描述", entry['demand'])
        deadline = st.date_input("需求完成期限", datetime.strptime(entry['deadline'], "%Y-%m-%d"))
        notes = st.text_area("備註", entry.get('notes', ''))
        submit = st.form_submit_button("更新")
    if submit:
        entry.update({
            'year': year, 'department': department, 'position': position,
            'demand': demand_desc, 'deadline': deadline.strftime("%Y-%m-%d"), 'notes': notes,
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_json(DATA_FILE, st.session_state.hrp_data)
        log_action("修改需求", f"{entry['id']}")
        st.success("更新成功。")

def delete_entry():
    st.header("🗑️ 刪除人力資源規劃需求")
    options = {f"{e['year']} | {e['department']} - {e['position']}": e for e in st.session_state.hrp_data}
    if not options:
        st.info("無可刪除的需求。")
        return
    key = st.selectbox("選擇條目", list(options.keys()))
    entry = options[key]
    if st.button("確認刪除"):
        st.session_state.hrp_data = [e for e in st.session_state.hrp_data if e['id'] != entry['id']]
        st.session_state.hrp_calendar = [c for c in st.session_state.hrp_calendar if c['entry_id'] != entry['id']]
        save_json(DATA_FILE, st.session_state.hrp_data)
        save_json(CALENDAR_FILE, st.session_state.hrp_calendar)
        log_action("刪除需求", f"{entry['id']}")
        st.success("刪除成功。")

def batch_delete():
    st.subheader("🔁 批量刪除")
    if not st.session_state.hrp_data:
        st.info("無資料。")
        return
    selections = st.multiselect(
        "選擇要刪除的條目", st.session_state.hrp_data,
        format_func=lambda x: f"{x['year']} | {x['department']} - {x['position']}"
    )
    if st.button("執行批量刪除"):
        for entry in selections:
            st.session_state.hrp_data.remove(entry)
            st.session_state.hrp_calendar = [c for c in st.session_state.hrp_calendar if c['entry_id'] != entry['id']]
            log_action("批量刪除", f"{entry['id']}")
        save_json(DATA_FILE, st.session_state.hrp_data)
        save_json(CALENDAR_FILE, st.session_state.hrp_calendar)
        st.success("批量刪除完成。")


def view_logs():
    st.header("📜 操作日誌")
    df = pd.DataFrame(st.session_state.hrp_logs)
    if df.empty:
        st.info("無日誌。")
    else:
        st.dataframe(df)
        # 下載按鈕
        json_str = json.dumps(st.session_state.hrp_logs, ensure_ascii=False, indent=2)
        st.download_button(
            label="Download Logs (JSON)",
            data=json_str,
            file_name="hrp_logs.json",
            mime="application/json"
        )

def view_calendar():
    st.header("📅 規劃提醒日曆")
    cal = pd.DataFrame(st.session_state.hrp_calendar)
    if cal.empty:
        st.info("無提醒。")
    else:
        cal['date'] = pd.to_datetime(cal['date'])
        cal = cal.sort_values('date')
        st.dataframe(cal[['date', 'note']])
        # 下載按鈕
        json_str = json.dumps(st.session_state.hrp_calendar, ensure_ascii=False, indent=2)
        st.download_button(
            label="Download Calendar (JSON)",
            data=json_str,
            file_name="hrp_calendar.json",
            mime="application/json"
        )

def data_analysis():
    st.header("📊 數據分析儀表板")
    df = pd.DataFrame(st.session_state.hrp_data)
    if df.empty:
        st.info("無資料進行分析。")
        return
    st.subheader("年度需求分佈")
    fig, ax = plt.subplots()
    df['year'].value_counts().sort_index().plot(kind='bar', ax=ax)
    ax.set_xlabel("Year"); ax.set_ylabel("Count")
    st.pyplot(fig)

    st.subheader("部門需求排名")
    dept_counts = df['department'].value_counts().head(10)
    st.bar_chart(dept_counts)

    st.subheader("職位關鍵詞排行榜")
    word_freq = pd.Series(" ".join(df['demand']).split()).value_counts().head(10)
    st.table(word_freq)
    # 下載按鈕
    json_str = df.to_json(orient="records", force_ascii=False, indent=2)
    st.download_button(
        label="Download Analysis Data (JSON)",
        data=json_str,
        file_name="hrp_analysis.json",
        mime="application/json"
    )

# -------------------- 主入口：可供匯入 --------------------
def hrp_module():
    initialize_session_state()
    st.title("📌 HRP 模組 - ST Engineering")
    st.sidebar.title("功能選單")
    menu = [
        "查看需求", "新增需求", "修改需求", "刪除需求",
        "批量刪除", "查看日誌",
        "日曆提醒", "數據分析"
    ]
    choice = st.sidebar.radio("請選擇操作", menu)

    if choice == "查看需求": view_data()
    elif choice == "新增需求": add_entry()
    elif choice == "修改需求": edit_entry()
    elif choice == "刪除需求": delete_entry()
    elif choice == "批量刪除": batch_delete()

    elif choice == "查看日誌": view_logs()
    elif choice == "日曆提醒": view_calendar()
    elif choice == "數據分析": data_analysis()

# 可被 main.py 匯入
__all__ = ["hrp_module"]
