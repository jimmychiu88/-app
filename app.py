import streamlit as st
import json
import os
import datetime
import time

# --- 1. 頁面設定與 CSS/JS 特效 ---
st.set_page_config(page_title="Visable Care", page_icon="🏠", layout="centered")

st.markdown("""
<style>
    /* 調整主要區域的上方空白 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    /* 按鈕美化 */
    .stButton>button {
        border-radius: 20px;
        border: none;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
    }
    
    /* 定義震動動畫 (Screen Shake) */
    @keyframes shake {
      10%, 90% { transform: translate3d(-1px, 0, 0); }
      20%, 80% { transform: translate3d(2px, 0, 0); }
      30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
      40%, 60% { transform: translate3d(4px, 0, 0); }
    }
</style>
""", unsafe_allow_html=True)

# --- 資料庫處理 ---
DATA_FILE = 'data.json'

# 初始化預設資料 (已修正圖示與備註的對應邏輯)
default_data = {
    "points": 0,
    "history": [],
    "tasks": [
        {"name": "洗衣服", "points": 50, "icon": "👕", "note": "記得分深淺色"},
        {"name": "倒垃圾", "points": 30, "icon": "🗑️", "note": "包含回收"},
        {"name": "洗碗", "points": 40, "icon": "🍽️", "note": "瓦斯爐也要擦"},
    ],
    "rewards": [
        {"name": "週末睡到自然醒", "cost": 100, "icon": "💤", "note": "最晚到中午12點"},
        {"name": "吃美食", "cost": 200, "icon": "🍜", "note": "獎勵自己吃個好的"},
    ],
    "feedback": [
        {"name": "另一半", "msg": "今天的晚餐超好吃，辛苦了！❤️", "color": "#fff740", "date": "01/06"},
        {"name": "小寶", "msg": "謝謝你教我寫功課", "color": "#7afcff", "date": "01/06"},
    ]
}

def load_data():
    if not os.path.exists(DATA_FILE):
        return default_data
    try:
        data = json.load(open(DATA_FILE, 'r', encoding='utf-8'))
    except:
        return default_data
        
    if 'feedback' not in data: data['feedback'] = default_data['feedback']
    for t in data['tasks']:
        if 'note' not in t: t['note'] = ""
    for r in data['rewards']:
        if 'note' not in r: r['note'] = ""
    return data

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

# --- 側邊欄 ---
with st.sidebar:
    st.write("⚙️ 設定")
    if st.button("🔴 重置所有數據", help="清空所有分數和紀錄"):
        save_data(default_data)
        st.rerun()

# --- 主畫面 ---
st.title("🏡 Visable Care")
st.caption("讓家務價值被看見，努力都值得被肯定！")

col_score, col_bar = st.columns([1, 2])
with col_score:
    st.metric(label="目前愛心積分", value=f"{data['points']} pts")
with col_bar:
    st.write("累積成就感")
    st.progress(min(data['points'] / 1000, 1.0))

st.markdown("---")

# --- 主要功能區 ---
tab1, tab2, tab3, tab4 = st.tabs(["🎯 任務", "🎁 獎勵", "📜 歷史紀錄", "💌 家人留言板"])

