import requests
import json

# Kredensial Bot Telegram Abang Resmi
TOKEN = "8839152051:AAHF5NIlFruU5ZsT5AymlliVlJGZLDapY2Q"
CHAT_ID = "8440896866"

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("🚀 BERHASIL DIKIRIM KE TELEGRAM!")
        else:
            print(f"❌ Gagal kirim Telegram: {response.text}")
    except Exception as e:
        print(f"❌ Eror koneksi Telegram: {e}")

def ambil_data_market():
    print("📡 Menghubungi bursa data global Yahoo Finance...")
    msg = "🔔 **SEKARANG OPEN CANDLE H1** 🔔\n🦅 **ALCHEMIST SNIPER V6.0 CLOUD** 🦅\n───────────────────────\n"
    
    pairs = [
        {'id': 'GC=F', 'nama': 'XAUUSD (GOLD)'},
        {'id': 'BTC-USD', 'nama': 'BTCUSD'},
        {'id': 'EURUSD=X', 'nama': 'EURUSD'}
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for p in pairs:
        try:
            url = f"https://query1.financeapi.com/v8/finance/chart/{p['id']}?interval=1h&range=5d"
            res = requests.get(url, headers=headers).json()
            
            data = res['chart']['result'][0]
            o = [x for x in data['indicators']['quote'][0]['open'] if x is not None]
            c = [x for x in data['indicators']['quote'][0]['close'] if x is not None]
            h = [x for x in data['indicators']['quote'][0]['high'] if x is not None]
            l = [x for x in data['indicators']['quote'][0]['low'] if x is not None]
            
            sizes = [{'idx': i, 's': abs(c[i] - o[i])} for i in range(len(o))]
            sizes.sort(key=lambda x: x['s'], reverse=True)
            idx = sizes[0]['idx']
            mid_ob = (o[idx] + c[idx]) / 2
            
            liq_h = max(h[-24:])
            liq_l = min(l[-24:])
            price = c[-1]
            
            if price > mid_ob:
                tipe = "SELL LIMIT (Premium Area)"
                sl, tp = liq_h * 1.001, liq_l
            else:
                tipe = "BUY LIMIT (Discount Area)"
                sl, tp = liq_l * 0.999, liq_h
                
            msg += f"📊 **Market: {p['nama']}**\n• Setup: **{tipe}**\n• Entry: `{mid_ob:.2f}`\n• SL: `{sl:.2f}`\n• TP: `{tp:.2f}`\n\n"
            print(f"✓ Sukses kalkulasi {p['nama']}")
        except Exception as e:
            msg += f"❌ Gagal scan {p['nama']}\n\n"
            print(f"❌ Gagal scan {p['nama']}: {e}")
            
    kirim_telegram(msg)

if __name__ == "__main__":
    ambil_data_market()
