#main.py
import streamlit as st
from hr_planning import hrp_module
from recruitment import rs_module
from training import td_module
from performance import kpi_module
from compensation import cb_module
from employee_relations import er_module

st.set_page_config(page_title="HR Management System", layout="wide")

st.title("新加坡科技工程有限公司 人力資源管理系統")

menu = ["人力資源規劃", "招募與遴選", "訓練與發展", "績效管理", "薪酬與福利", "員工關係"]
choice = st.sidebar.selectbox("選擇模組", menu)

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
