# training.py — 完整增強版 T&D 模組，包含持久化、日誌與美化及6項創意功能
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
import json
import os
import uuid

DATA_FILE = "td_data.json"
LOG_FILE = "td_logs.json"
ATTEND_FILE = "td_attendance.json"
CERT_FILE = "td_certificates.json"

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
    st.session_state.setdefault('trainings', load_json(DATA_FILE))
    st.session_state.setdefault('td_logs', load_json(LOG_FILE))
    st.session_state.setdefault('attendance', load_json(ATTEND_FILE))
    st.session_state.setdefault('certificates', load_json(CERT_FILE))
    st.session_state.setdefault('last_updated', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# -------------------- 日誌記錄 --------------------
def log_action(action, details):
    entry = {
        'id': str(uuid.uuid4()),
        'action': action,
        'details': details,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.td_logs.append(entry)
    save_json(LOG_FILE, st.session_state.td_logs)

# -------------------- 基本 CRUD --------------------
def view_trainings():
    st.header("📋 訓練課程列表")
    st.write(f"最後更新：{st.session_state.last_updated}")
    df = pd.DataFrame(st.session_state.trainings)
    if df.empty:
        st.info("目前沒有訓練課程。")
    else:
        # 搜尋課程
        kw = st.text_input("🔍 搜尋課程")
        if kw:
            df = df[df['course'].str.contains(kw, case=False)]
        st.dataframe(df)

def add_training():
    st.header("🆕 新增訓練課程")
    with st.form("form_add"):
        course = st.text_input("課程名稱")
        desc = st.text_area("課程描述")
        duration = st.number_input("持續時長(小時)", 1, 8, 2)
        start_date = st.date_input("開始日期", date.today())
        rating = st.slider("預期滿意度(1-5)", 1, 5, 3)
        submit = st.form_submit_button("提交")
    if submit:
        if not course.strip():
            st.error("課程名稱不可為空")
        else:
            entry = {
                'id': str(uuid.uuid4()),
                'course': course,
                'description': desc,
                'duration': duration,
                'start_date': start_date.strftime("%Y-%m-%d"),
                'expected_rating': rating,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.trainings.append(entry)
            save_json(DATA_FILE, st.session_state.trainings)
            log_action("新增課程", course)
            st.success("訓練課程新增成功！")

def edit_training():
    st.header("✏️ 修改訓練課程")
    if not st.session_state.trainings:
        st.info("無可修改課程")
        return
    opts = {t['course']: t for t in st.session_state.trainings}
    sel = st.selectbox("選擇課程", list(opts.keys()))
    tr = opts[sel]
    with st.form("form_edit"):
        course = st.text_input("課程名稱", tr['course'])
        desc = st.text_area("課程描述", tr['description'])
        duration = st.number_input("持續時長(小時)", 1, 8, tr['duration'])
        start_date = st.date_input("開始日期", datetime.strptime(tr['start_date'], "%Y-%m-%d"))
        rating = st.slider("預期滿意度(1-5)", 1, 5, tr['expected_rating'])
        submit = st.form_submit_button("更新")
    if submit:
        tr.update({
            'course': course, 'description': desc, 'duration': duration,
            'start_date': start_date.strftime("%Y-%m-%d"), 'expected_rating': rating,
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_json(DATA_FILE, st.session_state.trainings)
        log_action("更新課程", course)
        st.success("課程更新成功！")

def delete_training():
    st.header("🗑️ 刪除訓練課程")
    if not st.session_state.trainings:
        st.info("無可刪除課程")
        return
    opts = {t['course']: t for t in st.session_state.trainings}
    sel = st.selectbox("選擇課程", list(opts.keys()))
    if st.button("確認刪除"):
        st.session_state.trainings = [t for t in st.session_state.trainings if t['id'] != opts[sel]['id']]
        save_json(DATA_FILE, st.session_state.trainings)
        log_action("刪除課程", sel)
        st.success("課程刪除成功！")

# -------------------- 創意功能 --------------------
def batch_delete():
    st.subheader("🔁 批量刪除課程")
    df = pd.DataFrame(st.session_state.trainings)
    if df.empty:
        st.info("無課程可批次刪除")
        return
    sels = st.multiselect("選擇要刪除的課程", df['course'])
    if st.button("執行批次刪除"):
        for c in sels:
            st.session_state.trainings = [t for t in st.session_state.trainings if t['course'] != c]
            log_action("批次刪除", c)
        save_json(DATA_FILE, st.session_state.trainings)
        st.success("批次刪除完成！")

def import_data():
    st.subheader("📂 導入課程資料(JSON)")
    up = st.file_uploader("上傳 JSON", type=["json"])
    if up:
        data = json.load(up)
        if isinstance(data, list):
            st.session_state.trainings.extend(data)
            save_json(DATA_FILE, st.session_state.trainings)
            log_action("導入資料", f"{len(data)} 條")
            st.success("導入成功！")
        else:
            st.error("格式錯誤！")

def view_logs():
    st.subheader("📜 操作日誌")
    df = pd.DataFrame(st.session_state.td_logs)
    if df.empty:
        st.info("無日誌")
    else:
        st.dataframe(df)
        # 新增下載按鈕
        json_str = json.dumps(st.session_state.td_logs, ensure_ascii=False, indent=2)
        st.download_button(
            label="Download Logs (JSON)",
            data=json_str,
            file_name="td_logs.json",
            mime="application/json"
        )

def schedule_session():
    st.subheader("📅 安排培訓場次")
    if not st.session_state.trainings:
        st.info("請先新增課程")
        return
    opts = {t['course']: t['id'] for t in st.session_state.trainings}
    sel = st.selectbox("選擇課程", list(opts.keys()))
    with st.form("form_sched"):
        date_input = st.date_input("場次日期", date.today())
        venue = st.text_input("地點", "公司教室")
        submit = st.form_submit_button("安排")
    if submit:
        entry = {'id': str(uuid.uuid4()), 'course_id': opts[sel], 'date': date_input.strftime("%Y-%m-%d"), 'venue': venue}
        st.session_state.attendance.append(entry)
        save_json(ATTEND_FILE, st.session_state.attendance)
        log_action("安排場次", sel)
        st.success("場次安排成功！")

def mark_attendance():
    st.subheader("✅ 標記出席")
    if not st.session_state.attendance:
        st.info("無場次可標記")
        return
    df = pd.DataFrame(st.session_state.attendance)
    df = df.merge(pd.DataFrame(st.session_state.trainings), left_on='course_id', right_on='id', suffixes=('','_t'))
    df['label'] = df['course'] + ' @ ' + df['date']
    opts = {r['label']: r['id'] for _, r in df.iterrows()}
    sel = st.selectbox("選擇場次", list(opts.keys()))
    if st.button("標記所有候選人出席"):
        # 就範例，標記簡單日誌
        log_action("出席標記", sel)
        st.success("已標記所有候選人出席！")

def generate_certificate():
    st.subheader("🎓 生成結業證書")
    if not st.session_state.trainings:
        st.info("請先新增課程")
        return
    opts = {t['course']: t['id'] for t in st.session_state.trainings}
    sel = st.selectbox("選擇課程", list(opts.keys()))
    name = st.text_input("員工姓名")
    if st.button("生成證書"):
        cert = {'id': str(uuid.uuid4()), 'course_id': opts[sel], 'name': name, 'date': datetime.now().strftime("%Y-%m-%d")}
        st.session_state.certificates.append(cert)
        save_json(CERT_FILE, st.session_state.certificates)
        log_action("生成證書", f"{name} - {sel}")
        st.success("結業證書已生成！")
    # 新增下載按鈕
    if st.session_state.certificates:
        json_str = json.dumps(st.session_state.certificates, ensure_ascii=False, indent=2)
        st.download_button(
            label="Download Certificates (JSON)",
            data=json_str,
            file_name="td_certificates.json",
            mime="application/json"
        )

def analytics():
    st.subheader("📊 課程分析儀表板")
    df = pd.DataFrame(st.session_state.trainings)
    if df.empty:
        st.info("無資料分析")
        return
    # 課程數量走勢
    df['created_at'] = pd.to_datetime(df['created_at'])
    count_by_month = df.groupby(df['created_at'].dt.to_period('M')).size()
    st.line_chart(count_by_month)
    # 新增下載按鈕
    json_str = df.to_json(orient="records", force_ascii=False, indent=2)
    st.download_button(
        label="Download Training Data (JSON)",
        data=json_str,
        file_name="td_trainings.json",
        mime="application/json"
    )

# -------------------- 主入口 --------------------
def td_module():
    initialize_session_state()
    st.title("📌 訓練與發展 (T&D) - ST Engineering")
    st.sidebar.title("功能選單")
    choice = st.sidebar.radio("請選擇操作", [
        "查看課程", "新增課程", "修改課程", "刪除課程",
        "批量刪除", "導入資料", "日誌紀錄",
        "安排場次", "標記出席", "生成證書", "課程分析"
    ])

    if choice == "查看課程": view_trainings()
    elif choice == "新增課程": add_training()
    elif choice == "修改課程": edit_training()
    elif choice == "刪除課程": delete_training()
    elif choice == "批量刪除": batch_delete()
    elif choice == "導入資料": import_data()
    elif choice == "日誌紀錄": view_logs()
    elif choice == "安排場次": schedule_session()
    elif choice == "標記出席": mark_attendance()
    elif choice == "生成證書": generate_certificate()
    elif choice == "課程分析": analytics()

# 供 main.py 匯入
__all__ = ["td_module"]
