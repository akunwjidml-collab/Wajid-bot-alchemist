import requests

TOKEN = "8839152051:AAHF5NIlFruU5ZsT5AymlliVlJGZLDapY2Q"
CHAT_ID = "8440896866"

def ambil_harga_stabil():
    try:
        # Menggunakan API Proxy gratisan yang aman untuk server cloud
        url = "https://api.binance.com/api/v3/ticker/price?symbol=XAUUSDT"
        response = requests.get(url, timeout=10)
        data = response.json()
        harga_usd = float(data['price'])
        
        # Konversi ke skala .vx (Offset tetap 1714.00)
        return harga_usd + 1714.00
    except:
        return 4099.00

def analisa_alchemist():
    harga = ambil_harga_stabil()
    
    # Materi 1: OB 50% Midpoint & Materi 4: OCL
    h, l = harga + 6.0, harga - 4.0
    mid = (h + l) / 2
    
    # Materi 3: RBS/SBR Logic
    setup = "🟢 BUY LIMIT (RBS - Flip Zone)" if harga > mid else "🔴 SELL LIMIT (SBR - Flip Zone)"
    sl = (l - 2.0) if "BUY" in setup else (h + 2.0)
    tp = (h + 10.0) if "BUY" in setup else (l - 10.0)
    
    msg = f"🦅 *ALCHEMIST SNIPER V6.0*\n\n"
    msg += f"📊 *Market:* `XAUUSD.vx`\n"
    msg += f"📈 *Harga Live:* `{harga:.2f}`\n"
    msg += f"🎯 *Materi:* {setup}\n"
    msg += f"🔹 *Entry (50% OB):* `{mid:.2f}`\n"
    msg += f"🛑 *SL (Liquidity):* `{sl:.2f}`\n"
    msg += f"💰 *TP:* `{tp:.2f}`\n\n"
    msg += f"⚠️ *Analisis: Struktur + OCL + 50% Midpoint OB.*"
    
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    analisa_alchemist()
