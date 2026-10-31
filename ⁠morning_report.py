import os
import requests
import yfinance as yf
from datetime import datetime
import pytz

def get_weather():
    cwa_key = os.environ.get("CWA_API_KEY")
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={cwa_key}&locationName=臺北市"
    try:
        data = requests.get(url).json()['records']['location'][0]['weatherElement']
        pop = data[1]['time'][0]['parameter']['parameterName']
        min_t = data[2]['time'][0]['parameter']['parameterName']
        max_t = data[4]['time'][0]['parameter']['parameterName']
        return f"{min_t}~{max_t}°C | 降雨 {pop}%"
    except Exception as e:
        return f"取得失敗 ({e})"

def get_aqi():
    moenv_key = os.environ.get("MOENV_API_KEY")
    url = f"https://data.moenv.gov.tw/api/v2/aqx_p_432?api_key={moenv_key}"
    try:
        records = requests.get(url).json().get('records', [])
        target_stations = ['中正', '大安', '內湖']
        results = [f"{r['sitename']}{r['aqi']}" for r in records if r['sitename'] in target_stations]
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

def send_telegram_message(msg):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": msg
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    tz = pytz.timezone('Asia/Taipei')
    today_str = datetime.now(tz).strftime('%Y-%m-%d')
    
    report = f"📅 {today_str} 晨報\n"
    report += f"📍 位置：臺北市\n"
    report += f"🌡️ 天氣：{get_weather()}\n"
    report += f"😷 AQI：{get_aqi()}\n"
    report += f"📈 NASDAQ：{get_nasdaq()}"
    
    print(report) # 在 GitHub Log 中印出結果方便除錯
    send_telegram_message(report)
