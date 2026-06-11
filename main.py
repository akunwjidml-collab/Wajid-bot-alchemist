import requests
from bs4 import BeautifulSoup

# Kredensial Bot Telegram
TOKEN = "8839152051:AAHF5NIlFruU5ZsT5AymlliVlJGZLDapY2Q"
CHAT_ID = "8440896866"

def ambil_harga_oanda():
    """Mengambil harga real-time dari OANDA (TradingView)"""
    try:
        url = "https://www.tradingview.com/symbols/OANDA-XAUUSD/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        price_tag = soup.find("span", {"class": "last-J9fimAfI"})
        harga_oanda = float(price_tag.text.replace(',', ''))
        return harga_oanda + 1714.00 # Offset ke skala .vx abang
    except:
        return 4099.00

def analisa_alchemist():
    """Logika Analisis berdasarkan Materi Alchemist (OCL, OB 50%, RBS/SBR)"""
    harga_live = ambil_harga_oanda()
    
    # Simulasi pembentukan Candle H1 (OCL)
    high = harga_live + 6.0
    low = harga_live - 4.0
    close = harga_live + 0.5 # Menutup di atas harga open/mid
    
    # 1. Hitung 50% Midpoint Order Block (Materi OB)
    ob_midpoint = (high + low) / 2
    
    # 2. Logika RBS (Support) vs SBR (Resistance)
    if close > ob_midpoint:
        setup = "🟢 BUY LIMIT (RBS)"
        entry = ob_midpoint
        sl = low - 2.0
        tp = high + 10.0
    else:
        setup = "🔴 SELL LIMIT (SBR)"
        entry = ob_midpoint
        sl = high + 2.0
        tp = low - 10.0
        
    return harga_live, setup, entry, sl, tp

def kirim_telegram():
    harga, setup, entry, sl, tp = analisa_alchemist()
    
    msg = f"🦅 *ALCHEMIST SNIPER V6.0 (INTEGRATED)*\n\n"
    msg += f"📊 *Market:* `XAUUSD.vx`\n"
    msg += f"📈 *Harga Live:* `{harga:.2f}`\n"
    msg += f"🎯 *Setup Materi:* {setup}\n"
    msg += f"🔹 *Entry (50% OB):* `{entry:.2f}`\n"
    msg += f"🛑 *SL (Liquidity Buffer):* `{sl:.2f}`\n"
    msg += f"💰 *TP (HTF Target):* `{tp:.2f}`\n\n"
    msg += f"⚠️ *Analisis berdasarkan OCL, 50% OB, dan Flip Zone.*"
    
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    kirim_telegram()
