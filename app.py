import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# -----------------------------------------
# 1. 乗り場を割り当てる関数
# -----------------------------------------
def assign_bus_stop(terminal, exit_gate, flight_type):
    if flight_type == "国際線" and terminal == "T2":
        return "4号乗り場"
        
    first_exit = str(exit_gate).replace(" ", "")
    if not first_exit or first_exit == "nan" or first_exit == "": return "不明"
        
    try:
        first_exit_num = int(first_exit[0])
    except ValueError:
        return "不明"

    if terminal == "T1":
        return "1号乗り場" if first_exit_num in [1, 2, 3, 4] else "2号乗り場" if first_exit_num in [5, 6, 7, 8] else "その他"
    elif terminal == "T2":
        return "3号乗り場" if first_exit_num in [1, 2, 3] else "4号乗り場" if first_exit_num in [4, 5, 6] else "その他"
            
    return "その他"

# -----------------------------------------
# 2. 機体のサイズを推測する関数
# -----------------------------------------
def estimate_aircraft_capacity(flight_number):
    flight_num_upper = str(flight_number).upper()
    if any(code in flight_num_upper for code in ["BC", "HD", "6J", "7G", "MQ"]):
        return "✈️ 小型機 (約150席)"
    elif any(code in flight_num_upper for code in ["JL", "NH", "BR", "CA"]):
        return "✈️ 大型/中型機 (約250〜350席)"
    return "✈️ 機種不明"

# -----------------------------------------
# 3. 乗り場への到着目安時間を計算する関数 [NEW!]
# -----------------------------------------
def calculate_bus_stop_time(time_str, flight_type):
    """
    フライト到着時刻(HH:MM)に所要時間を加算する
    国内線: +15分 / 国際線: +30分
    """
    try:
        # 文字列(例:"17:30")を時刻計算用のデータに変換
        t = datetime.strptime(time_str, "%H:%M")
        
        # 区分に応じて分を加算
        if flight_type == "国内線":
            adjusted_t = t + timedelta(minutes=15)
        elif flight_type == "国際線":
            adjusted_t = t + timedelta(minutes=30)
        else:
            adjusted_t = t
            
        # 計算結果を再び文字列(HH:MM)に戻して返す
        return adjusted_t.strftime("%H:%M")
        
    except ValueError:
        # 時刻の形式が想定外(空欄など)の場合はそのまま返す
        return time_str

# -----------------------------------------
# 4. アプリ画面の構築（UI）
# -----------------------------------------
st.set_page_config(page_title="羽田到着便 乗り場案内", layout="wide")
st.title("羽田空港 到着便 乗り場案内")

# サーバーの場所に関関わらず、完全に日本時間に固定します
import zoneinfo
tokyo_zone = zoneinfo.ZoneInfo("Asia/Tokyo")
now = datetime.now(tokyo_zone)

current_time_str = now.strftime("%H:%M")
st.markdown(f"⏱️ 現在の日本時刻: **{current_time_str}**")
st.markdown("※表示されている時刻は、フライト到着時刻に降機・手荷物受取の目安時間を加算した「乗り場到着目安」です。")

# 先に画面にタブを作っておきます
tabs = st.tabs(["1号乗り場", "2号乗り場", "3号乗り場", "4号乗り場"])

# 各タブの中に案内を表示するための入れ物を作っておきます
placeholders = []
for i, tab in enumerate(tabs):
    with tab:
        st.subheader(f"📍 {i+1}号乗り場 に向かってくる到着便")
        ph = st.empty()
        ph.info("「最新のフライト情報を取得」ボタンを押してください。")
        placeholders.append(ph)

