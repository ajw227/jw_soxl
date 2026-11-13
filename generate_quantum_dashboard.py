#!/usr/bin/env python3
"""
Generate quantum_dashboard.html: Interactive SOXL Quant Dashboard with Custom Period Selector
"""
import json
from pathlib import Path
import pandas as pd

def main():
    csv_path = Path("data/SOXL_1d.csv")
    df = pd.read_csv(csv_path)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.dropna(subset=["Close"]).drop_duplicates(subset=["datetime"], keep="last")
    df = df.sort_values("datetime").reset_index(drop=True)
    df["SMA200"] = df["Close"].rolling(200).mean().fillna(df["Close"])
    df["SMA50"] = df["Close"].rolling(50).mean().fillna(df["Close"])
    df["STD50"] = df["Close"].rolling(50).std().fillna(df["Close"] * 0.1)
    df["Z50"] = ((df["Close"] - df["SMA50"]) / df["STD50"]).fillna(0.0)
    df["Disparity200"] = (df["Close"] / df["SMA200"]).fillna(1.0)

    # Extract all historical bars
    bars = []
    for _, r in df.iterrows():
        bars.append([
            str(r["datetime"])[:10],
            round(float(r["Close"]), 4),
            round(float(r["SMA200"]), 4),
            round(float(r["SMA50"]), 4),
            round(float(r["Z50"]), 4),
            round(float(r["Disparity200"]), 4)
        ])

    json_bars = json.dumps(bars)

    html_content = f"""<!DOCTYPE html>
<html lang="ko" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JW 퀀트 히스테리시스 실전 백테스트 대시보드</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {{
      darkMode: "class",
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ["Pretendard", "system-ui", "-apple-system", "sans-serif"],
            mono: ["JetBrains Mono", "monospace"]
          }},
          colors: {{
            brand: {{ 50: "#eef2ff", 100: "#e0e7ff", 500: "#6366f1", 600: "#4f46e5", 700: "#4338ca" }}
          }}
        }}
      }}
    }}
  </script>
  <style>
    body {{ background-color: #080c14; color: #e2e8f0; }}
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: #0b0f19; }}
    ::-webkit-scrollbar-thumb {{ background: #26334d; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #3b4d6e; }}
    .glass-panel {{ background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }}
    .btn-preset {{ background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); transition: all 0.15s ease; }}
    .btn-preset:hover {{ background: rgba(79, 70, 229, 0.3); border-color: rgba(99, 102, 241, 0.5); color: #fff; }}
    .btn-preset.active {{ background: #4f46e5; border-color: #6366f1; color: #fff; font-weight: 700; }}
    .tab-btn.active {{ border-bottom: 2px solid #6366f1; color: #818cf8; font-weight: 700; }}
  </style>
</head>
<body class="font-sans antialiased text-slate-200 min-h-screen pb-20 selection:bg-indigo-500 selection:text-white">

  <!-- Header -->
  <header class="border-b border-slate-800/80 bg-slate-950/80 sticky top-0 z-50 backdrop-blur-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-emerald-400 flex items-center justify-center text-lg font-black shadow-lg shadow-indigo-500/25">⚡</span>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-base sm:text-lg font-bold tracking-tight text-white">JW 퀀트 히스테리시스 + 수학 퀀트 대시보드</h1>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">Mathematix v2.5</span>
            <span class="text-[10px] font-medium px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">과열익절(D200≥1.6) & 바닥손절차단(Z50&lt;-1.5)</span>
          </div>
          <p class="text-[11px] text-slate-400">극단 과매도 바닥 손절 차단 + 200 SMA 버블 이격도 30% 분할 익절 수학 모델 실시간 백테스트</p>
        </div>
      </div>
      <div class="flex items-center gap-2 text-xs">
        <a href="orders.html" class="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-3 py-1.5 rounded-lg transition shadow-sm">
          <span>📋</span>
          <span>실전 주문표</span>
        </a>
        <div class="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-300">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>자산: <strong>SOXL 1D</strong></span>
        </div>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 space-y-6">

    <!-- Control Bar: Period Selection & Capital -->
    <div class="glass-panel rounded-2xl p-5 space-y-4 shadow-xl">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        
        <!-- Preset Buttons -->
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-xs font-semibold text-slate-400 mr-1">⚡ 빠른 기간:</span>
          <button class="btn-preset active px-3 py-1.5 rounded-lg text-xs" onclick="setPreset('2026-01-02', 'latest', this)">2026 (올해 YTD)</button>
          <button class="btn-preset px-3 py-1.5 rounded-lg text-xs" onclick="setPreset('2025-01-01', '2025-12-31', this)">2025 (전년도)</button>
          <button class="btn-preset px-3 py-1.5 rounded-lg text-xs" onclick="setPreset('2025-01-01', 'latest', this)">최근 2년 (2025~2026)</button>
          <button class="btn-preset px-3 py-1.5 rounded-lg text-xs" onclick="setPreset('2024-01-01', '2024-12-31', this)">2024 (롤러코스터)</button>
          <button class="btn-preset px-3 py-1.5 rounded-lg text-xs" onclick="setPreset('2022-01-01', '2022-12-31', this)">2022 (대폭락장)</button>
          <button class="btn-preset px-3 py-1.5 rounded-lg text-xs" onclick="setPreset('2020-01-01', 'latest', this)">최근 7년 (2020~2026)</button>
          <button class="btn-preset px-3 py-1.5 rounded-lg text-xs" onclick="setPreset('2010-03-11', 'latest', this)">16년 전체 (2010~2026)</button>
        </div>

        <!-- Custom Date Range & Capital Inputs -->
        <div class="flex flex-wrap items-center gap-3">
          <div class="flex items-center gap-2 bg-slate-900/90 border border-slate-700/80 rounded-xl px-3 py-1.5">
            <span class="text-xs text-slate-400">기간:</span>
            <input type="date" id="inStartDate" value="2026-01-02" class="bg-transparent text-xs text-white font-mono focus:outline-none">
            <span class="text-slate-500 text-xs">~</span>
            <input type="date" id="inEndDate" value="2026-11-02" class="bg-transparent text-xs text-white font-mono focus:outline-none">
          </div>

          <div class="flex items-center gap-2 bg-slate-900/90 border border-slate-700/80 rounded-xl px-3 py-1.5">
            <span class="text-xs text-slate-400">시작 원금:</span>
            <span class="text-xs text-slate-400">$</span>
            <input type="number" id="inCapital" value="10000" step="1000" class="w-20 bg-transparent text-xs text-white font-mono focus:outline-none">
          </div>

          <button onclick="applyFilters()" class="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white text-xs font-bold shadow-md shadow-indigo-500/20 transition">
            🚀 백테스트 실행
          </button>
        </div>

      </div>
    </div>

    <!-- Summary KPI Cards -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
      <div class="glass-panel rounded-2xl p-4">
        <p class="text-[11px] text-slate-400 font-medium">최종 자산</p>
        <h3 id="kpiFinalEquity" class="text-lg sm:text-xl font-bold font-mono text-white mt-1">$0</h3>
        <p id="kpiNetProfit" class="text-[11px] font-mono mt-1 text-slate-400">순익 $0</p>
      </div>

      <div class="glass-panel rounded-2xl p-4">
        <p class="text-[11px] text-slate-400 font-medium">전략 수익률</p>
        <h3 id="kpiTotalReturn" class="text-lg sm:text-xl font-bold font-mono text-emerald-400 mt-1">+0.0%</h3>
        <p id="kpiSoxlBnh" class="text-[11px] font-mono mt-1 text-slate-400">SOXL B&H: +0.0%</p>
      </div>

      <div class="glass-panel rounded-2xl p-4">
        <p class="text-[11px] text-slate-400 font-medium">최대 낙폭 (MDD)</p>
        <h3 id="kpiMDD" class="text-lg sm:text-xl font-bold font-mono text-rose-400 mt-1">-0.0%</h3>
        <p id="kpiSoxlMdd" class="text-[11px] font-mono mt-1 text-slate-400">SOXL B&H: -0.0%</p>
      </div>

      <div class="glass-panel rounded-2xl p-4">
        <p class="text-[11px] text-slate-400 font-medium">총 실현 순익</p>
        <h3 id="kpiRealizedPnL" class="text-lg sm:text-xl font-bold font-mono text-indigo-400 mt-1">+$0</h3>
        <p id="kpiSellTradesCount" class="text-[11px] font-mono mt-1 text-slate-400">매도 0건</p>
      </div>

      <div class="glass-panel rounded-2xl p-4">
        <p class="text-[11px] text-slate-400 font-medium">승률 & 손익비</p>
        <h3 id="kpiWinRate" class="text-lg sm:text-xl font-bold font-mono text-amber-400 mt-1">0.0%</h3>
        <p id="kpiPayoff" class="text-[11px] font-mono mt-1 text-slate-400">손익비: 0.0x</p>
      </div>

      <div class="glass-panel rounded-2xl p-4">
        <p class="text-[11px] text-slate-400 font-medium">완료 사이클 / 매매</p>
        <h3 id="kpiCycles" class="text-lg sm:text-xl font-bold font-mono text-cyan-400 mt-1">0회</h3>
        <p id="kpiTotalTrades" class="text-[11px] font-mono mt-1 text-slate-400">총 0회 체결</p>
      </div>
    </div>

    <!-- Charts Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Equity Chart -->
      <div class="lg:col-span-2 glass-panel rounded-2xl p-5 space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-sm font-bold text-white flex items-center gap-2">
              <span>📈 자산 성장 곡선 (Equity Curve)</span>
              <span class="text-[10px] text-slate-400 font-normal">전략 vs SOXL 단순보유</span>
            </h2>
          </div>
          <div class="flex items-center gap-3 text-xs font-mono">
            <span class="flex items-center gap-1.5"><span class="w-3 h-0.5 bg-indigo-500 rounded"></span> JW 퀀트</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-0.5 bg-slate-500 rounded"></span> SOXL B&H</span>
          </div>
        </div>
        <div class="h-72 w-full">
          <canvas id="chartEquity"></canvas>
        </div>
      </div>

      <!-- Asset Allocation Breakdown Chart -->
      <div class="glass-panel rounded-2xl p-5 space-y-3">
        <div class="flex items-center justify-between">
          <h2 class="text-sm font-bold text-white">💼 포트폴리오 자산 구성 (%)</h2>
          <span class="text-[10px] text-slate-400">현금 vs 앵커 vs 그리드</span>
        </div>
        <div class="h-72 w-full">
          <canvas id="chartAllocation"></canvas>
        </div>
      </div>
    </div>

    <!-- Details Section with Tabs -->
    <div class="glass-panel rounded-2xl p-5 space-y-4">
      <div class="sticky top-16 z-30 bg-slate-900/95 backdrop-blur-md pb-3 pt-1 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <!-- Tabs -->
        <div class="flex items-center gap-6 text-sm">
          <button id="tabBtn1" class="tab-btn active pb-2 font-medium transition" onclick="switchTab(1)">
            💰 매도 실현 손익 장부 (<span id="countSellTrades">0</span>건)
          </button>
          <button id="tabBtn2" class="tab-btn pb-2 font-medium text-slate-400 hover:text-slate-200 transition" onclick="switchTab(2)">
            📜 전체 체결 내역 (<span id="countAllTrades">0</span>건)
          </button>
          <button id="tabBtn3" class="tab-btn pb-2 font-medium text-slate-400 hover:text-slate-200 transition" onclick="switchTab(3)">
            📅 일별 계좌 장부 (<span id="countDailyRows">0</span>일)
          </button>
          <button id="tabBtn4" class="tab-btn pb-2 font-medium text-slate-400 hover:text-slate-200 transition" onclick="switchTab(4)">
            🗓️ 월별 성과 요약
          </button>
        </div>

        <!-- Export CSV Button -->
        <button onclick="exportCurrentTableCsv()" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 border border-slate-700 self-end sm:self-auto shadow-sm">
          <span>📥</span> <span>Excel CSV 다운로드</span>
        </button>
      </div>

      <!-- Tab Content 1: Sell Realized PnL Table -->
      <div id="tabContent1" class="tab-content overflow-x-auto max-h-[70vh] overflow-y-auto rounded-xl border border-slate-800/80">
        <table class="w-full text-left text-xs font-mono">
          <thead class="sticky top-0 z-20 bg-slate-950/95 backdrop-blur-md text-slate-300 border-b border-slate-700/80 shadow-md">
            <tr>
              <th class="py-2.5 px-3">#</th>
              <th class="py-2.5 px-3">체결일자</th>
              <th class="py-2.5 px-3">포지션</th>
              <th class="py-2.5 px-3 text-right">수량</th>
              <th class="py-2.5 px-3 text-right">매수평단</th>
              <th class="py-2.5 px-3 text-right">매도단가</th>
              <th class="py-2.5 px-3 text-right font-bold">실현 손익 ($)</th>
              <th class="py-2.5 px-3 text-right font-bold">수익률 (%)</th>
              <th class="py-2.5 px-3 text-right">누적 실현순익</th>
              <th class="py-2.5 px-3">매매 사유</th>
            </tr>
          </thead>
          <tbody id="tbodySellTrades" class="divide-y divide-slate-800/60 text-slate-300">
          </tbody>
        </table>
      </div>

      <!-- Tab Content 2: All Trades Table -->
      <div id="tabContent2" class="tab-content hidden overflow-x-auto max-h-[70vh] overflow-y-auto rounded-xl border border-slate-800/80">
        <table class="w-full text-left text-xs font-mono">
          <thead class="sticky top-0 z-20 bg-slate-950/95 backdrop-blur-md text-slate-300 border-b border-slate-700/80 shadow-md">
            <tr>
              <th class="py-2.5 px-3">#</th>
              <th class="py-2.5 px-3">체결일자</th>
              <th class="py-2.5 px-3">포지션</th>
              <th class="py-2.5 px-3">구분</th>
              <th class="py-2.5 px-3 text-right">수량</th>
              <th class="py-2.5 px-3 text-right">체결단가</th>
              <th class="py-2.5 px-3 text-right">거래금액</th>
              <th class="py-2.5 px-3">체결 사유</th>
            </tr>
          </thead>
          <tbody id="tbodyAllTrades" class="divide-y divide-slate-800/60 text-slate-300">
          </tbody>
        </table>
      </div>

      <!-- Tab Content 3: Daily Ledger Table -->
      <div id="tabContent3" class="tab-content hidden overflow-x-auto max-h-[70vh] overflow-y-auto rounded-xl border border-slate-800/80">
        <table class="w-full text-left text-xs font-mono">
          <thead class="sticky top-0 z-20 bg-slate-950/95 backdrop-blur-md text-slate-300 border-b border-slate-700/80 shadow-md">
            <tr>
              <th class="py-2.5 px-3">일자</th>
              <th class="py-2.5 px-3 text-right">SOXL 종가</th>
              <th class="py-2.5 px-3 text-right">앵커(코어)</th>
              <th class="py-2.5 px-3 text-right">그리드</th>
              <th class="py-2.5 px-3 text-right">총 수량</th>
              <th class="py-2.5 px-3 text-right">통합 평단가</th>
              <th class="py-2.5 px-3 text-right">평단 대비</th>
              <th class="py-2.5 px-3 text-right">현금 잔고</th>
              <th class="py-2.5 px-3 text-right font-bold">계좌 총 평가액</th>
              <th class="py-2.5 px-3 text-right">MDD</th>
            </tr>
          </thead>
          <tbody id="tbodyDaily" class="divide-y divide-slate-800/60 text-slate-300">
          </tbody>
        </table>
      </div>

      <!-- Tab Content 4: Monthly Matrix -->
      <div id="tabContent4" class="tab-content hidden overflow-x-auto max-h-[70vh] overflow-y-auto rounded-xl border border-slate-800/80">
        <table class="w-full text-left text-xs font-mono">
          <thead class="sticky top-0 z-20 bg-slate-950/95 backdrop-blur-md text-slate-300 border-b border-slate-700/80 shadow-md">
            <tr>
              <th class="py-2.5 px-3">연월</th>
              <th class="py-2.5 px-3 text-right">SOXL 종가</th>
              <th class="py-2.5 px-3 text-right">SOXL 월간</th>
              <th class="py-2.5 px-3 text-right font-bold">월말 평가액</th>
              <th class="py-2.5 px-3 text-right font-bold">월간 수익률</th>
              <th class="py-2.5 px-3 text-right">누적 수익률</th>
              <th class="py-2.5 px-3 text-right">월말 현금</th>
              <th class="py-2.5 px-3 text-right">월말 보유량</th>
            </tr>
          </thead>
          <tbody id="tbodyMonthly" class="divide-y divide-slate-800/60 text-slate-300">
          </tbody>
        </table>
      </div>

    </div>

  </main>

  <script>
    // -------------------------------------------------------------
    // Raw Historical Bars [date, close, sma200, sma50]
    // -------------------------------------------------------------
    const ALL_BARS = {json_bars};

    // State
    let currentTrades = [];
    let currentDaily = [];
    let currentMonthly = [];
    let chartEquityInstance = null;
    let chartAllocInstance = null;

    // Initialize
    window.addEventListener("DOMContentLoaded", () => {{
      const latestDate = ALL_BARS[ALL_BARS.length - 1][0];
      document.getElementById("inEndDate").value = latestDate;
      document.getElementById("inEndDate").max = latestDate;
      applyFilters();
    }});

    function setPreset(start, end, btn) {{
      document.querySelectorAll(".btn-preset").forEach(b => b.classList.remove("active"));
      if (btn) btn.classList.add("active");

      const latestDate = ALL_BARS[ALL_BARS.length - 1][0];
      document.getElementById("inStartDate").value = start;
      document.getElementById("inEndDate").value = (end === "latest") ? latestDate : end;
      applyFilters();
    }}

    function switchTab(idx) {{
      for (let i = 1; i <= 4; i++) {{
        document.getElementById(`tabBtn${{i}}`).classList.remove("active", "text-indigo-400");
        document.getElementById(`tabContent${{i}}`).classList.add("hidden");
      }}
      document.getElementById(`tabBtn${{idx}}`).classList.add("active");
      document.getElementById(`tabContent${{idx}}`).classList.remove("hidden");
    }}

    // -------------------------------------------------------------
    // Core Quantum Hysteresis Simulation Engine
    // -------------------------------------------------------------
    function runQuantumEngine(bars, initialCapital) {{
      let cash = initialCapital;
      let anchorQty = 0;
      let anchorAvgPrice = 0.0;
      let gridQty = 0;
      let gridAvgPrice = 0.0;
      let runnerQty = 0;
      let runnerAvgPrice = 0.0;
      let runnerPeak = 0.0;

      const gridSplit = 14;
      const gridTarget = 24.0;
      let gridOrderUnit = (initialCapital * 0.5) / gridSplit;
      let gridStartCash = cash * 0.5;
      let cycles = 0;
      let overheatTrims = 0;
      let reversionGateBlocks = 0;

      const trades = [];
      const daily = [];
      let cumRealizedPnL = 0.0;

      for (let i = 0; i < bars.length; i++) {{
        const [currDate, c, sma200, sma50, z50, disp200] = bars[i];
        const totalEquity = cash + (anchorQty + gridQty + runnerQty) * c;

        // 1. Hysteresis Anchor + Overheat Trim
        let targetRatio = 0.15;
        if (c >= sma200 * 1.02 && c >= sma50) {{
          targetRatio = 0.50;
        }} else if (c >= sma200 * 0.95) {{
          targetRatio = (anchorQty > 0) ? 0.30 : 0.0;
        }} else {{
          targetRatio = 0.15; // floor
        }}

        // [수학 1] 과열 분할 익절 (Overheat Trim): 200 SMA 대비 +60% 괴리 시 앵커 30% 현금화
        if (disp200 >= 1.60 && anchorQty > 0) {{
          targetRatio *= 0.70;
        }}

        const targetVal = totalEquity * targetRatio;
        const currentVal = anchorQty * c;

        if (targetVal > currentVal * 1.15) {{
          const diff = Math.min(targetVal - currentVal, totalEquity * 0.05); // 1일 최대 5% 스프레드 적립
          const bQty = Math.floor(diff / c);
          if (bQty > 0 && cash >= bQty * c) {{
            const cost = bQty * c;
            cash -= cost;
            anchorAvgPrice = (anchorAvgPrice * anchorQty + cost) / (anchorQty + bQty);
            anchorQty += bQty;
            trades.push({{
              date: currDate, side: "BUY", type: "ANCHOR", qty: bQty, price: c,
              costBasis: anchorAvgPrice, pnl: 0.0, retPct: 0.0, cumPnL: cumRealizedPnL,
              reason: "앵커 점진 보충"
            }});
          }}
        }} else if (targetVal < currentVal * 0.85 && anchorQty > 0) {{
          const diff = currentVal - targetVal;
          let sQty = Math.floor(diff / c);
          sQty = Math.min(sQty, Math.floor(anchorQty * 0.30));
          if (sQty > 0) {{
            const proceeds = sQty * c;
            cash += proceeds;
            const pnl = (c - anchorAvgPrice) * sQty;
            const retPct = anchorAvgPrice > 0 ? ((c - anchorAvgPrice) / anchorAvgPrice) * 100.0 : 0.0;
            cumRealizedPnL += pnl;
            const sellReason = disp200 >= 1.60 ? `앵커 과열 분할 익절 (이격도 ${{disp200.toFixed(2)}})` : "앵커 분할 축소 (휩소방지)";
            if (disp200 >= 1.60) overheatTrims++;
            trades.push({{
              date: currDate, side: "SELL", type: "ANCHOR", qty: sQty, price: c,
              costBasis: anchorAvgPrice, pnl: pnl, retPct: retPct, cumPnL: cumRealizedPnL,
              reason: sellReason
            }});
            anchorQty -= sQty;
          }}
        }}

        // 2. Runner Exit
        if (runnerQty > 0) {{
          if (c > runnerPeak) runnerPeak = c;
          const dropPct = ((runnerPeak - c) / runnerPeak) * 100.0;
          if (dropPct >= 6.5) {{
            const proceeds = runnerQty * c;
            cash += proceeds;
            const pnl = (c - runnerAvgPrice) * runnerQty;
            const retPct = runnerAvgPrice > 0 ? ((c - runnerAvgPrice) / runnerAvgPrice) * 100.0 : 0.0;
            cumRealizedPnL += pnl;
            trades.push({{
              date: currDate, side: "SELL", type: "RUNNER", qty: runnerQty, price: c,
              costBasis: runnerAvgPrice, pnl: pnl, retPct: retPct, cumPnL: cumRealizedPnL,
              reason: `런너 트레일링 엑시트 (-${{dropPct.toFixed(1)}}%)`
            }});
            runnerQty = 0;
            runnerPeak = 0.0;
          }}
        }}

        // 3. Grid Sells & Reversion Gate
        if (gridQty > 0) {{
          const gainPct = ((c - gridAvgPrice) / gridAvgPrice) * 100.0;
          const remPrincipal = Math.max(0.0, (initialCapital * 0.5) - (gridQty * gridAvgPrice));
          const remPct = (remPrincipal / (initialCapital * 0.5)) * 100.0;

          if (gainPct >= gridTarget) {{
            const proceeds = gridQty * c;
            cash += proceeds;
            const pnl = (c - gridAvgPrice) * gridQty;
            cumRealizedPnL += pnl;
            trades.push({{
              date: currDate, side: "SELL", type: "GRID", qty: gridQty, price: c,
              costBasis: gridAvgPrice, pnl: pnl, retPct: gainPct, cumPnL: cumRealizedPnL,
              reason: `그리드 목표 익절 (+${{gainPct.toFixed(1)}}%)`
            }});
            const keepRunner = Math.floor(gridQty * 0.25);
            gridQty = 0;
            runnerQty = keepRunner;
            runnerAvgPrice = gridAvgPrice;
            runnerPeak = c;
            cash -= runnerQty * c;
            gridAvgPrice = 0.0;
            cycles += 1;
            gridOrderUnit = (cash * 0.5) / gridSplit;
            gridStartCash = cash * 0.5;
          }} else if (remPct < 50.0) {{
            // [수학 2] 과매도 손절 차단 (Reversion Gate): Z-score < -1.5 극단 바닥 시 손절 차단
            if (z50 < -1.5) {{
              reversionGateBlocks++;
            }} else {{
              const qCut = Math.floor(gridQty * 0.25);
              if (qCut > 0) {{
                const proceeds = qCut * c;
                cash += proceeds;
                const pnl = (c - gridAvgPrice) * qCut;
                const retPct = ((c - gridAvgPrice) / gridAvgPrice) * 100.0;
                cumRealizedPnL += pnl;
                trades.push({{
                  date: currDate, side: "SELL", type: "GRID", qty: qCut, price: c,
                  costBasis: gridAvgPrice, pnl: pnl, retPct: retPct, cumPnL: cumRealizedPnL,
                  reason: `별률 쿼터 매도 (${{retPct.toFixed(1)}}%)`
                }});
                gridQty -= qCut;
              }}
            }}
          }}
        }}

        // 4. Grid Buys
        const effOrderUnit = gridOrderUnit;
        const remPrincipal = Math.max(0.0, (initialCapital * 0.5) - (gridQty * gridAvgPrice));
        const remPct = (remPrincipal / (initialCapital * 0.5)) * 100.0;

        const valA = 1.0 + 0.05 / 2.0;
        const valB = 1.0 - (0.05 / 2.0) * Math.pow(remPct / 100.0, 1.5);
        const priceStar = gridAvgPrice > 0 ? gridAvgPrice * valA * valB : c;
        const priceLarge = gridAvgPrice > 0 ? gridAvgPrice * 1.15 : c;

        if (gridQty === 0 && runnerQty === 0) {{
          const qty = Math.floor(effOrderUnit / c);
          if (qty > 0 && cash >= qty * c) {{
            const cost = qty * c;
            cash -= cost;
            gridQty = qty;
            gridAvgPrice = c;
            trades.push({{
              date: currDate, side: "BUY", type: "GRID", qty: qty, price: c,
              costBasis: gridAvgPrice, pnl: 0.0, retPct: 0.0, cumPnL: cumRealizedPnL,
              reason: "그리드 1회차 매수"
            }});
          }}
        }} else {{
          if (remPrincipal > 0) {{
            const budget = (remPct < 50) ? (effOrderUnit / 2) : Math.min(remPrincipal, effOrderUnit);
            const starQty = priceStar > 0 ? Math.floor(budget / priceStar) : 0;
            const largeQty = priceLarge > 0 ? Math.floor((effOrderUnit / 2) / priceLarge) : 0;

            if (starQty > 0 && priceStar >= c && cash >= starQty * c) {{
              const cost = starQty * c;
              cash -= cost;
              gridAvgPrice = (gridAvgPrice * gridQty + cost) / (gridQty + starQty);
              gridQty += starQty;
              trades.push({{
                date: currDate, side: "BUY", type: "GRID", qty: starQty, price: c,
                costBasis: gridAvgPrice, pnl: 0.0, retPct: 0.0, cumPnL: cumRealizedPnL,
                reason: "별률 분할 매수"
              }});
            }}
            if (largeQty > 0 && priceLarge >= c && cash >= largeQty * c) {{
              const cost = largeQty * c;
              cash -= cost;
              gridAvgPrice = (gridAvgPrice * gridQty + cost) / (gridQty + largeQty);
              gridQty += largeQty;
              trades.push({{
                date: currDate, side: "BUY", type: "GRID", qty: largeQty, price: c,
                costBasis: gridAvgPrice, pnl: 0.0, retPct: 0.0, cumPnL: cumRealizedPnL,
                reason: "장대양봉 추격 매수"
              }});
            }}
          }}
        }}

        const totHolding = anchorQty + gridQty + runnerQty;
        const eq = cash + totHolding * c;
        const totAvg = totHolding > 0 ? ((anchorQty * anchorAvgPrice) + (gridQty * gridAvgPrice)) / totHolding : 0.0;
        const retVsAvg = totAvg > 0 ? ((c - totAvg) / totAvg) * 100.0 : 0.0;

        daily.push({{
          date: currDate, close: c, cash: cash, anchorQty: anchorQty, anchorAvg: anchorAvgPrice,
          gridQty: gridQty, gridAvg: gridAvgPrice, runnerQty: runnerQty, totHolding: totHolding,
          totAvg: totAvg, retVsAvg: retVsAvg, equity: eq, cumPnL: cumRealizedPnL
        }});
      }}

      // Compute Peak & DD
      let peak = 0.0;
      let maxDD = 0.0;
      for (let i = 0; i < daily.length; i++) {{
        if (daily[i].equity > peak) peak = daily[i].equity;
        const dd = ((daily[i].equity - peak) / peak) * 100.0;
        daily[i].peak = peak;
        daily[i].dd = dd;
        if (dd < maxDD) maxDD = dd;
      }}

      return {{ trades, daily, cycles, maxDD, overheatTrims, reversionGateBlocks }};
    }}

    // -------------------------------------------------------------
    // Apply Filters & Update View
    // -------------------------------------------------------------
    function applyFilters() {{
      const start = document.getElementById("inStartDate").value;
      const end = document.getElementById("inEndDate").value;
      const capital = parseFloat(document.getElementById("inCapital").value) || 10000.0;

      const subBars = ALL_BARS.filter(b => b[0] >= start && b[0] <= end);
      if (subBars.length === 0) {{
        alert("선택하신 기간에 해당하는 거래일 데이터가 없습니다.");
        return;
      }}

      const result = runQuantumEngine(subBars, capital);
      currentTrades = result.trades;
      currentDaily = result.daily;

      // Update KPI
      const finalEq = currentDaily[currentDaily.length - 1].equity;
      const totalProfit = finalEq - capital;
      const totalRet = (totalProfit / capital) * 100.0;

      const soxlStart = subBars[0][1];
      const soxlEnd = subBars[subBars.length - 1][1];
      const soxlBnh = ((soxlEnd - soxlStart) / soxlStart) * 100.0;

      // SOXL MDD
      let soxlPeak = 0.0;
      let soxlMdd = 0.0;
      for (let b of subBars) {{
        if (b[1] > soxlPeak) soxlPeak = b[1];
        const dd = ((b[1] - soxlPeak) / soxlPeak) * 100.0;
        if (dd < soxlMdd) soxlMdd = dd;
      }}

      // Sells & Win Rate
      const sellTrades = currentTrades.filter(t => t.side === "SELL");
      const wins = sellTrades.filter(t => t.pnl > 0);
      const losses = sellTrades.filter(t => t.pnl < 0);
      const winRate = sellTrades.length > 0 ? (wins.length / sellTrades.length) * 100.0 : 0.0;
      const totRealized = sellTrades.reduce((acc, t) => acc + t.pnl, 0.0);

      const avgWin = wins.length > 0 ? wins.reduce((acc, t) => acc + t.pnl, 0.0) / wins.length : 0.0;
      const avgLoss = losses.length > 0 ? Math.abs(losses.reduce((acc, t) => acc + t.pnl, 0.0) / losses.length) : 0.0;
      const payoff = avgLoss > 0 ? (avgWin / avgLoss) : 0.0;

      // Render KPIs
      document.getElementById("kpiFinalEquity").textContent = `$${{Math.round(finalEq).toLocaleString()}}`;
      document.getElementById("kpiNetProfit").textContent = `순익 ${{totalProfit >= 0 ? '+' : ''}}$${{Math.round(totalProfit).toLocaleString()}}`;
      
      document.getElementById("kpiTotalReturn").textContent = `${{totalRet >= 0 ? '+' : ''}}${{totalRet.toFixed(2)}}%`;
      document.getElementById("kpiTotalReturn").className = `text-lg sm:text-xl font-bold font-mono mt-1 ${{totalRet >= 0 ? 'text-emerald-400' : 'text-rose-400'}}`;
      document.getElementById("kpiSoxlBnh").textContent = `SOXL B&H: ${{soxlBnh >= 0 ? '+' : ''}}${{soxlBnh.toFixed(1)}}%`;

      document.getElementById("kpiMDD").textContent = `${{result.maxDD.toFixed(1)}}%`;
      document.getElementById("kpiSoxlMdd").textContent = `SOXL B&H: ${{soxlMdd.toFixed(1)}}%`;

      document.getElementById("kpiRealizedPnL").textContent = `${{totRealized >= 0 ? '+' : ''}}$${{Math.round(totRealized).toLocaleString()}}`;
      document.getElementById("kpiSellTradesCount").textContent = `매도 ${{sellTrades.length}}건 (익절 ${{wins.length}} / 손절 ${{losses.length}})`;

      document.getElementById("kpiWinRate").textContent = `${{winRate.toFixed(1)}}%`;
      document.getElementById("kpiPayoff").textContent = `손익비: ${{payoff.toFixed(2)}}x`;

      document.getElementById("kpiCycles").textContent = `${{result.cycles}}회`;
      document.getElementById("kpiTotalTrades").textContent = `총 ${{currentTrades.length}}회 (과열익절 ${{result.overheatTrims}}회 / 바닥보호 ${{result.reversionGateBlocks}}회)`;

      document.getElementById("countSellTrades").textContent = sellTrades.length;
      document.getElementById("countAllTrades").textContent = currentTrades.length;
      document.getElementById("countDailyRows").textContent = currentDaily.length;

      renderCharts(subBars, capital);
      renderTables();
    }}

    // -------------------------------------------------------------
    // Charts Rendering
    // -------------------------------------------------------------
    function renderCharts(subBars, capital) {{
      const labels = currentDaily.map(d => d.date);
      const stratEquity = currentDaily.map(d => d.equity);
      
      const soxl0 = subBars[0][1];
      const bnhEquity = subBars.map(b => (b[1] / soxl0) * capital);

      // 1. Equity Curve
      const ctxEq = document.getElementById("chartEquity").getContext("2d");
      if (chartEquityInstance) chartEquityInstance.destroy();

      chartEquityInstance = new Chart(ctxEq, {{
        type: "line",
        data: {{
          labels: labels,
          datasets: [
            {{
              label: "JW 퀀트 전략 자산 ($)",
              data: stratEquity,
              borderColor: "#6366f1",
              backgroundColor: "rgba(99, 102, 241, 0.1)",
              borderWidth: 2,
              fill: true,
              pointRadius: 0,
              tension: 0.1
            }},
            {{
              label: "SOXL 단순보유 자산 ($)",
              data: bnhEquity,
              borderColor: "#64748b",
              borderWidth: 1.5,
              borderDash: [4, 4],
              pointRadius: 0,
              tension: 0.1
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          interaction: {{ mode: "index", intersect: false }},
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              callbacks: {{
                label: (ctx) => `${{ctx.dataset.label}}: $${{Math.round(ctx.parsed.y).toLocaleString()}}`
              }}
            }}
          }},
          scales: {{
            x: {{ grid: {{ display: false }}, ticks: {{ maxTicksLimit: 8, color: "#64748b", font: {{ size: 10 }} }} }},
            y: {{ grid: {{ color: "rgba(255,255,255,0.05)" }}, ticks: {{ color: "#64748b", font: {{ size: 10 }}, callback: (v) => `$${{v.toLocaleString()}}` }} }}
          }}
        }}
      }});

      // 2. Asset Allocation Breakdown Chart
      const ctxAlloc = document.getElementById("chartAllocation").getContext("2d");
      if (chartAllocInstance) chartAllocInstance.destroy();

      const cashPct = currentDaily.map(d => (d.cash / d.equity) * 100.0);
      const anchorPct = currentDaily.map(d => ((d.anchorQty * d.close) / d.equity) * 100.0);
      const gridPct = currentDaily.map(d => (((d.gridQty + d.runnerQty) * d.close) / d.equity) * 100.0);

      chartAllocInstance = new Chart(ctxAlloc, {{
        type: "line",
        data: {{
          labels: labels,
          datasets: [
            {{ label: "현금 비중 (%)", data: cashPct, borderColor: "#10b981", backgroundColor: "rgba(16, 185, 129, 0.2)", fill: true, pointRadius: 0 }},
            {{ label: "앵커 비중 (%)", data: anchorPct, borderColor: "#6366f1", backgroundColor: "rgba(99, 102, 241, 0.2)", fill: true, pointRadius: 0 }},
            {{ label: "그리드 비중 (%)", data: gridPct, borderColor: "#f59e0b", backgroundColor: "rgba(245, 158, 11, 0.2)", fill: true, pointRadius: 0 }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          interaction: {{ mode: "index", intersect: false }},
          plugins: {{
            legend: {{ labels: {{ color: "#94a3b8", font: {{ size: 10 }} }} }},
            tooltip: {{ callbacks: {{ label: (ctx) => `${{ctx.dataset.label}}: ${{ctx.parsed.y.toFixed(1)}}%` }} }}
          }},
          scales: {{
            x: {{ grid: {{ display: false }}, ticks: {{ maxTicksLimit: 6, color: "#64748b", font: {{ size: 10 }} }} }},
            y: {{ stacked: true, max: 100, min: 0, grid: {{ color: "rgba(255,255,255,0.05)" }}, ticks: {{ color: "#64748b", callback: (v) => `${{v}}%` }} }}
          }}
        }}
      }});
    }}

    // -------------------------------------------------------------
    // Tables Rendering
    // -------------------------------------------------------------
    function renderTables() {{
      // 1. Sell Trades Table
      const sellTrades = currentTrades.filter(t => t.side === "SELL");
      const tbodySell = document.getElementById("tbodySellTrades");
      tbodySell.innerHTML = sellTrades.map((t, idx) => {{
        const isWin = t.pnl >= 0;
        const typeBadge = t.reason.includes("과열")
          ? `<span class="px-2 py-0.5 rounded text-[10px] bg-orange-500/20 text-orange-300 border border-orange-500/30 font-bold">🔥 과열익절</span>`
          : `<span class="px-2 py-0.5 rounded text-[10px] ${{t.type === 'ANCHOR' ? 'bg-indigo-500/20 text-indigo-300' : 'bg-amber-500/20 text-amber-300'}}">${{t.type}}</span>`;
        return `
          <tr class="hover:bg-slate-800/40 transition">
            <td class="py-2 px-3 text-slate-500">${{idx + 1}}</td>
            <td class="py-2 px-3 text-slate-200">${{t.date}}</td>
            <td class="py-2 px-3">${{typeBadge}}</td>
            <td class="py-2 px-3 text-right font-medium">${{t.qty}}주</td>
            <td class="py-2 px-3 text-right text-slate-400">$${{t.costBasis.toFixed(2)}}</td>
            <td class="py-2 px-3 text-right text-slate-200">$${{t.price.toFixed(2)}}</td>
            <td class="py-2 px-3 text-right font-bold ${{isWin ? 'text-emerald-400' : 'text-rose-400'}}">${{isWin ? '+' : ''}}$${{t.pnl.toFixed(2)}}</td>
            <td class="py-2 px-3 text-right font-bold ${{isWin ? 'text-emerald-400' : 'text-rose-400'}}">${{isWin ? '+' : ''}}$${{t.retPct.toFixed(1)}}%</td>
            <td class="py-2 px-3 text-right text-slate-400">$${{Math.round(t.cumPnL).toLocaleString()}}</td>
            <td class="py-2 px-3 text-slate-400 text-[11px]">${{t.reason}}</td>
          </tr>
        `;
      }}).join("");

      // 2. All Trades Table
      const tbodyAll = document.getElementById("tbodyAllTrades");
      tbodyAll.innerHTML = currentTrades.map((t, idx) => {{
        const isBuy = t.side === "BUY";
        return `
          <tr class="hover:bg-slate-800/40 transition">
            <td class="py-2 px-3 text-slate-500">${{idx + 1}}</td>
            <td class="py-2 px-3 text-slate-200">${{t.date}}</td>
            <td class="py-2 px-3"><span class="px-2 py-0.5 rounded text-[10px] ${{t.type === 'ANCHOR' ? 'bg-indigo-500/20 text-indigo-300' : 'bg-amber-500/20 text-amber-300'}}">${{t.type}}</span></td>
            <td class="py-2 px-3"><span class="font-bold ${{isBuy ? 'text-emerald-400' : 'text-rose-400'}}">${{isBuy ? '🟢 매수' : '🔴 매도'}}</span></td>
            <td class="py-2 px-3 text-right font-medium">${{t.qty}}주</td>
            <td class="py-2 px-3 text-right text-slate-200">$${{t.price.toFixed(2)}}</td>
            <td class="py-2 px-3 text-right text-slate-300">$${{Math.round(t.qty * t.price).toLocaleString()}}</td>
            <td class="py-2 px-3 text-slate-400 text-[11px]">${{t.reason}}</td>
          </tr>
        `;
      }}).join("");

      // 3. Daily Ledger Table
      const tbodyDaily = document.getElementById("tbodyDaily");
      tbodyDaily.innerHTML = currentDaily.map(d => {{
        const retSign = d.retVsAvg >= 0 ? '+' : '';
        return `
          <tr class="hover:bg-slate-800/40 transition">
            <td class="py-2 px-3 text-slate-200">${{d.date}}</td>
            <td class="py-2 px-3 text-right text-slate-200 font-medium">$${{d.close.toFixed(2)}}</td>
            <td class="py-2 px-3 text-right text-indigo-300">${{d.anchorQty}}주</td>
            <td class="py-2 px-3 text-right text-amber-300">${{d.gridQty + d.runnerQty}}주</td>
            <td class="py-2 px-3 text-right font-bold">${{d.totHolding}}주</td>
            <td class="py-2 px-3 text-right text-slate-300">${{d.totAvg > 0 ? '$' + d.totAvg.toFixed(2) : '-'}}</td>
            <td class="py-2 px-3 text-right font-bold ${{d.retVsAvg >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{d.totAvg > 0 ? retSign + d.retVsAvg.toFixed(1) + '%' : '-'}}</td>
            <td class="py-2 px-3 text-right text-slate-400">$${{Math.round(d.cash).toLocaleString()}}</td>
            <td class="py-2 px-3 text-right font-bold text-white">$${{Math.round(d.equity).toLocaleString()}}</td>
            <td class="py-2 px-3 text-right text-rose-400">${{d.dd.toFixed(1)}}%</td>
          </tr>
        `;
      }}).join("");

      // 4. Monthly Matrix Table
      buildMonthlyMatrix();
    }}

    function buildMonthlyMatrix() {{
      const months = {{}};
      for (let d of currentDaily) {{
        const m = d.date.substring(0, 7);
        if (!months[m]) months[m] = [];
        months[m].push(d);
      }}

      const capital = parseFloat(document.getElementById("inCapital").value) || 10000.0;
      const tbodyMonthly = document.getElementById("tbodyMonthly");
      let html = "";

      for (let m of Object.keys(months).sort()) {{
        const arr = months[m];
        const first = arr[0];
        const last = arr[arr.length - 1];
        
        const soxlMRet = ((last.close - first.close) / first.close) * 100.0;
        const eqStart = first.equity;
        const eqEnd = last.equity;
        const mRet = ((eqEnd - eqStart) / eqStart) * 100.0;
        const cumRet = ((eqEnd - capital) / capital) * 100.0;

        html += `
          <tr class="hover:bg-slate-800/40 transition">
            <td class="py-2 px-3 font-bold text-slate-200">${{m}}</td>
            <td class="py-2 px-3 text-right text-slate-200 font-medium">$${{last.close.toFixed(2)}}</td>
            <td class="py-2 px-3 text-right font-medium ${{soxlMRet >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{soxlMRet >= 0 ? '+' : ''}}${{soxlMRet.toFixed(1)}}%</td>
            <td class="py-2 px-3 text-right font-bold text-white">$${{Math.round(eqEnd).toLocaleString()}}</td>
            <td class="py-2 px-3 text-right font-bold ${{mRet >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{mRet >= 0 ? '+' : ''}}${{mRet.toFixed(2)}}%</td>
            <td class="py-2 px-3 text-right font-bold ${{cumRet >= 0 ? 'text-emerald-400' : 'text-rose-400'}}">${{cumRet >= 0 ? '+' : ''}}${{cumRet.toFixed(1)}}%</td>
            <td class="py-2 px-3 text-right text-slate-400">$${{Math.round(last.cash).toLocaleString()}}</td>
            <td class="py-2 px-3 text-right font-medium text-slate-300">${{last.totHolding}}주</td>
          </tr>
        `;
      }}
      tbodyMonthly.innerHTML = html;
    }}

    function exportCurrentTableCsv() {{
      const sellTrades = currentTrades.filter(t => t.side === "SELL");
      let csv = "번호,체결일자,포지션,수량,매수평단,매도단가,실현손익,체결수익률,누적실현순익,매매사유\\n";
      sellTrades.forEach((t, idx) => {{
        csv += `${{idx + 1}},${{t.date}},${{t.type}},${{t.qty}},${{t.costBasis.toFixed(2)}},${{t.price.toFixed(2)}},${{t.pnl.toFixed(2)}},${{t.retPct.toFixed(2)}}%,${{t.cumPnL.toFixed(2)}},"${{t.reason}}"\\n`;
      }});
      const blob = new Blob([csv], {{ type: "text/csv;charset=utf-8;" }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `JW_Quant_Trades_${{document.getElementById("inStartDate").value}}_${{document.getElementById("inEndDate").value}}.csv`;
      a.click();
    }}
  </script>
</body>
</html>"""

    target_path = Path("quantum_dashboard.html")
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Generated {target_path} successfully ({len(html_content)} bytes).")

if __name__ == "__main__":
    main()
