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
st.markdown("※表示されている時刻は、**フライト到着時刻に降機・手荷物受取の目安時間（国内線+15分、国際線+30分）を加算した「乗り場到着目安」**です。")

# 【ここをボタンの外に出しました】
tabs = st.tabs(["1号乗り場", "2号乗り場", "3号乗り場", "4号乗り場"])

# 最初は各タブにボタンを押すよう促す案内を出しておきます
for i, tab in enumerate(tabs):
    with tab:
        st.subheader(f"📍 {i+1}号乗り場 に向かってくる到着便")
        placeholder = st.empty()
        placeholder.info("「最新のフライト情報を取得」ボタンを押してください。")

# ボタンの処理
if st.button("最新のフライト情報を取得 (デモ)"):
    with st.spinner('データを取得・解析中...'):
        
        raw_data = [
            {"type": "国内線", "time": "17:30", "origin": "札幌(新千歳)", "terminal": "T2", "exit": "5 6", "flight": "NH072", "status": "到着済み"},
            {"type": "国内線", "time": "17:50", "origin": "大阪(伊丹)", "terminal": "T1", "exit": "3 4", "flight": "JL320", "status": "定刻"},
            {"type": "国際線", "time": "17:40", "origin": "青島", "terminal": "T2", "exit": "", "flight": "CA167", "status": "定刻"},
            {"type": "国際線", "time": "17:45", "origin": "台北(松山)", "terminal": "T2", "exit": "", "flight": "BR2176", "status": "定刻"},
            {"type": "国内線", "time": "18:00", "origin": "福岡", "terminal": "T2", "exit": "4 5", "flight": "NH264", "status": "定刻"},
        ]
        
        for flight in raw_data:
            flight["bus_stop"] = assign_bus_stop(flight["terminal"], flight["exit"], flight["type"])
            flight["capacity"] = estimate_aircraft_capacity(flight["flight"])
            flight["bus_stop_time"] = calculate_bus_stop_time(flight["time"], flight["type"])
            
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

        # ボタンが押されたら、用意しておいたタブの中にデータを上書きします
        for i, tab in enumerate(tabs):
            bus_stop_name = f"{i+1}号乗り場"
            with tab:
                filtered_df = display_df[display_df["bus_stop"] == bus_stop_name]
                if filtered_df.empty:
                    st.info("現在、この乗り場に該当する到着便はありません。")
                else:
                    st.dataframe(filtered_df.drop(columns=["bus_stop"]), use_container_width=True, hide_index=True)