# ボタンの処理
if st.button("最新のフライト情報を取得"):
    with st.spinner('29:00までの大量のフライトスケジュールを全乗り場に配分中...'):
        
        # 全ての乗り場（1〜4号）に満遍なく行き渡るように配置した40便以上のベースデータ
        base_data = [
            # --- 1号乗り場へ向かう便（T1・出口1〜3、または特定の国際線） ---
            {"type": "国内線", "min_offset": -15, "origin": "福岡", "terminal": "T1", "exit": "2", "flight": "JL318", "status": "到着済み"},
            {"type": "国内線", "min_offset": -5, "origin": "大阪(伊丹)", "terminal": "T1", "exit": "3", "flight": "JL320", "status": "到着済み"},
            {"type": "国内線", "min_offset": 15, "origin": "鹿児島", "terminal": "T1", "exit": "1", "flight": "JL652", "status": "定刻"},
            {"type": "国内線", "min_offset": 45, "origin": "熊本", "terminal": "T1", "exit": "2", "flight": "JL634", "status": "定刻"},
            {"type": "国内線", "min_offset": 90, "origin": "長崎", "terminal": "T1", "exit": "3", "flight": "JL612", "status": "定刻"},
            {"type": "国内線", "min_offset": 150, "origin": "札幌(新千歳)", "terminal": "T1", "exit": "1", "flight": "JL524", "status": "定刻"},
            {"type": "国内線", "min_offset": 240, "origin": "那覇", "terminal": "T1", "exit": "2", "flight": "JL916", "status": "定刻"},
            {"type": "国内線", "min_offset": 360, "origin": "小松", "terminal": "T1", "exit": "3", "flight": "JL188", "status": "定刻"},
            {"type": "国際線", "min_offset": 480, "origin": "パース", "terminal": "T3", "exit": "1", "flight": "NH882", "status": "定刻"},
            {"type": "国際線", "min_offset": 660, "origin": "パリ", "terminal": "T3", "exit": "1", "flight": "AF274", "status": "定刻"},

            # --- 2号乗り場へ向かう便（T1・出口4〜7、または特定の国際線） ---
            {"type": "国内線", "min_offset": -10, "origin": "北九州", "terminal": "T1", "exit": "5", "flight": "SFJ082", "status": "到着済み"},
            {"type": "国内線", "min_offset": 10, "origin": "旭川", "terminal": "T1", "exit": "4", "flight": "ADO084", "status": "定刻"},
            {"type": "国内線", "min_offset": 35, "origin": "函館", "terminal": "T1", "exit": "6", "flight": "ADO060", "status": "定刻"},
            {"type": "国内線", "min_offset": 70, "origin": "青森", "terminal": "T1", "exit": "4", "flight": "JL148", "status": "定刻"},
            {"type": "国内線", "min_offset": 120, "origin": "南紀白浜", "terminal": "T1", "exit": "5", "flight": "JL218", "status": "定刻"},
            {"type": "国内線", "min_offset": 200, "origin": "出雲", "terminal": "T1", "exit": "7", "flight": "JL284", "status": "定刻"},
            {"type": "国内線", "min_offset": 300, "origin": "徳島", "terminal": "T1", "exit": "4", "flight": "JL464", "status": "定刻"},
            {"type": "国際線", "min_offset": 450, "origin": "デリー", "terminal": "T3", "exit": "4", "flight": "AI306", "status": "定刻"},
            {"type": "国際線", "min_offset": 580, "origin": "シドニー", "terminal": "T3", "exit": "5", "flight": "QF025", "status": "定刻"},
            {"type": "国際線", "min_offset": 700, "origin": "ロンドン", "terminal": "T3", "exit": "4", "flight": "BA007", "status": "定刻"},

            # --- 3号乗り場へ向かう便（T2・出口1〜3、または特定の国際線） ---
            {"type": "国内線", "min_offset": -5, "origin": "富山", "terminal": "T2", "exit": "2", "flight": "NH320", "status": "到着済み"},
            {"type": "国内線", "min_offset": 20, "origin": "米子", "terminal": "T2", "exit": "1", "flight": "NH386", "status": "定刻"},
            {"type": "国内線", "min_offset": 55, "origin": "鳥取", "terminal": "T2", "exit": "3", "flight": "NH298", "status": "定刻"},
            {"type": "国内線", "min_offset": 105, "origin": "高松", "terminal": "T2", "exit": "2", "flight": "NH538", "status": "定刻"},
            {"type": "国内線", "min_offset": 180, "origin": "大館能代", "terminal": "T2", "exit": "1", "flight": "NH724", "status": "定刻"},
            {"type": "国内線", "min_offset": 260, "origin": "庄内", "terminal": "T2", "exit": "3", "flight": "NH400", "status": "定刻"},
            {"type": "国内線", "min_offset": 340, "origin": "岩国", "terminal": "T2", "exit": "2", "flight": "NH638", "status": "定刻"},
            {"type": "国際線", "min_offset": 510, "origin": "バンコク", "terminal": "T3", "exit": "2", "flight": "TG682", "status": "定刻"},
            {"type": "国際線", "min_offset": 620, "origin": "マニラ", "terminal": "T3", "exit": "3", "flight": "PR424", "status": "定刻"},
            {"type": "国際線", "min_offset": 740, "origin": "フランクフルト", "terminal": "T3", "exit": "2", "flight": "LH716", "status": "定刻"},

            # --- 4号乗り場へ向かう便（T2・出口4〜7、または特定の国際線/T2国際線） ---
            {"type": "国内線", "min_offset": 0, "origin": "札幌(新千歳)", "terminal": "T2", "exit": "5", "flight": "NH072", "status": "定刻"},
            {"type": "国内線", "min_offset": 25, "origin": "沖縄(那覇)", "terminal": "T2", "exit": "4", "flight": "NH472", "status": "定刻"},
            {"type": "国内線", "min_offset": 40, "origin": "福岡", "terminal": "T2", "exit": "5", "flight": "NH264", "status": "定刻"},
            {"type": "国内線", "min_offset": 60, "origin": "広島", "terminal": "T2", "exit": "6", "flight": "6J036", "status": "定刻"},
            {"type": "国内線", "min_offset": 80, "origin": "小松", "terminal": "T2", "exit": "4", "flight": "NH756", "status": "定刻"},
            {"type": "国内線", "min_offset": 130, "origin": "宮崎", "terminal": "T2", "exit": "5", "flight": "6J054", "status": "定刻"},
            {"type": "国内線", "min_offset": 210, "origin": "鹿児島", "terminal": "T2", "exit": "6", "flight": "NH628", "status": "定刻"},
            {"type": "国際線", "min_offset": -5, "origin": "青島", "terminal": "T2", "exit": "", "flight": "CA167", "status": "到着済み"},
            {"type": "国際線", "min_offset": 5, "origin": "台北(松山)", "terminal": "T2", "exit": "", "flight": "BR2176", "status": "定刻"},
            {"type": "国際線", "min_offset": 400, "origin": "ホノルル", "terminal": "T2", "exit": "", "flight": "HA863", "status": "定刻"},
            {"type": "国際線", "min_offset": 550, "origin": "ロサンゼルス", "terminal": "T3", "exit": "7", "flight": "AA027", "status": "定刻"},
            {"type": "国際線", "min_offset": 720, "origin": "シンガポール", "terminal": "T3", "exit": "6", "flight": "SQ636", "status": "定刻"},
        ]
        
        raw_data = []
        for base in base_data:
            flight_time = now + timedelta(minutes=base["min_offset"])
            
            # 24時以降を「25:00」「29:00」のように変換
            total_hours = flight_time.hour
            if flight_time.date() > now.date():
                total_hours += 24
                
            time_str = f"{total_hours:02d}:{flight_time.minute:02d}"
            
            raw_data.append({
                "type": base["type"],
                "time": time_str,
                "origin": base["origin"],
                "terminal": base["terminal"],
                "exit": base["exit"],
                "flight": base["flight"],
                "status": base["status"]
            })

        for flight in raw_data:
            flight["bus_stop"] = assign_bus_stop(flight["terminal"], flight["exit"], flight["type"])
            flight["capacity"] = estimate_aircraft_capacity(flight["flight"])
            
            # バス乗り場目安時刻の計算（24時超え表記を維持）
            try:
                h, m = map(int, flight["time"].split(":"))
                if flight["type"] == "国内線":
                    m += 15
                else:
                    m += 30
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

        # 各タブに偏りなくデータを流し込みます
        for i, tab in enumerate(tabs):
            bus_stop_name = f"{i+1}号乗り場"
            filtered_df = display_df[display_df["bus_stop"] == bus_stop_name]
            
            with tab:
                if filtered_df.empty:
                    placeholders[i].info("現在、この乗り場に該当する到着便はありません。")
                else:
                    placeholders[i].empty()
                    st.dataframe(filtered_df.drop(columns=["bus_stop"]), use_container_width=True, hide_index=True)
