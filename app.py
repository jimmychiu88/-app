import streamlit as st
import json
import os
import datetime

# --- 設定頁面樣式 ---
st.set_page_config(page_title="家庭互助獎勵 App", page_icon="🏠", layout="centered")

# --- 資料庫處理 (使用簡單的 JSON 檔案模擬) ---
DATA_FILE = 'data.json'

# 初始化預設資料
default_data = {
    "points": 0,
    "history": [],  # 歷史紀錄
    "tasks": [
        {"name": "完成全家晚餐烹飪", "points": 50, "icon": "🍳"},
        {"name": "清洗浴室", "points": 30, "icon": "🛁"},
        {"name": "陪伴小孩寫功課 1小時", "points": 40, "icon": "📚"},
    ],
    "rewards": [
        {"name": "週末睡到自然醒券", "cost": 100, "icon": "💤"},
        {"name": "老公負責全天小孩", "cost": 200, "icon": "👶"},
        {"name": "購買 3000 元以內保養品", "cost": 500, "icon": "💄"},
    ]
}

def load_data():
    if not os.path.exists(DATA_FILE):
        return default_data
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 載入資料
data = load_data()

# --- 側邊欄：角色切換 ---
st.sidebar.title("👤 角色登入")
role = st.sidebar.radio("請選擇你的身份：", ["使用者", "管理員"])

st.sidebar.markdown("---")
if st.sidebar.button("重置所有數據 (Demo用)"):
    save_data(default_data)
    st.rerun()

# --- 主頁面邏輯 ---

if role == "使用者":
    st.title("💖 今天也是閃閃發亮的一天！")
    
    # 1. 顯示目前積分 (儀表板)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header(f"目前愛心積分： {data['points']} pts")
    with col2:
        st.write("累積成就感")
        st.progress(min(data['points'] / 1000, 1.0)) # 假設1000分是滿條

    st.markdown("---")

    # 2. 任務區 (賺取積分)
    st.subheader("📝 每日任務清單")
    st.caption("完成任務，獲得家人給予的愛心回饋")
    
    for i, task in enumerate(data['tasks']):
        col_t1, col_t2, col_t3 = st.columns([1, 3, 1])
        with col_t1:
            st.markdown(f"### {task['icon']}")
        with col_t2:
            st.write(f"**{task['name']}**")
            st.caption(f"+ {task['points']} 積分")
        with col_t3:
            if st.button("完成", key=f"task_{i}"):
                data['points'] += task['points']
                # 紀錄 Log
                log = f"{datetime.date.today()} - 完成任務：{task['name']} (+{task['points']})"
                data['history'].insert(0, log)
                save_data(data)
                st.toast(f"好棒！獲得 {task['points']} 分！🎉")
                st.rerun()

    st.markdown("---")

    # 3. 獎勵區 (兌換積分)
    st.subheader("🎁 獎勵兌換區")
    st.caption("這是你應得的寵愛")
    
    # 使用 container 讓排版漂亮一點
    cols = st.columns(2)
    for i, reward in enumerate(data['rewards']):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"#### {reward['icon']} {reward['name']}")
                st.write(f"所需積分: **{reward['cost']}**")
                
                if st.button(f"兌換", key=f"reward_{i}", type="primary" if data['points'] >= reward['cost'] else "secondary"):
                    if data['points'] >= reward['cost']:
                        data['points'] -= reward['cost']
                        log = f"{datetime.date.today()} - 兌換獎勵：{reward['name']} (-{reward['cost']})"
                        data['history'].insert(0, log)
                        save_data(data)
                        st.balloons() # 放氣球特效
                        st.success(f"兌換成功！請找家人履行承諾：{reward['name']}")
                        st.rerun()
                    else:
                        st.error("積分不足，加油！")

elif role == "管理員":
    st.title("🛠️ 家人後台管理系統")
    st.info("在這裡設定任務與獎勵，讓家務價值被看見。")

    # 1. 新增任務
    with st.expander("➕ 新增家務任務", expanded=True):
        new_task_name = st.text_input("任務名稱 (例如：倒垃圾)")
        new_task_points = st.number_input("設定分數", min_value=10, step=10, value=50)
        new_task_icon = st.selectbox("選擇圖示", ["🧹", "🍳", "🧺", "👶", "🐶", "🚙"])
        
        if st.button("新增任務"):
            if new_task_name:
                data['tasks'].append({"name": new_task_name, "points": new_task_points, "icon": new_task_icon})
                save_data(data)
                st.success(f"已新增任務：{new_task_name}")
                st.rerun()

    # 2. 新增獎勵
    with st.expander("🎁 設定獎勵內容 (Brainstorming 重點)", expanded=True):
        st.write("根據之前的 KJ 法，這裡可以設定一些「非物質」的獎勵，如自由時間。")
        new_reward_name = st.text_input("獎勵名稱 (例如：一整天不被打擾)")
        new_reward_cost = st.number_input("兌換所需分數", min_value=50, step=50, value=200)
        new_reward_icon = st.selectbox("獎勵圖示", ["💆‍♀️", "☕", "🎟️", "✈️", "🎮", "💤"])
        
        if st.button("新增獎勵"):
            if new_reward_name:
                data['rewards'].append({"name": new_reward_name, "cost": new_reward_cost, "icon": new_reward_icon})
                save_data(data)
                st.success(f"已新增獎勵：{new_reward_name}")
                st.rerun()

    # 3. 查看兌換紀錄
    st.subheader("📜 積分流動紀錄")
    for log in data['history']:
        st.text(log)