# === Tab 1: 任務列表 ===
with tab1:
    st.subheader("今日待辦")
    if not data['tasks']: st.info("目前沒有任務")

    # 1. 先顯示列表
    for i, task in enumerate(data['tasks']):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([0.8, 3.5, 1.5, 0.8])
            with c1: st.markdown(f"### {task['icon']}")
            with c2: 
                st.markdown(f"**{task['name']}**")
                if task['note']: st.caption(f"📝 {task['note']}")
            with c3:
                st.write(f"**+{task['points']}**")
                if st.button("✅ 完成", key=f"do_{i}", use_container_width=True):
                    data['points'] += task['points']
                    log = {"type": "earn", "name": task['name'], "points": task['points'], "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
                    data['history'].insert(0, log)
                    save_data(data)
                    st.toast(f"獲得 {task['points']} 分！")
                    st.rerun()
            with c4:
                if st.button("🗑️", key=f"del_t_{i}"):
                    data['tasks'].pop(i)
                    save_data(data)
                    st.rerun()

    st.markdown("---")

    # 2. 新增功能移到最下面
    with st.expander("➕ 新增家務項目", expanded=False):
        c1, c2 = st.columns([3, 2])
        with c1: new_task_name = st.text_input("任務名稱", placeholder="ex: 倒垃圾")
        with c2: new_task_points = st.number_input("分數", 10, 100, 30)
        
        new_task_note = st.text_input("備註說明", placeholder="選填...", key="task_note_input")
        
        icon_mode = st.radio("圖示來源", ["預設", "Emoji"], horizontal=True, key="task_icon_mode")
        if icon_mode == "預設":
            new_task_icon = st.selectbox("圖示", ["🧹", "🍳", "🧺", "👶", "🐶", "🚙"], index=0, key="task_icon_select")
        else:
            new_task_icon = st.text_input("輸入 Emoji", value="🧹", max_chars=2, key="task_icon_text")

        if st.button("新增任務", key="btn_add_task"):
            if new_task_name:
                data['tasks'].append({"name": new_task_name, "points": new_task_points, "icon": new_task_icon, "note": new_task_note})
                save_data(data)
                st.success(f"已新增：{new_task_name}")
                st.rerun()

# === Tab 2: 獎勵列表 (修改為條列式 + 新增移到底部) ===
with tab2:
    st.subheader("犒賞自己")
    if not data['rewards']: st.info("目前沒有獎勵")

    # 1. 顯示列表 (改成跟任務一樣的條列式版面)
    for i, reward in enumerate(data['rewards']):
        with st.container(border=True):
            # 版面配置：圖示 | 名稱+備註 | 分數+兌換按鈕 | 刪除按鈕
            c1, c2, c3, c4 = st.columns([0.8, 3.5, 1.5, 0.8])
            
            with c1: st.markdown(f"### {reward['icon']}")
            
            with c2: 
                st.markdown(f"**{reward['name']}**")
                if reward['note']: st.caption(f"📝 {reward['note']}")
            
            with c3:
                st.write(f"需 **{reward['cost']}** 分")
                
                can_buy = data['points'] >= reward['cost']
                # 兌換按鈕
                if st.button("✨ 兌換", key=f"buy_{i}", disabled=not can_buy, type="primary" if can_buy else "secondary", use_container_width=True):
                    data['points'] -= reward['cost']
                    log = {"type": "spend", "name": reward['name'], "points": reward['cost'], "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
                    data['history'].insert(0, log)
                    save_data(data)
                    
                    st.markdown("""
                        <script>
                        if (navigator.vibrate) { navigator.vibrate([200, 50, 200]); }
                        document.body.style.animation = "shake 0.5s cubic-bezier(.36,.07,.19,.97) both";
                        </script>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                    st.success(f"兌換成功！")
                    time.sleep(1.5) 
                    st.rerun()
            
            with c4:
                if st.button("🗑️", key=f"del_r_{i}"):
                    data['rewards'].pop(i)
                    save_data(data)
                    st.rerun()

    st.markdown("---")

    # 2. 新增功能移到最下面
    with st.expander("➕ 新增願望", expanded=False):
        c1, c2 = st.columns([3, 2])
        with c1: new_reward_name = st.text_input("獎勵名稱", placeholder="ex: 看電影")
        with c2: new_reward_cost = st.number_input("所需分數", 50, 1000, 100)
        
        new_reward_note = st.text_input("備註說明", placeholder="選填...", key="reward_note_input")
        
        r_icon_mode = st.radio("圖示來源", ["預設", "Emoji"], horizontal=True, key="r_icon")
        if r_icon_mode == "預設":
            new_reward_icon = st.selectbox("圖示", ["🎁", "💆‍♀️", "☕", "🎟️", "✈️"], index=0, key="r_icon_sel")
        else:
            new_reward_icon = st.text_input("輸入 Emoji", value="🎁", max_chars=2, key="cust_r")

        if st.button("新增願望", key="btn_add_reward"):
            if new_reward_name:
                data['rewards'].append({"name": new_reward_name, "cost": new_reward_cost, "icon": new_reward_icon, "note": new_reward_note})
                save_data(data)
                st.success(f"已新增：{new_reward_name}")
                st.rerun()

# === Tab 3: 歷史紀錄 ===
with tab3:
    c1, c2 = st.columns([4, 1])
    with c1: st.write("近期動態：")
    with c2: 
        if st.button("清除紀錄"):
            data['history'] = []
            save_data(data)
            st.rerun()

    if not data['history']: st.caption("暫無紀錄")
    
    for item in data['history']:
        if isinstance(item, str):
            st.text(f"• {item}")
        else:
            if item['type'] == 'earn':
                bg, border, text, icon, sign = "#e8f5e9", "#c3e6cb", "#2e7d32", "📥", "+"
            else:
                bg, border, text, icon, sign = "#ffebee", "#f5c6cb", "#c62828", "🎁", "-"
            
            st.markdown(f"""
            <div style="background-color: {bg}; border: 1px solid {border}; padding: 12px; border-radius: 12px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center;">
                    <div style="font-size: 24px; margin-right: 12px;">{icon}</div>
                    <div>
                        <div style="font-weight: bold; color: #333; font-size: 16px;">{item['name']}</div>
                        <div style="font-size: 12px; color: #888;">{item['date']}</div>
                    </div>
                </div>
                <div style="font-weight: bold; font-size: 20px; color: {text};">{sign}{item['points']}</div>
            </div>
            """, unsafe_allow_html=True)

# === Tab 4: 家人留言板 (補回快速配色按鈕) ===
with tab4:
    st.subheader("💌 給家人的悄悄話")
    st.caption("不管多忙，記得留張便利貼說聲謝謝。")

    with st.expander("✏️ 寫一張新便利貼", expanded=False):
        c1, c2 = st.columns([1, 2])
        with c1:
            note_name = st.text_input("我是...", placeholder="簽個名吧", key="note_who")
            
            # 補回顏色選擇器與快速按鈕
            note_color = st.color_picker("選擇便利貼顏色", "#fff740", key="note_color_picker")
            
        with c2:
            note_msg = st.text_area("想說的話...", placeholder="晚餐超好吃！愛你喔～", key="note_content")
        
        if st.button("貼上去", key="btn_post_note"):
            if note_msg and note_name:
                data['feedback'].append({
                    "name": note_name,
                    "msg": note_msg,
                    "color": note_color,
                    "date": datetime.datetime.now().strftime("%m/%d")
                })
                save_data(data)
                st.success("留言成功！")
                st.rerun()
            elif not note_name:
                st.error("請記得簽名喔！")

    st.markdown("---")
    
    if not data['feedback']: st.info("快來貼第一張便利貼！")
    
    cols = st.columns(2)
    for i, note in enumerate(data['feedback']):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="
                background-color: {note['color']};
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 3px 3px 5px rgba(0,0,0,0.2);
                font-family: 'Comic Sans MS', 'Microsoft JhengHei', sans-serif;
                color: #333;
                transform: rotate({(i % 3 - 1)}deg);
            ">
                <div style="font-weight: bold; font-size: 1.1em; margin-bottom: 5px;">
                    📌 {note['name']} 
                    <span style="font-size: 0.7em; color: #666; float: right;">{note.get('date', '')}</span>
                </div>
                <div style="font-size: 1.2em; line-height: 1.4;">
                    {note['msg']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("撕掉", key=f"del_note_{i}"):
                data['feedback'].pop(i)
                save_data(data)
                st.rerun()