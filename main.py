import os
import time
import requests
import pandas as pd
import numpy as np

# =======================================================
# TINGGAL GANTI DUA BARIS DI BAWAH INI PAKAI DATA LO
# =======================================================
TOKEN = "8839152051:AAHF5NIlFruU5ZsT5AymlliVlJGZLDapY2Q"  # <--- Ganti pakai Token Bot Telegram lo
CHAT_ID = "8440896866"                            # <--- Ganti pakai Chat ID Telegram lo
# =======================================================

INTERVAL = "1h" # HTF Level (1 Jam) Sesuai SOP Dokumen Alchemist

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

def hitung_advanced_alchemist(df, nama_market):
    # Mengambil data 48 bar untuk memetakan Market Structure & Liquidity Pools
    period = 48
    if len(df) < period:
        period = len(df)
    
    recent_df = df.tail(period).copy()
    
    # 1. Deteksi Liquidity Pool (Maksimum High dan Minimum Low murni)
    liq_high = recent_df['high'].max()
    liq_low = recent_df['low'].min()
    harga_sekarang = df['close'].iloc[-1]
    
    # 2. Cari Zona OCL (Open-Close Level) untuk validasi Hidden Base Order Block
    # Mendeteksi area body candle penutupan yang sejajar/sejajar terdekat
    recent_df['body_max'] = recent_df[['open', 'close']].max(axis=1)
    recent_df['body_min'] = recent_df[['open', 'close']].min(axis=1)
    
    ocl_resistance = recent_df['body_max'].max() # Batas atas OCL Base
    ocl_support = recent_df['body_min'].min()    # Batas bawah OCL Base
    
    # 3. Hitung 50% Midpoint Order Block (Equilibrium Zone) sesuai materi lo
    ob_mid_buy = (liq_low + ocl_support) / 2
    ob_mid_sell = (liq_high + ocl_resistance) / 2
    
    is_crypto_or_index = nama_market in ["BTCUSD", "NASDAQ"]
    
    # --- FORMULA TRADING MECHANICAL (ANTI LIQUIDITY SWEEP) ---
    
    # SETUP BUY (Menunggu Liquidity Sweep di bawah Low, Entry di 50% OB)
    if is_crypto_or_index:
        sl_buy = ob_mid_buy * 0.985 # SL 1.5% aman dari noise
        jarak_resiko_buy = ob_mid_buy - sl_buy
        tp_buy = ob_mid_buy + (jarak_resiko_buy * 2.5) # RR 1:2.5 Premium target
    else:
        pengali_pips = 0.1 if "JPY" in nama_market else 0.0050 if "USD" in nama_market else 5.0
        sl_buy = ob_mid_buy - pengali_pips # SL 50 Pips di bawah zona OB
        jarak_resiko_buy = ob_mid_buy - sl_buy
        tp_buy = ob_mid_buy + (jarak_resiko_buy * 2.5)

    # SETUP SELL (Menunggu Liquidity Sweep di atas High, Entry di 50% OB)
    if is_crypto_or_index:
        sl_sell = ob_mid_sell * 1.015 # SL 1.015%
        jarak_resiko_sell = sl_sell - ob_mid_sell
        tp_sell = ob_mid_sell - (jarak_resiko_sell * 2.5)
    else:
        pengali_pips = 0.1 if "JPY" in nama_market else 0.0050 if "USD" in nama_market else 5.0
        sl_sell = ob_mid_sell + pengali_pips # SL 50 Pips di atas zona OB
        jarak_resiko_sell = sl_sell - ob_mid_sell
        tp_sell = ob_mid_sell - (jarak_resiko_sell * 2.5)

    fmt = ".2f" if (is_crypto_or_index or "JPY" in nama_market or "XAU" in nama_market) else ".5f"

    pesan = f"🔮 *ALCHEMIST ADVANCED V4: {nama_market}*\n"
    pesan += f"Harga Saat Ini: `{harga_sekarang:{fmt}}`\n\n"
    pesan += f"🚨 *Liquidity Pools (HTF Target):*\n"
    pesan += f"   • Sell-Side Liq (High): `{liq_high:{fmt}}`\n"
    pesan += f"   • Buy-Side Liq (Low): `{liq_low:{fmt}}`\n\n"
    pesan += f"📦 *OCL Hidden Base Zone:*\n"
    pesan += f"   • Base Supply: `{ocl_resistance:{fmt}}`\n"
    pesan += f"   • Base Demand: `{ocl_support:{fmt}}`\n"
    pesan += f"─" * 15 + "\n"
    
    # Deteksi Setup Proporsional Berdasarkan Siklus Discount vs Premium Market
    if (harga_sekarang - liq_low) < (liq_high - harga_sekarang):
        pesan += f"💡 *INSTITUTIONAL SETUP: BUY LIMIT*\n"
        pesan += f"🟢 Entry (50% Mid OB): `{ob_mid_buy:{fmt}}`\n"
        pesan += f"🔴 Stop Loss (Protected): `{sl_buy:{fmt}}`\n"
        pesan += f"🔵 Take Profit (Premium): `{tp_buy:{fmt}}`\n"
    else:
        pesan += f"💡 *INSTITUTIONAL SETUP: SELL LIMIT*\n"
        pesan += f"🟢 Entry (50% Mid OB): `{ob_mid_sell:{fmt}}`\n"
        pesan += f"🔴 Stop Loss (Protected): `{sl_sell:{fmt}}`\n"
        pesan += f"🔵 Take Profit (Discount): `{tp_sell:{fmt}}`\n"
        
    pesan += f"⚠️ _SOP: Tunggu Liquidity Sweep terkonfirmasi, RR 1:2.5_\n\n"
    return pesan

def main():
    print("Memulai pemindaian kode Alchemist Advanced V4...")
    laporan_total = "🦅 *ALCHEMIST V4 ANTI-LIQUIDITY SCANNER* 🦅\n\n"
    
    for nama_market, simbol_yahoo in DAFTAR_MARKET.items():
        try:
            df = ambil_data(simbol_yahoo)
            laporan_market = hitung_advanced_alchemist(df, nama_market)
            laporan_total += laporan_market
            time.sleep(1)
        except Exception as e:
            print(f"Gagal memproses {nama_market}: {e}")
            
    kirim_telegram(laporan_total)
    print("Laporan Advanced Sniper V4 Sukses Dikirim!")

if __name__ == "__main__":
    main()
