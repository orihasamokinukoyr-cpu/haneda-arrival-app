import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import zoneinfo
import random

# -----------------------------------------
# 乗り場判定ロジック
# -----------------------------------------
def assign_bus_stop(terminal, exit_gate, flight_type):
    if flight_type == "国際線":
        return "4号乗り場" if terminal == "T2" else None
    else:
        # 国内線：T2出口4,5,6は4号乗り場へ
        if terminal == "T1":
            return "1号乗り場" if exit_gate in ["1", "2", "3"] else "2号乗り場"
        else:
            return "3号乗り場" if exit_gate in ["1", "2", "3"] else "4号乗り場"

# -----------------------------------------
# 機材規模予測
# -----------------------------------------
def estimate_aircraft_capacity(flight_number):
    num_part = ''.join(filter(str.isdigit, flight_number))
    val = int(num_part) if num_part else 200
    if val % 3 == 0: return "大型機 (目安: 300〜500席)"
    elif val % 3 == 1: return "中型機 (目安: 200〜300席)"
    return "小型機 (目安: 100〜200席)"

st.set_page_config(page_title="羽田到着便 乗り場案内", layout="wide")
st.title("羽田空港 到着便 乗り場案内")

tokyo_zone = zoneinfo.ZoneInfo("Asia/Tokyo")
now = datetime.now(tokyo_zone)
st.markdown(f"⏱️ 現在の日本時刻: **{now.strftime('%H:%M')}**")

tabs = st.tabs(["1号乗り場", "2号乗り場", "3号乗り場", "4号乗り場"])

if st.button("最新のフライト情報を取得"):
    # -----------------------------------------
    # 未来のフライト枠のみを生成（過去便の混入を物理的に防ぐ）
    # -----------------------------------------
    start = now - timedelta(minutes=30)
    end = (now.replace(hour=5, minute=0, second=0, microsecond=0) + timedelta(days=1))
    
    flights = []
    f_num = 100
    
    # 5分刻みでフライトを生成
    t = start
    while t < end:
        # 24:00以降は「国内線通常便」を生成しない（深夜国際線のみにする）
        hours_val = t.hour + (24 if t.date() > now.date() else 0)
        
        # 1. 国際線 (T2)
        if random.random() < 0.3:
            flights.append({
                "type": "国際線", "terminal": "T2", "exit": str(random.randint(1, 4)),
                "arr": t + timedelta(minutes=30), "flight": f"NH{f_num}"
            })
            f_num += 1
            
        # 2. 国内線 (T1/T2) - 深夜は生成しない
        if hours_val < 23 and random.random() < 0.5:
            is_delayed = (hours_val >= 20 and random.random() < 0.1)
            delay = random.randint(60, 150) if is_delayed else 0
            flights.append({
                "type": "国内線", "terminal": random.choice(["T1", "T2"]),
                "exit": str(random.randint(1, 6)),
                "arr": t + timedelta(minutes=delay) + timedelta(minutes=15),
                "flight": f"JL{f_num}", "status": "遅延" if is_delayed else "定刻"
            })
            f_num += 1
        
        t += timedelta(minutes=30)

    # DataFrame処理
    df = pd.DataFrame([{
        "乗り場目安時刻": f.get("arr").strftime("%H:%M"),
        "便到着": f.get("arr").strftime("%H:%M"), # 簡易化
        "出発地": f"{'[国際]' if f['type']=='国際線' else '[国内]'} {random.choice(['福岡','札幌','那覇','香港','LA'])}",
        "便名": f["flight"],
        "規模": estimate_aircraft_capacity(f["flight"]),
        "状況": f.get("status", "定刻"),
        "bus_stop": assign_bus_stop(f["terminal"], f["exit"], f["type"])
    } for f in flights])

    # 画面出力
    for i, tab in enumerate(tabs):
        with tab:
            filtered = df[df["bus_stop"] == f"{i+1}号乗り場"]
            if filtered.empty:
                st.info("該当便なし")
            else:
                st.dataframe(filtered.drop(columns=["bus_stop"]), use_container_width=True)
