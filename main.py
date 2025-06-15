# main.py
import streamlit as st
from hr_planning import hrp_module
from recruitment import rs_module
from training import td_module
from performance import kpi_module
from compensation import cb_module
from employee_relations import er_module

# 設定頁面屬性
st.set_page_config(page_title="HR Management System", layout="wide")

# 自訂 CSS：調整整體樣式、下拉選單的各項色彩、滑鼠懸停特效，及右側色彩裝飾
custom_css = """
<style>
/* 整體背景與字型 */
body {
    background: linear-gradient(135deg, #fdfbfb, #ebedee);
    font-family: 'Helvetica Neue', Arial, sans-serif;
}

/* 主標題美化 */
h1 {
    color: #2c3e50;
    text-shadow: 2px 2px 6px #bdc3c7;
    text-align: center;
}

/* 側邊欄背景 */
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #85FFBD, #FFFB7D);
}

/* 調整下拉選單容器 */
[data-baseweb="select"] {
    position: relative;
    background: #ffffff;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding-right: 35px; /* 為右側的色彩條留空間 */
}

/* 下拉選單右側裝飾色條 */
[data-baseweb="select"]::after {
    content: "";
    position: absolute;
    right: 0;
    top: 0;
    width: 10px;
    height: 100%;
    background: linear-gradient(180deg, #ff9a9e, #fad0c4);
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}

/* 為下拉選項設定顏色（假設選單展開後的選項使用 role="option" 標籤） */
div[role="option"]:nth-child(1) {
    background-color: #ffcccc !important;
}
div[role="option"]:nth-child(2) {
    background-color: #ccffcc !important;
}
div[role="option"]:nth-child(3) {
    background-color: #ccccff !important;
}
div[role="option"]:nth-child(4) {
    background-color: #fffacc !important;
}
div[role="option"]:nth-child(5) {
    background-color: #ccfaff !important;
}
div[role="option"]:nth-child(6) {
    background-color: #f0ccff !important;
}

/* 滑鼠移動到選項時的效果 */
div[role="option"]:hover {
    filter: brightness(90%);
    cursor: pointer;
}

/* 假如有使用按鈕也做點美化 */
.stButton > button {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    font-size: 1em;
    transition: background-color 0.3s;
}
.stButton > button:hover {
    background-color: #2980b9;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 主標題
st.title("新加坡科技工程有限公司 人力資源管理系統")

# 側邊欄下拉選單（模組選擇）
menu = ["人力資源規劃", "招募與遴選", "訓練與發展", "績效管理", "薪酬與福利", "員工關係"]
choice = st.sidebar.selectbox("選擇模組", menu)

# 根據選擇載入對應模組
if choice == "人力資源規劃":
    hrp_module()
elif choice == "招募與遴選":
    rs_module()
elif choice == "訓練與發展":
    td_module()
elif choice == "績效管理":
    kpi_module()
elif choice == "薪酬與福利":
    cb_module()
elif choice == "員工關係":
    er_module()