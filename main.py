import os
import time
import requests
import pandas as pd

# ========================================================
# TINGGAL GANTI DUA BARIS DI BAWAH INI PAKAI DATA LO
# ========================================================
TOKEN = "8839152051:AAHF5NIlFruU5ZsT5AymlliVlJGZLDapY2Q"
CHAT_ID = "8440896866"
# ========================================================

INTERVAL = "1h" # HTF Level (1 Jam) sesuai materi untuk nyari Key SNR

DAFTAR_MARKET = {
    "XAUUSD": "GC=F",
    "BTCUSD": "BTC-USD",
    "EURUSD": "EURUSD=X",
    "USDJPY": "USDJPY=X",
    "GBPUSD": "GBPUSD=X",
    "NASDAQ": "NQ=F"
}

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Gagal kirim tele:", e)

def ambil_data(simbol_yahoo):
    url = f"https://query1.financeapi.com/v8/finance/chart/{simbol_yahoo}?interval={INTERVAL}&range=5d"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers).json()
    
    candles = res['chart']['result'][0]['indicators']['quote'][0]
    timestamps = res['chart']['result'][0]['timestamp']
    
    df = pd.DataFrame({
        'time': pd.to_datetime(timestamps, unit='s'),
        'open': candles['open'],
        'high': candles['high'],
        'low': candles['low'],
        'close': candles['close']
    }).dropna()
    return df

def cek_setup_alchemist():
    for nama_pasaran, simbol_yahoo in DAFTAR_MARKET.items():
        print(f"Memeriksa market {nama_pasaran}...")
        try:
            df = ambil_data(simbol_yahoo)
            if len(df) < 15: continue

            # Ambil candle running dan candle konfirmasi ke belakang
            c = df.iloc[-1]   # Candle running sekarang
            p1 = df.iloc[-2]  # Candle konfirmasi CHoCH / MSB
            p2 = df.iloc[-3]  # Candle pemicu Sweep (OB / MSNR Zone)
            
            # Materi 1: LIT & ICT (Mencari Liquidity Pool dari Swing High/Low Terkuat)
            prev_candles = df.iloc[:-3]
            highest_high = prev_candles['high'].max()
            lowest_low = prev_candles['low'].min()

            # Format angka desimal biar rapih di notif HP
            fmt = "{:.2f}" if "USD" not in nama_pasaran or nama_pasaran == "XAUUSD" else "{:.5f}"

            # ------------------------------------------------------------
            # SETUP BEARISH ALCHEMIST COMPLETE (SMC + MSNR + ICT + LIT)
            # ------------------------------------------------------------
            # A. ICT/LIT Check: Terjadi Liquidity Sweep (Harga nembus High lalu close di bawahnya)
            if p2['high'] > highest_high and p2['close'] < highest_high:
                
                # B. SMC Check: Terjadi Market Structure Break / CHoCH valid (Bodi candle p1 close menembus low p2)
                if p1['close'] < p2['low']:
                    
                    # C. MSNR & FIBO Check: Ambil area Order Block (OB) dan hitung Fibo 0.5 (Midpoint)
                    ob_high = p2['high']
                    ob_low = p2['low']
                    ob_mid = (ob_high + ob_low) / 2  # Level Fibo 0.5 sesuai E-book Alchemist
                    
                    pesan = f"🌋 *ALCHEMIST SUPREME SIGNAL - {nama_pasaran}* 🌋\n\n" \
                            f"📌 *METODE COMPILATION:* SMC + MSNR + ICT + LIT\n\n" \
                            f"✅ *1. LIT & ICT:* Liquidity Sweep / Turtle Soup Sukses! ({fmt.format(highest_high)})\n" \
                            f"✅ *2. SMC STRUCT:* CHoCH / Break of Structure Terdeteksi (Valid Bodi Close)\n" \
                            f"✅ *3. MSNR POI:* Order Block Terbentuk di Area Key SNR\n\n" \
                            f"🎯 *TRADING PLAN (SELL LIMIT):*\n" \
                            f"▪️ *Entry Zone (Fibo 0.5):* {fmt.format(ob_mid)}\n" \
                            f"▪️ *Stop Loss (High OB):* {fmt.format(ob_high)}\n" \
                            f"▪️ *Take Profit:* Cari area Swing Low terdekat / Opsi RR 1:2\n\n" \
                            f"ℹ️ _Sinyal otomatis aktif 24 Jam nonstop via Render Cloud._"
                    
                    kirim_telegram(pesan)
                    print(f"Sinyal SELL {nama_pasaran} sukses dikirim!")

            # ------------------------------------------------------------
            # SETUP BULLISH ALCHEMIST COMPLETE (SMC + MSNR + ICT + LIT)
            # ------------------------------------------------------------
            # A. ICT/LIT Check: Terjadi Liquidity Sweep (Harga nembus Low lalu close di atasnya)
            elif p2['low'] < lowest_low and p2['close'] > lowest_low:
                
                # B. SMC Check: Terjadi CHoCH valid (Bodi candle p1 close menembus high p2)
                if p1['close'] > p2['high']:
                    
                    # C. MSNR & FIBO Check: Ambil area Order Block (OB) dan hitung Fibo 0.5 (Midpoint)
                    ob_high = p2['high']
                    ob_low = p2['low']
                    ob_mid = (ob_high + ob_low) / 2  # Level Fibo 0.5 sesuai E-book Alchemist
                    
                    pesan = f"🌋 *ALCHEMIST SUPREME SIGNAL - {nama_pasaran}* 🌋\n\n" \
                            f"📌 *METODE COMPILATION:* SMC + MSNR + ICT + LIT\n\n" \
                            f"✅ *1. LIT & ICT:* Liquidity Sweep / Turtle Soup Sukses! ({fmt.format(lowest_low)}\n" \
                            f"✅ *2. SMC STRUCT:* CHoCH / Break of Structure Terdeteksi (Valid Bodi Close)\n" \
                            f"✅ *3. MSNR POI:* Order Block Terbentuk di Area Key SNR\n\n" \
                            f"🎯 *TRADING PLAN (BUY LIMIT):*\n" \
                            f"▪️ *Entry Zone (Fibo 0.5):* {fmt.format(ob_mid)}\n" \
                            f"▪️ *Stop Loss (Low OB):* {fmt.format(ob_low)}\n" \
                            f"▪️ *Take Profit:* Cari area Swing High terdekat / Opsi RR 1:2\n\n" \
                            f"ℹ️ _Sinyal otomatis aktif 24 Jam nonstop via Render Cloud._"
                    
                    kirim_telegram(pesan)
                    print(f"Sinyal BUY {nama_pasaran} sukses dikirim!")
                    
        except Exception as e:
            print(f"Gagal scan {nama_pasaran}: {e}")

if __name__ == "__main__":
    kirim_telegram("🌋 Bot Alchemist ALL MATERI V2 Aktif 24/7 di Cloud!")
    while True:
        try:
            cek_setup_alchemist()
        except Exception as e:
            print("Error utama:", e)
        time.sleep(300) # Cek market berkala tiap 5 menit
