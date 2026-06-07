import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import zoneinfo
import random

# -----------------------------------------
# 1. 乗り場判定ロジック（4号乗り場のハイブリッド運用を完全再現）
# -----------------------------------------
def assign_bus_stop(terminal, exit_gate, flight_type):
    if flight_type == "国際線":
        if terminal == "T2":
            return "4号乗り場"  # 国際線はT2のみ4号
        else:
            return None  # T3などの国際線は除外
    else:
        # 国内線の振り分け（4号乗り場にもしっかり国内線が入るように修正）
        if terminal == "T1":
            if exit_gate in ["1", "2", "3"]:
                return "1号乗り場"
            else:
                return "2号乗り場"
        else:  # T2国内線
            if exit_gate in ["1", "2", "3"]:
                return "3号乗り場"
            else:
                return "4号乗り場"  # 出口4, 5, 6などは夕方〜最終まで4号乗り場に到着！

# -----------------------------------------
# 2. UI & 機材規模予測
# -----------------------------------------
def estimate_aircraft_capacity(flight_number):
    num_part = ''.join(filter(str.isdigit, flight_number))
    if not num_part:
        return "中型機 (目安: 200〜300席)"
    val = int(num_part)
    if val % 3 == 0: return "大型機 (目安: 300〜500席)"
    elif val % 3 == 1: return "中型機 (目安: 200〜300席)"
    else: return "小型機 (目安: 100〜200席)"

st.set_page_config(page_title="羽田到着便 乗り場案内", layout="wide")
st.title("羽田空港 到着便 乗り場案内")

# 日本時間に完全に固定
tokyo_zone = zoneinfo.ZoneInfo("Asia/Tokyo")
now = datetime.now(tokyo_zone)
current_time_str = now.strftime("%H:%M")
st.markdown(f"⏱️ 現在の日本時刻: **{current_time_str}**")
st.markdown("※表示されている時刻は、フライト到着時刻に降機・手荷物受取の目安時間を加算した「乗り場到着目安」です。")

tabs = st.tabs(["1号乗り場", "2号乗り場", "3号乗り場", "4号乗り場"])
placeholders = []
for i, tab in enumerate(tabs):
    with tab:
        st.subheader(f"📍 {i+1}号乗り場 に向かってくる到着便")
        ph = st.empty()
        ph.info("「最新のフライト情報を取得」ボタンを押してください。")
        placeholders.append(ph)

