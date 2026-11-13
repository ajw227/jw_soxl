#!/usr/bin/env python3
"""
Fetch latest SOXL 1d data up to today using yfinance, update data/SOXL_1d.csv,
and write soxl_latest.json for static GitHub Pages consumption.
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import yfinance as yf


def main():
    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir / "data" / "SOXL_1d.csv"
    json_path = base_dir / "soxl_latest.json"

    df_old = pd.read_csv(csv_path)
    df_old["datetime"] = df_old["datetime"].astype(str).str.slice(0, 10)
    df_old["Close"] = pd.to_numeric(df_old["Close"], errors="coerce")
    df_old = df_old.dropna(subset=["Close"])

    ticker = yf.Ticker("SOXL")
    df_new = ticker.history(period="1mo")
    if not df_new.empty:
        df_new.index.name = "datetime"
        df_new = df_new.reset_index()
        df_new["datetime"] = df_new["datetime"].apply(lambda d: str(d)[:10])
        cols = ["datetime", "Close", "High", "Low", "Open", "Volume"]
        df_new = df_new[[c for c in cols if c in df_new.columns]]
        df_new["Close"] = pd.to_numeric(df_new["Close"], errors="coerce")
        df_new = df_new.dropna(subset=["Close"])
        combined = pd.concat([df_old, df_new], ignore_index=True)
    else:
        combined = df_old

    combined = combined.drop_duplicates(subset=["datetime"], keep="last")
    combined = combined.sort_values("datetime").reset_index(drop=True)
    combined.to_csv(csv_path, index=False)

    closes = combined["Close"].astype(float).tolist()
    dates = combined["datetime"].astype(str).tolist()
    n = len(closes)
    tail_start = max(0, n - 120)
    hist_dates = dates[tail_start:]
    hist_closes = [round(closes[i], 2) for i in range(tail_start, n)]
    hist_sma50 = [round(sum(closes[max(0, i - 49):i + 1]) / min(50, i + 1), 2) for i in range(tail_start, n)]
    hist_sma200 = [round(sum(closes[max(0, i - 199):i + 1]) / min(200, i + 1), 2) for i in range(tail_start, n)]

    latest = {
        "ok": True,
        "date": dates[-1],
        "price": round(closes[-1], 4),
        "sma50": round(sum(closes[-50:]) / len(closes[-50:]), 4),
        "sma200": round(sum(closes[-200:]) / len(closes[-200:]), 4),
        "history": {
            "dates": hist_dates,
            "closes": hist_closes,
            "sma50": hist_sma50,
            "sma200": hist_sma200,
        },
    }
    json_path.write_text(json.dumps(latest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated CSV ({len(combined)} rows) & soxl_latest.json: {latest}")


if __name__ == "__main__":
    main()
