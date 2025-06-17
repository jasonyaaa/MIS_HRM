
# recruitment.py — 完整增強版 R&S 模組，包含持久化、日誌與美化，並加入創意功能
import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import os
import uuid

DATA_FILE = "rs_data.json"
LOG_FILE = "rs_logs.json"
INTERVIEW_FILE = "rs_interviews.json"

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
    if 'candidates' not in st.session_state:
        st.session_state.candidates = load_json(DATA_FILE)
    if 'rs_logs' not in st.session_state:
        st.session_state.rs_logs = load_json(LOG_FILE)
    if 'interviews' not in st.session_state:
        st.session_state.interviews = load_json(INTERVIEW_FILE)
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
    st.session_state.rs_logs.append(entry)
    save_json(LOG_FILE, st.session_state.rs_logs)

# -------------------- 功能模組 --------------------
def view_candidates():
    st.header("📋 候選人名單")
    st.write(f"最後更新：{st.session_state.last_updated}")
    df = pd.DataFrame(st.session_state.candidates)
    if df.empty:
        st.info("目前沒有候選人。")
        return
    # 搜尋功能
    keyword = st.text_input("🔍 搜尋候選人 (姓名或職位)")
    if keyword:
        df = df[df['name'].str.contains(keyword, case=False) |
               df['position'].str.contains(keyword, case=False)]
    st.dataframe(df)
    # 下載按鈕
    json_str = json.dumps(st.session_state.candidates, ensure_ascii=False, indent=2)
    st.download_button(
        label="Download Candidates (JSON)",
        data=json_str,
        file_name="candidates.json",
        mime="application/json"
    )

def add_candidate():
    st.header("🆕 新增候選人")
    with st.form("form_add"):
        name = st.text_input("姓名")
        position = st.text_input("應徵職位")
        resume = st.text_area("簡歷內容")
        rating = st.slider("初步評分 (1-5)", 1, 5, 3)
        submit = st.form_submit_button("提交")
    if submit:
        if not name.strip() or not position.strip():
            st.error("姓名和職位不可為空。")
        else:
            entry = {
                'id': str(uuid.uuid4()),
                'name': name,
                'position': position,
                'resume': resume,
                'rating': rating,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.candidates.append(entry)
            save_json(DATA_FILE, st.session_state.candidates)
            log_action("新增候選人", f"{name} - {position}")
            st.success("已成功新增候選人！")

def edit_candidate():
    st.header("✏️ 修改候選人")
    if not st.session_state.candidates:
        st.info("無可修改的候選人。")
        return
    options = {f"{c['name']} - {c['position']}": c for c in st.session_state.candidates}
    key = st.selectbox("選擇候選人", list(options.keys()))
    candidate = options[key]
    with st.form("form_edit"):
        name = st.text_input("姓名", candidate['name'])
        position = st.text_input("應徵職位", candidate['position'])
        resume = st.text_area("簡歷內容", candidate['resume'])
        rating = st.slider("評分 (1-5)", 1, 5, candidate.get('rating', 3))
        submit = st.form_submit_button("更新")
    if submit:
        candidate.update({
            'name': name,
            'position': position,
            'resume': resume,
            'rating': rating,
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_json(DATA_FILE, st.session_state.candidates)
        log_action("修改候選人", f"{name} - {position}")
        st.success("已成功更新候選人！")

def delete_candidate():
    st.header("🗑️ 刪除候選人")
    if not st.session_state.candidates:
        st.info("無可刪除的候選人。")
        return
    options = {f"{c['name']} - {c['position']}": c for c in st.session_state.candidates}
    key = st.selectbox("選擇候選人", list(options.keys()))
    candidate = options[key]
    if st.button("確認刪除"):
        st.session_state.candidates = [c for c in st.session_state.candidates if c['id'] != candidate['id']]
        save_json(DATA_FILE, st.session_state.candidates)
        log_action("刪除候選人", f"{candidate['name']} - {candidate['position']}")
        st.success("已成功刪除候選人！")

def schedule_interview():
    st.header("📆 安排面試")
    if not st.session_state.candidates:
        st.info("請先新增候選人。")
        return
    options = {f"{c['name']} - {c['position']}": c['id'] for c in st.session_state.candidates}
    sel = st.selectbox("選擇候選人", list(options.keys()))
    cand_id = options[sel]
    with st.form("form_interview"):
        date_input = st.date_input("面試日期", date.today())
        time = st.text_input("面試時間", "09:00")
        location = st.text_input("地點", "總部會議室")
        submit = st.form_submit_button("安排")
    if submit:
        iv = {
            'id': str(uuid.uuid4()),
            'candidate_id': cand_id,
            'datetime': f"{date_input} {time}",
            'location': location
        }
        st.session_state.interviews.append(iv)
        save_json(INTERVIEW_FILE, st.session_state.interviews)
        log_action("安排面試", f"{sel} on {iv['datetime']}")
        st.success("面試已安排！")

def view_interviews():
    st.header("📅 面試日程")
    df = pd.DataFrame(st.session_state.interviews)
    if df.empty:
        st.info("目前無面試安排。")
    else:
        st.dataframe(df)
        # 下載按鈕
        json_str = json.dumps(st.session_state.interviews, ensure_ascii=False, indent=2)
        st.download_button(
            label="Download Interviews (JSON)",
            data=json_str,
            file_name="interviews.json",
            mime="application/json"
        )

def view_logs():
    st.header("📜 操作日誌")
    df = pd.DataFrame(st.session_state.rs_logs)
    if df.empty:
        st.info("無日誌記錄。")
    else:
        st.dataframe(df)
        # 下載按鈕
        json_str = json.dumps(st.session_state.rs_logs, ensure_ascii=False, indent=2)
        st.download_button(
            label="Download Logs (JSON)",
            data=json_str,
            file_name="rs_logs.json",
            mime="application/json"
        )

# 創意功能：統計資訊
def analytics():
    st.header("📊 候選人分析")
    df = pd.DataFrame(st.session_state.candidates)
    if df.empty:
        st.info("無資料分析。")
        return
    # 平均評分
    avg_rating = df['rating'].mean()
    st.metric("平均評分", f"{avg_rating:.1f}")
    # 職位分佈
    st.subheader("職位需求分佈")
    st.bar_chart(df['position'].value_counts())
    # 下載按鈕
    json_str = df.to_json(orient="records", force_ascii=False, indent=2)
    st.download_button(
        label="Download Analysis Data (JSON)",
        data=json_str,
        file_name="candidates_analysis.json",
        mime="application/json"
    )

# -------------------- 主入口 --------------------
def rs_module():
    initialize_session_state()
    st.title("📌 招募與遴選 (R&S) - ST Engineering")
    st.sidebar.title("功能選單")
    choice = st.sidebar.radio("請選擇操作", [
        "查看候選人", "新增候選人", "修改候選人", "刪除候選人",
        "安排面試", "查看面試", "候選人分析", "查看日誌"
    ])

    if choice == "查看候選人": view_candidates()
    elif choice == "新增候選人": add_candidate()
    elif choice == "修改候選人": edit_candidate()
    elif choice == "刪除候選人": delete_candidate()
    elif choice == "安排面試": schedule_interview()
    elif choice == "查看面試": view_interviews()
    elif choice == "候選人分析": analytics()
    elif choice == "查看日誌": view_logs()

# 供 main.py 匯入
__all__ = ["rs_module"]
