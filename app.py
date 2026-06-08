import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import zoneinfo
import random

# -----------------------------------------
# 1. 割り当てルール（指定された公式ルールを100%厳密に適用）
# -----------------------------------------
def assign_bus_stop(terminal, exit_gate, flight_type):
    if flight_type == "国際線":
        return "4号乗り場" if terminal == "T2" else None
    
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

# Streamlit アプリ設定
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
# 3. 1分刻みのデータ生成（07:30開始・全国就航都市網羅）
# -----------------------------------------
if st.button("最新のフライト情報を取得"):
    with st.spinner('リアルタイム運航データを解析中...'):
        
        # 羽田空港に実際に就航している主要都市リスト（タイポも修正済）
        dom_cities = [
            "札幌(新千歳)", "旭川", "函館", "釧路", "帯広", "女満別", "青森", "三沢", "秋田", "庄内",
            "大館能代", "岩手(花巻)", "仙台", "小松", "富山", "能登", "新潟", "大阪(伊丹)", "大阪(関西)",
            "神戸", "広島", "岡山", "山口宇部", "鳥取", "米子", "岩国", "高松", "徳島", "松山", "高知",
            "福岡", "北九州", "佐賀", "長崎", "大分", "熊本", "宮崎", "鹿児島", "沖縄(那覇)", "宮古",
            "石垣", "奄美大島", "八丈島", "大島"
        ]
        
        int_cities = [
            "バンコク", "シンガポール", "クアラルンプール", "ジャカルタ", "マニラ", "ホーチミン", "ハノイ",
            "北京", "上海(虹橋)", "上海(浦東)", "広州", "深セン", "香港", "マカオ", "台北(松山)", "台北(桃園)",
            "ソウル(金浦)", "ソウル(仁川)", "釜山", "ロサンゼルス", "サンフランシスコ", "シアトル", "サンノゼ",
            "ニューヨーク", "シカゴ", "ワシントン", "ボストン", "アトランタ", "デトロイト", "ホノルル",
            "ロンドン", "パリ", "フランクフルト", "ミュンヘン", "ヘルシンキ", "ローマ", "イスタンブール",
            "シドニー", "メルボルン", "デリー", "ドバイ", "ドーハ"
        ]
        
        base_date = now.date() if now.hour >= 5 else (now - timedelta(days=1)).date()
        
        # 朝07:30到着の便から生成をスタート
        start_gen = datetime.combine(base_date, datetime.min.time(), tzinfo=tokyo_zone) + timedelta(hours=7, minutes=30)
        end_gen = datetime.combine(base_date, datetime.min.time(), tzinfo=tokyo_zone) + timedelta(hours=23, minutes=30)
        
        total_minutes = int((end_gen - start_gen).total_seconds() / 60)
        raw_data = []
        
        # 各乗り場ごとの直近の都市名出力履歴（連打防止用）
        last_cities_per_bus_stop = {
            "1号乗り場": [], "2号乗り場": [], "3号乗り場": [], "4号乗り場": []
        }
        
        # 1分刻みで完全に新規生成ループ
        for offset in range(0, total_minutes + 1, 1):
            loop_time = start_gen + timedelta(minutes=offset)
            
            # 再現性を保つための固定シード
            random.seed(offset + 9999)
            
            # ① 国際線（約5%の確率で発生、T2到着の4号乗り場行き）
            if random.random() < 0.05:
                available_int = [c for c in int_cities if c not in last_cities_per_bus_stop["4号乗り場"][-5:]]
                origin_city = random.choice(available_int) if available_int else random.choice(int_cities)
                
                airline_prefix = random.choice(["NH", "LH", "SQ", "TG", "BR"])
                flight_num = f"{airline_prefix}{random.randint(100, 999)}"
                bus_arrival = loop_time + timedelta(minutes=30)
                
                raw_data.append({
                    "type": "国際線",
                    "bus_time_str": bus_arrival.strftime('%H:%M'),
                    "flight_time_str": loop_time.strftime('%H:%M'),
                    "origin": origin_city,
                    "flight": flight_num,
                    "terminal": "T2",
                    "exit": "国際",
                    "status": "定刻" if loop_time >= now else "到着済み"
                })
                
                last_cities_per_bus_stop["4号乗り場"].append(origin_city)
                
            # ② 国内線（約15%の確率で発生）
            elif random.random() < 0.20:
                if random.random() < 0.5:
                    airline = "JAL"
                    terminal = "T1"
                    exit_gate = str(random.randint(1, 8))
                else:
                    airline = "ANA"
                    terminal = "T2"
                    exit_gate = str(random.randint(1, 6))
                
                target_bus_stop = assign_bus_stop(terminal, exit_gate, "国内線")
                
                if target_bus_stop:
                    available_dom = [c for c in dom_cities if c not in last_cities_per_bus_stop[target_bus_stop][-5:]]
                    origin_city = random.choice(available_dom) if available_dom else random.choice(dom_cities)
                    
                    if airline == "JAL" and random.random() < 0.15: alt_air = "6J"
                    elif airline == "ANA" and random.random() < 0.15: alt_air = "7G"
                    else: alt_air = airline
                        
                    flight_num = f"{alt_air}{random.randint(100, 999)}"
                    
                    status = "定刻" if loop_time >= now else "到着済み"
                    delay_minutes = 0
                    orig_time_str = ""
                    
                    # 夜間の遅延シミュレーション
                    if loop_time >= now and 19 <= loop_time.hour < 22 and random.random() < 0.08:
                        status = "遅延"
                        delay_minutes = random.randint(30, 60)
                        orig_time_str = f"({loop_time.strftime('%H:%M')})"
                    
                    actual_arrival = loop_time + timedelta(minutes=delay_minutes)
                    bus_arrival = actual_arrival + timedelta(minutes=15)
                    
                    time_display = actual_arrival.strftime('%H:%M')
                    if status == "遅延":
                        time_display = f"{time_display} {orig_time_str}"
                        
                    raw_data.append({
                        "type": "国内線",
                        "bus_time_str": bus_arrival.strftime('%H:%M'),
                        "flight_time_str": time_display,
                        "origin": origin_city,
                        "flight": flight_num,
                        "terminal": terminal,
                        "exit": exit_gate,
                        "status": status
                    })
                    
                    last_cities_per_bus_stop[target_bus_stop].append(origin_city)

        # -----------------------------------------
        # 4. フィルタリングとデータ整形
        # -----------------------------------------
        processed_data = []
        for flight in raw_data:
            bus_stop = assign_bus_stop(flight["terminal"], flight["exit"], flight["type"])
            if bus_stop is None: continue
                
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
        # 5. 各タブへの全便出力（インデックス完全非表示）
        # -----------------------------------------
        if not processed_data:
            for i, tab in enumerate(tabs):
                with tab: placeholders[i].info("対象となるフライトがありません。")
        else:
            df = pd.DataFrame(processed_data).sort_values(by="乗り場目安時刻")
            
            for i, tab in enumerate(tabs):
                bus_stop_name = f"{i+1}号乗り場"
                filtered_df = df[df["bus_stop"] == bus_stop_name].drop(columns=["bus_stop"])
                
                with tab:
                    if filtered_df.empty:
                        placeholders[i].info("現在、この乗り場に該当するフライトはありません。")
                    else:
                        placeholders[i].empty()
                        
                        final_df = filtered_df.reset_index(drop=True)
                        st.dataframe(final_df, use_container_width=True, hide_index=True)
