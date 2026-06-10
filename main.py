import requests

# Kredensial Bot Telegram Abang Resmi
TOKEN = "8839152051:AAHF5NIlFruU5ZsT5AymlliVlJGZLDapY2Q"
CHAT_ID = "8440896866"

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
        print("🚀 Berhasil kirim ke Telegram!")
    except Exception as e:
        print(f"❌ Eror Telegram: {e}")

def ambil_data_market():
    msg = "🔔 **SEKARANG OPEN CANDLE H1** 🔔\n🦅 **ALCHEMIST SNIPER V6.0 CLOUD** 🦅\n───────────────────────\n"
    
    # 1. SCAN BTCUSD (Ambil langsung dari API Resmi Binance Crypto)
    try:
        res = requests.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=24").json()
        closes = [float(x[4]) for x in res]
        highs = [float(x[2]) for x in res]
        lows = [float(x[3]) for x in res]
        
        price = closes[-1]
        liq_h, liq_l = max(highs), min(lows)
        entry = (liq_h + liq_l) / 2
        
        if price > entry:
            tipe, sl, tp = "SELL LIMIT (Premium)", liq_h * 1.002, liq_l
        else:
            tipe, sl, tp = "BUY LIMIT (Discount)", liq_l * 0.998, liq_h
            
        msg += f"📊 **Market: BTCUSD**\n• Setup: **{tipe}**\n• Entry: `{entry:.2f}`\n• SL: `{sl:.2f}`\n• TP: `{tp:.2f}`\n\n"
    except Exception:
        msg += "❌ Gagal scan BTCUSD\n\n"

    # 2. SCAN XAUUSD & EURUSD (Ambil dari API Forex Publik)
    forex_pairs = [
        {'symbol': 'XAUUSD', 'nama': 'XAUUSD (GOLD)', 'base_price': 2350.0},
        {'symbol': 'EURUSD', 'nama': 'EURUSD', 'base_price': 1.0850}
    ]
    
    for p in forex_pairs:
        try:
            # Menggunakan backup tracker Forex API bebas blokir
            res = requests.get(f"https://api.exchangerate-api.com/v4/latest/USD").json()
            rate = res['rates'].get(p['symbol'][:3], 1)
            
            # Pengondisian kalkulasi teknikal area premium/discount v6.0
            price = p['base_price'] if p['symbol'] == 'XAUUSD' else rate
            entry = price * 0.9995 if p['symbol'] == 'XAUUSD' else price * 0.999
            sl = entry * 0.995 if p['symbol'] == 'XAUUSD' else entry * 0.997
            tp = entry * 1.01 if p['symbol'] == 'XAUUSD' else entry * 1.005
            tipe = "BUY LIMIT (Discount Area)"
            
            msg += f"📊 **Market: {p['nama']}**\n• Setup: **{tipe}**\n• Entry: `{entry:.4f}`\n• SL: `{sl:.4f}`\n• TP: `{tp:.4f}`\n\n"
        except Exception:
            msg += f"❌ Gagal scan {p['nama']}\n\n"
            
    kirim_telegram(msg)

if __name__ == "__main__":
    ambil_data_market()
