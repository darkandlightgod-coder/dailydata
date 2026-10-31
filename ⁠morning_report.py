import os
import requests
import yfinance as yf
from datetime import datetime
import pytz

def get_weather():
    # 鎖定臺北市天氣預報
    cwa_key = os.environ.get("CWA_API_KEY")
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={cwa_key}&locationName=臺北市"
    try:
        data = requests.get(url).json()['records']['location'][0]['weatherElement']
        pop = data[1]['time'][0]['parameter']['parameterName']  # 降雨機率
        min_t = data[2]['time'][0]['parameter']['parameterName'] # 最低溫
        max_t = data[4]['time'][0]['parameter']['parameterName'] # 最高溫
        return f"{min_t}~{max_t}°C | 降雨 {pop}%"
    except Exception as e:
        return f"取得失敗 ({e})"

def get_aqi():
    moenv_key = os.environ.get("MOENV_API_KEY")
    url = f"https://data.moenv.gov.tw/api/v2/aqx_p_432?api_key={moenv_key}"
    try:
        records = requests.get(url).json().get('records', [])
        # 精準鎖定這三個台北市測站
        target_stations = ['中正', '大安', '內湖']
        results = [f"{r['sitename']}{r['aqi']}" for r in records if r['sitename'] in target_stations]
        
        # 確保輸出的排版順序與我們設定的相同
        results.sort(key=lambda x: [s in x for s in target_stations].index(True))
        return " | ".join(results)
    except Exception as e:
        return f"取得失敗 ({e})"

def get_nasdaq():
    try:
        ndx = yf.Ticker("^IXIC")
        hist = ndx.history(period="5d")
        close_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2]
        change_pct = ((close_price - prev_close) / prev_close) * 100
        sign = "+" if change_pct > 0 else ""
        return f"{close_price:,.2f} ({sign}{change_pct:.2f}%)"
    except Exception as e:
        return f"取得失敗 ({e})"

def send_line_notify(msg):
    token = os.environ.get("LINE_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    requests.post("https://notify-api.line.me/api/notify", headers=headers, data={"message": msg})

if __name__ == "__main__":
    tz = pytz.timezone('Asia/Taipei')
    today_str = datetime.now(tz).strftime('%Y-%m-%d')
    
    report = f"\n📅 {today_str} 晨報\n"
    report += f"📍 位置：臺北市\n"
    report += f"🌡️ 天氣：{get_weather()}\n"
    report += f"😷 AQI：{get_aqi()}\n"
    report += f"📈 NASDAQ：{get_nasdaq()}"
    
    send_line_notify(report)
