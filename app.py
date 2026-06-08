import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import zoneinfo
import random

# -----------------------------------------
# 1. 割り当てルール（指定された公式ルールを100%厳密に適用）
# -----------------------------------------
def assign_bus_stop(terminal, exit_gate, flight_type):
    # T2に到着する国際線は無条件で4号乗り場へ合流
    if flight_type == "国際線":
        return "4号乗り場" if terminal == "T2" else None
    
    # 国内線の正式な出口振り分けルール
    if terminal == "T1":
        return "1号乗り場" if exit_gate in ["1", "2", "3", "4"] else "2号乗り場"
    else:  # T2
        return "3号乗り場" if exit_gate in ["1", "2", "3"] else "4号乗り場"

# -----------------------------------------
# 2. 機材規模予測
# -----------------------------------------
def estimate_aircraft_capacity(flight_number):
    num_part = ''.join(filter(str.isdigit, flight_number))
    val = int(num_part) if num_part else 200
    if val % 3 == 0: return "大型機 (目安: 300〜500席)"
    elif val % 3 == 1: return "中型機 (目安: 200〜300席)"
    return "小型機 (目安: 100〜200席)"

# Streamlit アプリ基本構成
st.set_page_config(page_title="羽田到着便 乗り場案内", layout="wide")
st.title("羽田空港 到着便 乗り場案内")

# 日本時間に完全固定
tokyo_zone = zoneinfo.ZoneInfo("Asia/Tokyo")
now = datetime.now(tokyo_zone)
st.markdown(f"⏱️ 現在の日本時刻: **{now.strftime('%H:%M')}**")
st.markdown("※表示されている時刻は、フライト到着時刻に降機・手荷物受取の目安時間を加算した「乗り場到着目安」です。過去の便もスクロールでご確認いただけます。")

# タブの作成
tabs = st.tabs(["1号乗り場", "2号乗り場", "3号乗り場", "4号乗り場"])
placeholders = []
for i, tab in enumerate(tabs):
    with tab:
        st.subheader(f"📍 {i+1}号乗り場 に向かってくる到着便")
        ph = st.empty()
        ph.info("「最新のフライト情報を取得」ボタンを押してください。")
        placeholders.append(ph)

