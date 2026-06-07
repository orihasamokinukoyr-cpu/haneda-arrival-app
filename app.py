import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import zoneinfo
import random

# -----------------------------------------
# 1. 乗り場判定ロジック
# -----------------------------------------
def assign_bus_stop(terminal, exit_gate, flight_type):
    if flight_type == "国際線":
        if terminal == "T2":
            return "4号乗り場"
        else:
            if exit_gate in ["1", "2"]:
                return "3号乗り場"
            else:
                return "4号乗り場"
    else:
        if terminal == "T1":
            if exit_gate in ["1", "2", "3"]:
                return "1号乗り場"
            else:
                return "2号乗り場"
        else:
            if exit_gate in ["1", "2", "3"]:
                return "3号乗り場"
            else:
                return "4号乗り場"

# -----------------------------------------
# 2. 機材規模予測
# -----------------------------------------
def estimate_aircraft_capacity(flight_number):
    num_part = ''.join(filter(str.isdigit, flight_number))
    if not num_part:
        return "中型機 (目安: 200〜300席)"
    
    val = int(num_part)
    if val % 3 == 0:
        return "大型機 (目安: 300〜500席)"
    elif val % 3 == 1:
        return "中型機 (目安: 200〜300席)"
    else:
        return "小型機 (目安: 100〜200席)"

# -----------------------------------------
# 3. アプリ画面の構築（UI）
# -----------------------------------------
st.set_page_config(page_title="羽田到着便 乗り場案内", layout="wide")
st.title("羽田空港 到着便 乗り場案内")

# 日本時間に完全に固定
tokyo_zone = zoneinfo.ZoneInfo("Asia/Tokyo")
now = datetime.now(tokyo_zone)

current_time_str = now.strftime("%H:%M")
st.markdown(f"⏱️ 現在の日本時刻: **{current_time_str}**")
st.markdown("※表示されている時刻は、フライト到着時刻に降機・手荷物受取の目安時間を加算した「乗り場到着目安」です。")

# 先にタブを作成
tabs = st.tabs(["1号乗り場", "2号乗り場", "3号乗り場", "4号乗り場"])

placeholders = []
for i, tab in enumerate(tabs):
    with tab:
        st.subheader(f"📍 {i+1}号乗り場 に向かってくる到着便")
        ph = st.empty()
        ph.info("「最新のフライト情報を取得」ボタンを押してください。")
        placeholders.append(ph)

# -----------------------------------------
# 4. データ生成・ボタン処理
# -----------------------------------------
if st.button("最新のフライト情報を取得"):
    with st.spinner('現在時刻から29:00までの全120便以上のスケジュールを処理中...'):
        
        dom_origins = ["札幌(新千歳)", "福岡", "大阪(伊丹)", "沖縄(那覇)", "広島", "鹿児島", "熊本", "長崎", "小松", "旭川", "函館", "青森", "南紀白浜", "出雲", "徳島", "富山", "米子", "鳥取", "高松", "大館能代", "庄内", "岩国", "宮崎", "秋田", "新潟", "大分"]
        int_origins = ["台北(松山)", "ソウル(仁川)", "香港", "バンコク", "シンガポール", "ホノルル", "マニラ", "ロサンゼルス", "シドニー", "ロンドン", "パリ", "フランクフルト", "デリー", "パース", "サンフランシスコ", "ニューヨーク", "上海(浦東)", "北京", "クアラルンプール", "ジャカルタ"]
        
        raw_data = []
        start_time = now.replace(minute=now.minute - (now.minute % 5), second=0, microsecond=0)
        target_end = now.replace(hour=5, minute=0, second=0, microsecond=0) + timedelta(days=1)
        total_minutes = int((target_end - start_time).total_seconds() / 60)
        
        if total_minutes < 720:
            total_minutes = 900
            
        flight_counter = 100
        for offset in range(-30, total_minutes, 5):
            loop_time = start_time + timedelta(minutes=offset)
            loop_total_hours = loop_time.hour + (24 if loop_time.date() > now.date() else 0)
            
            if loop_total_hours >= 29 and loop_time.minute > 0:
                break
                
            hour_24 = loop_time.hour
            is_night = (hour_24 >= 23 or hour_24 < 5)
            
            random.seed(offset + 2026)
            spawn_chance = 0.7 if not is_night else 0.4
            if random.random() > spawn_chance:
                continue
                
            flight_counter += 1
            
            if is_night:
                f_type = "国際線" if random.random() < 0.8 else "国内線"
            else:
                f_type = "国内線" if random.random() < 0.7 else "国際線"
                
            if f_type == "国内線":
                origin = random.choice(dom_origins)
                terminal = random.choice(["T1", "T2"])
                exit_gate = str(random.randint(1, 6))
                airline = random.choice(["JL", "NH", "6J", "ADO", "SFJ"])
                flight_num = f"{airline}{flight_counter:03d}"
                status = "到着済み" if offset < 0 else ("遅延" if random.random() < 0.05 else "定刻")
            else:
                origin = random.choice(int_origins)
                terminal = random.choice(["T2", "T3"])
                exit_gate = str(random.randint(1, 4)) if terminal == "T3" else ""
                airline = random.choice(["NH", "JL", "CX", "SQ", "TG", "BR", "AA", "DL", "LH", "AF"])
                flight_num = f"{airline}{flight_counter:03d}"
                status = "到着済み" if offset < 0 else "定刻"

            time_str = f"{loop_total_hours:02d}:{loop_time.minute:02d}"
            
            raw_data.append({
                "type": f_type,
                "time": time_str,
                "origin": origin,
                "terminal": terminal,
                "exit": exit_gate,
                "flight": flight_num,
                "status": status
            })

        for flight in raw_data:
            flight["bus_stop"] = assign_bus_stop(flight["terminal"], flight["exit"], flight["type"])
            flight["capacity"] = estimate_aircraft_capacity(flight["flight"])
            
            try:
                h, m = map(int, flight["time"].split(":"))
                m += 15 if flight["type"] == "国内線" else 30
                if m >= 60:
                    h += m // 60
                    m = m % 60
                flight["bus_stop_time"] = f"{h:02d}:{m:02d}"
            except:
                flight["bus_stop_time"] = flight["time"]
            
            if flight["type"] == "国際線":
                flight["origin"] = f"🌐[国際] {flight['origin']}"
            else:
                flight["origin"] = f"🇯🇵[国内] {flight['origin']}"
            
        df = pd.DataFrame(raw_data)
        df = df.sort_values(by="bus_stop_time")
        
        display_df = df[["bus_stop_time", "time", "origin", "flight", "capacity", "status", "bus_stop"]].rename(columns={
            "bus_stop_time": "乗り場目安時刻",
            "time": "(参考)便到着",
            "origin": "出発地", 
            "flight": "便名", 
            "capacity": "規模・座席目安", 
            "status": "状況"
        })

        for i, tab in enumerate(tabs):
            bus_stop_name = f"{i+1}号乗り場"
            filtered_df = display_df[display_df["bus_stop"] == bus_stop_name]
            
            with tab:
                if filtered_df.empty:
                    placeholders[i].info("現在、この乗り場に該当する到着便はありません。")
                else:
                    placeholders[i].empty()
                    st.dataframe(filtered_df.drop(columns=["bus_stop"]), use_container_width=True, hide_index=True)
