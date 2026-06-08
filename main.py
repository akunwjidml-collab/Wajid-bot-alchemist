import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime
import os

# CONFIGURATION
TOKEN = os.getenv('8839152051:AAHF5NIlFruU5ZsT5AymlliVlJGZLDapY2Q')
CHAT_ID = os.getenv('8440896866')

def get_forexfactory_high_impact():
    """Mengambil data kalender ekonomi High Impact USD langsung dari Feed Forex Factory"""
    try:
        url = "https://www.forexfactory.com/ff_calendar_thisweek.xml"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        
        hari_ini = datetime.utcnow().strftime('%m-%d-%Y')
        news_bintang_3 = []
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'xml')
            events = soup.find_all('event')
            
            for event in events:
                currency = event.find('currency').text if event.find('currency') else ''
                date = event.find('date').text if event.find('date') else ''
                impact = event.find('impact').text if event.find('impact') else ''
                
                if currency == 'USD' and date == hari_ini and impact == 'High':
                    title = event.find('title').text if event.find('title') else 'News'
                    time = event.find('time').text if event.find('time') else 'N/A'
                    news_bintang_3.append(f"• ⏰ **{time}** | {title}")
        
        if news_bintang_3:
            pesan_news = "🚨 **HIGH IMPACT NEWS USD HARI INI (FOREX FACTORY RED FOLDER)** 🚨\n" + "\n".join(news_bintang_3)
            pesan_news += "\n\n⚠️ *SOP Alchemist: Waspada manipulasi harga 30 menit sebelum rilis!*"
            return pesan_news
        else:
            return "🟢 **NEWS FILTER:** Hari ini aman bang, tidak ada High Impact News USD (Bintang 3)."
            
    except Exception as e:
        return "⚠️ **NEWS FILTER WARNING:** Pantau ForexFactory manual malam ini!"

def hitung_alchemist_v5_3():
    """Fungsi utama scan market SMC / Alchemist V5.3"""
    pairs = ['GC=F', 'BTC-USD', 'EURUSD=X']
    
    # 📢 DI SINI TAMBAHAN SAKRALNYA BANG: Menyapa "Sekarang open candle H1" di baris paling atas!
    pesan_total = "🔔 **SEKARANG OPEN CANDLE H1** 🔔\n"
    pesan_total += "🦅 **ALCHEMIST SNIPER V5.3 REPORT** 🦅\n"
    pesan_total += "───────────────────────\n"
    
    # Ambil info berita Forex Factory
    info_news = get_forexfactory_high_impact()
    pesan_total += f"{info_news}\n───────────────────────\n"
    
    for pair in pairs:
        nama_tampilan = "XAUUSD (GOLD)" if pair == 'GC=F' else ("BTCUSD" if pair == 'BTC-USD' else "EURUSD")
        pesan_total += f"📊 **Market: {nama_tampilan}**\n"
        
        try:
            url = f"https://query1.financeapi.com/v8/finance/chart/{pair}?interval=1h&range=5d"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
            
            result = res['chart']['result'][0]
            opens = result['indicators']['quote'][0]['open']
            closes = result['indicators']['quote'][0]['close']
            highs = result['indicators']['quote'][0]['high']
            lows = result['indicators']['quote'][0]['low']
            
            body_sizes = [abs(c - o) for o, c in zip(opens, closes) if o is not None and c is not None]
            idx_strong = np.argmax(body_sizes)
            
            ocl_open = opens[idx_strong]
            ocl_close = closes[idx_strong]
            mid_ob = (ocl_open + ocl_close) / 2
            
            liq_high = max(highs[-24:])
            liq_low = min(lows[-24:])
            
            harga_sekarang = closes[-1]
            if harga_sekarang > mid_ob:
                tipe_order = "SELL LIMIT (Premium / Inducement Area)"
                entry = mid_ob
                sl = liq_high + (liq_high * 0.001)
                tp = liq_low
            else:
                tipe_order = "BUY LIMIT (Discount / Stop Hunt Area)"
                entry = mid_ob
                sl = liq_low - (liq_low * 0.001)
                tp = liq_high

            pesan_total += f"• Setup: **{tipe_order}**\n"
            pesan_total += f"• Entry (50% OB): `{entry:.2f}`\n"
            pesan_total += f"• Stop Loss (SL): `{sl:.2f}`\n"
            pesan_total += f"• Take Profit (TP): `{tp:.2f}`\n\n"
            
        except Exception as e:
            pesan_total += f"❌ Gagal scan pair ini: {str(e)}\n\n"
            
    # Kirim ke Telegram lo
    url_tele = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url_tele, json={'chat_id': CHAT_ID, 'text': pesan_total, 'parse_mode': 'Markdown'})

if __name__ == "__main__":
    hitung_alchemist_v5_3()