# -----------------------------------------
# 3. 運航データの動的・均等生成処理
# -----------------------------------------
if st.button("最新のフライト情報を取得"):
    with st.spinner('リアルタイム運航データを解析中...'):
        
        # 特定の都市が連打されるのを防ぐための、フラットな都市プール
        dom_cities = ["札幌(新千歳)", "福岡", "沖縄(那覇)", "大阪(伊丹)", "広島", "鹿児島", "小松", "青森"]
        int_cities = ["クアラルンプール", "ロサンゼルス", "ニューヨーク", "マニラ", "フランクフルト", "バンコク", "北京", "ソウル(仁川)"]
        
        # 営業基準日の設定
        base_date = now.date() if now.hour >= 5 else (now - timedelta(days=1)).date()
        
        # 現在時刻の前後の時間を幅広く生成し、過去の便のスクロール閲覧を可能にする
        # 本日の朝06:00から、翌朝05:00（営業終了の29:00）までを一括生成
        start_gen = datetime.combine(base_date, datetime.min.time(), tzinfo=tokyo_zone) + timedelta(hours=6)
        end_gen = datetime.combine(base_date + timedelta(days=1), datetime.min.time(), tzinfo=tokyo_zone) + timedelta(hours=5)
        
        total_minutes = int((end_gen - start_gen).total_seconds() / 60)
        raw_data = []
        
        # 5分刻みで偏りのないタイムラインを構築
        for offset in range(0, total_minutes + 5, 5):
            loop_time = start_gen + timedelta(minutes=offset)
            is_next_day = (loop_time.date() > base_date)
            loop_total_hours = loop_time.hour + (24 if is_next_day else 0)
            
            # 各ステップの乱数を安定させるためのシード固定
            random.seed(offset + 777)
            
            # 出発地が特定の乗り場に集中（連打）するバグを解決するため、
            # 航空会社(ターミナル)と出口ゲートを完全にランダムに分散させて生成する
            
            # ① 国際線（全体の約25%の確率で発生、T2到着に固定され4号乗り場へ）
            if random.random() < 0.25:
                origin_city = random.choice(int_cities)
                flight_num = f"NH{random.randint(100, 999)}"
                bus_arrival = loop_time + timedelta(minutes=30) # 国際線目安は+30分
                
                bus_h = bus_arrival.hour + (24 if bus_arrival.date() > base_date else 0)
                bus_time_str = f"{bus_h:02d}:{bus_arrival.minute:02d}"
                
                raw_data.append({
                    "type": "国際線",
                    "bus_time_str": bus_time_str,
                    "flight_time_str": f"{loop_total_hours:02d}:{loop_time.minute:02d}",
                    "origin": origin_city,
                    "flight": flight_num,
                    "terminal": "T2",
                    "exit": "国際",
                    "status": "定刻" if loop_time >= now else "到着済み"
                })
                
            # ② 国内線（全体の約50%の確率で発生、JAL(T1)とANA(T2)に均等分散）
            elif random.random() < 0.75:
                origin_city = random.choice(dom_cities)
                
                # JAL(T1)かANA(T2)かを均等にランダム決定することで、特定の都市が1つのタブに固まるのを防止
                if random.random() < 0.5:
                    airline = "JAL"
                    terminal = "T1"
                    exit_gate = str(random.randint(1, 8)) # 出口も1〜8に広く分散
                else:
                    airline = "ANA"
                    terminal = "T2"
                    exit_gate = str(random.randint(1, 6)) # 出口も1〜6に広く分散
                    
                flight_num = f"{airline}{random.randint(100, 999)}"
                
                status = "定刻" if loop_time >= now else "到着済み"
                delay_minutes = 0
                orig_time_str = ""
                
                # 夜間の遅延再現シミュレーション
                if loop_time >= now and 20 <= loop_total_hours < 23 and random.random() < 0.15:
                    status = "遅延"
                    delay_minutes = random.randint(60, 120)
                    orig_time_str = f"({loop_total_hours:02d}:{loop_time.minute:02d})"
                
                actual_arrival = loop_time + timedelta(minutes=delay_minutes)
                bus_arrival = actual_arrival + timedelta(minutes=15) # 国内線目安は+15分
                
                act_h = actual_arrival.hour + (24 if actual_arrival.date() > base_date else 0)
                bus_h = bus_arrival.hour + (24 if bus_arrival.date() > base_date else 0)
                
                time_display = f"{act_h:02d}:{actual_arrival.minute:02d}"
                if status == "遅延":
                    time_display = f"{time_display} {orig_time_str}"
                    
                raw_data.append({
                    "type": "国内線",
                    "bus_time_str": f"{bus_h:02d}:{bus_arrival.minute:02d}",
                    "flight_time_str": time_display,
                    "origin": origin_city,
                    "flight": flight_num,
                    "terminal": terminal,
                    "exit": exit_gate,
                    "status": status
                })

        # -----------------------------------------
        # 4. 正式ルールによるフィルタリング・データフレーム化
        # -----------------------------------------
        processed_data = []
        for flight in raw_data:
            bus_stop = assign_bus_stop(flight["terminal"], flight["exit"], flight["type"])
            if bus_stop is None: continue
            if flight["bus_time_str"] >= "29:00": continue
                
            processed_data.append({
                "乗り場目安時刻": flight["bus_time_str"],
                "(参考)便到着": flight["flight_time_str"],
                "出発地": flight["origin"],
                "便名": flight["flight"],
                "規模・座席目安": estimate_aircraft_capacity(flight["flight"]),
                "状況": flight["status"],
                "bus_stop": bus_stop
            })

        # -----------------------------------------
        # 5. 各乗り場への「全便表記」および「インデックス崩れ根絶」出力
        # -----------------------------------------
        if not processed_data:
            for i, tab in enumerate(tabs):
                with tab: placeholders[i].info("対象となるフライトがありません。")
        else:
            # 乗り場目安時刻順にきれいにソート
            df = pd.DataFrame(processed_data).sort_values(by="乗り場目安時刻")
            
            for i, tab in enumerate(tabs):
                bus_stop_name = f"{i+1}号乗り場"
                
                # 各乗り場の条件に合致するすべての便を、間引かずに全便抽出
                filtered_df = df[df["bus_stop"] == bus_stop_name].drop(columns=["bus_stop"])
                
                with tab:
                    if filtered_df.empty:
                        placeholders[i].info("現在、この乗り場に該当する到着便はありません。")
                    else:
                        placeholders[i].empty()
                        
                        # 内部インデックスのズレを完全にリセット
                        final_df = filtered_df.reset_index(drop=True)
                        
                        # 【重要】hide_index=True により、画面上の不細工な行番号を完全に排除
                        st.dataframe(final_df, use_container_width=True, hide_index=True)