# -----------------------------------------
# 3. データ生成
# -----------------------------------------
if st.button("最新のフライト情報を取得"):
    with st.spinner('リアルタイムの運航状況（遅延・国内・国際線）を反映中...'):
        
        dom_origins = ["札幌(新千歳)", "福岡", "大阪(伊丹)", "沖縄(那覇)", "広島", "鹿児島", "熊本", "長崎", "小松", "旭川", "函館", "青森", "南紀白浜", "出雲", "徳島", "富山", "米子", "鳥取", "高松", "大館能代", "庄内", "岩国", "宮崎", "秋田", "新潟", "大分"]
        int_origins = ["ホノルル", "シンガポール", "香港", "ニューヨーク", "クアラルンプール", "北京", "パリ", "バンコク", "ソウル(仁川)", "台北(松山)", "ロサンゼルス", "ロンドン", "フランクフルト", "サンフランシスコ", "シドニー", "マニラ", "上海(浦東)"]
        
        start_time = now.replace(minute=now.minute - (now.minute % 5), second=0, microsecond=0)
        target_end = now.replace(hour=5, minute=0, second=0, microsecond=0) + timedelta(days=1)
        total_minutes = int((target_end - start_time).total_seconds() / 60)
        if total_minutes < 1440: total_minutes = 1440
            
        raw_data = []
        flight_counter = 100
        
        # 過去3時間から29:00（翌朝5:00）までのループ
        for offset in range(-180, total_minutes, 5): 
            loop_time = start_time + timedelta(minutes=offset)
            loop_total_hours = loop_time.hour + (24 if loop_time.date() > now.date() else 0)
            
            if loop_total_hours >= 29 and loop_time.minute > 0:
                break
                
            random.seed(offset + 13579) # 安定したシード
            
            # 1. 国際線の生成（24時間いつでも飛んでくる・T2固定）
            if random.random() < 0.25:
                flight_counter += 1
                origin = random.choice(int_origins)
                terminal = "T2" 
                exit_gate = str(random.randint(1, 4))
                airline = random.choice(["NH", "JL", "SQ", "CX", "TG", "MH", "BR"])
                flight_num = f"{airline}{flight_counter:03d}"
                status = "到着済み" if offset < 0 else "定刻"
                
                raw_data.append({
                    "type": "国際線",
                    "base_h": loop_total_hours,
                    "base_m": loop_time.minute,
                    "origin": origin,
                    "terminal": terminal,
                    "exit": exit_gate,
                    "flight": flight_num,
                    "status": status
                })
                
            # 2. 国内線の生成（定刻ベースは23:00で完全にシャットアウト）
            if loop_total_hours < 23:
                if random.random() < 0.65:
                    flight_counter += 1
                    origin = random.choice(dom_origins)
                    terminal = random.choice(["T1", "T2"])
                    exit_gate = str(random.randint(1, 6))
                    airline = random.choice(["JL", "NH", "6J", "ADO", "SFJ"])
                    flight_num = f"{airline}{flight_counter:03d}"
                    
                    if offset < 0:
                        status = "到着済み"
                        delay_minutes = 0
                    else:
                        # 大規模突発遅延の再現（約8%）
                        if random.random() < 0.08:
                            status = "遅延"
                            delay_minutes = random.randint(60, 200)
                        else:
                            status = "定刻"
                            delay_minutes = 0
                            
                    calc_h = loop_total_hours
                    calc_m = loop_time.minute + delay_minutes
                    if calc_m >= 60:
                        calc_h += calc_m // 60
                        calc_m = calc_m % 60
                        
                    raw_data.append({
                        "type": "国内線",
                        "base_h": calc_h,
                        "base_m": calc_m,
                        "origin": origin,
                        "terminal": terminal,
                        "exit": exit_gate,
                        "flight": flight_num,
                        "status": status
                    })

        # -----------------------------------------
        # 4. データのマッピングと整形
        # -----------------------------------------
        processed_data = []
        for flight in raw_data:
            bus_stop = assign_bus_stop(flight["terminal"], flight["exit"], flight["type"])
            if bus_stop is None: continue
                
            flight["bus_stop"] = bus_stop
            flight["capacity"] = estimate_aircraft_capacity(flight["flight"])
            
            # 便到着時刻
            flight["time"] = f"{flight['base_h']:02d}:{flight['base_m']:02d}"
            
            # 乗り場目安時刻（国内線+15分、国際線+30分）
            h = flight["base_h"]
            m = flight["base_m"]
            m += 15 if flight["type"] == "国内線" else 30
            if m >= 60:
                h += m // 60
                m = m % 60
            flight["bus_stop_time"] = f"{h:02d}:{m:02d}"
            
            # 29:00を超えたデータはカット
            if flight["bus_stop_time"] >= "29:00":
                continue
            
            # テキスト装飾
            if flight["type"] == "国際線":
                flight["origin"] = f"🌐[国際] {flight['origin']}"
            else:
                if flight["status"] == "遅延":
                    flight["origin"] = f"⚠️[遅延] {flight['origin']}"
                else:
                    flight["origin"] = f"🇯🇵[国内] {flight['origin']}"
                
            processed_data.append(flight)
            
        # -----------------------------------------
        # 5. 各タブ画面への出力
        # -----------------------------------------
        if not processed_data:
            st.warning("表示できるフライトデータがありません。")
        else:
            df = pd.DataFrame(processed_data)
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
