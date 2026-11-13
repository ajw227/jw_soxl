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
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JW 퀀트 백테스트 대시보드</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Jua&family=Pretendard:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ["Pretendard", "system-ui", "-apple-system", "sans-serif"],
            cute: ["Jua", "Pretendard", "sans-serif"],
            mono: ["JetBrains Mono", "monospace"]
          }}
        }}
      }}
    }}
  </script>
  <style>
    body {{
      background-color: #fff9f5;
      background-image:
        radial-gradient(circle at 12% 10%, rgba(255, 182, 193, 0.28), transparent 36%),
        radial-gradient(circle at 88% 8%, rgba(125, 211, 252, 0.25), transparent 38%),
        radial-gradient(circle at 50% 90%, rgba(253, 230, 138, 0.25), transparent 42%);
      color: #4a3728;
    }}
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: #fff5f7; }}
    ::-webkit-scrollbar-thumb {{ background: #fbcfe8; border-radius: 999px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #f472b6; }}
    .glass-panel {{
      background: rgba(255, 255, 255, 0.92);
      backdrop-filter: blur(10px);
      border: 2px solid #fce7f3;
      box-shadow: 0 10px 26px -10px rgba(244, 114, 182, 0.16);
    }}
    .btn-preset {{
      background: #fffdfb;
      border: 2px solid #fce7f3;
      color: #6b5344;
      font-weight: 600;
      transition: all 0.15s ease;
    }}
    .btn-preset:hover {{ background: #fdf2f8; border-color: #f9a8d4; color: #4a3728; }}
    .btn-preset.active {{ background: #f472b6; border-color: #f472b6; color: #fff; font-weight: 700; }}
    .tab-btn.active {{ border-bottom: 3px solid #f472b6; color: #be185d; font-weight: 700; }}
  </style>
</head>
<body class="font-sans antialiased min-h-screen pb-20 selection:bg-pink-200 selection:text-[#4a3728]">

  <!-- Header -->
  <header class="border-b-2 border-pink-100 bg-white/85 sticky top-0 z-50 backdrop-blur-md">
    <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-2">
      <div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
        <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-2xl bg-pink-100 border-2 border-pink-200 flex items-center justify-center shadow-sm shrink-0">
          <svg class="w-6 h-6 sm:w-7 sm:h-7" viewBox="0 0 40 40" fill="none">
            <circle cx="12" cy="11" r="5" fill="#FFFFFF" stroke="#4A3728" stroke-width="2"/>
            <circle cx="28" cy="11" r="5" fill="#FFFFFF" stroke="#4A3728" stroke-width="2"/>
            <ellipse cx="20" cy="23" rx="13" ry="11" fill="#FFFFFF" stroke="#4A3728" stroke-width="2"/>
            <circle cx="15.5" cy="21" r="1.6" fill="#4A3728"/>
            <circle cx="24.5" cy="21" r="1.6" fill="#4A3728"/>
            <ellipse cx="12.5" cy="24" rx="2.5" ry="1.4" fill="#FF9EBB" opacity="0.8"/>
            <ellipse cx="27.5" cy="24" rx="2.5" ry="1.4" fill="#FF9EBB" opacity="0.8"/>
            <path d="M18 24.5 Q20 26.5 22 24.5" stroke="#4A3728" stroke-width="1.6" stroke-linecap="round" fill="none"/>
          </svg>
        </div>
        <div class="min-w-0">
          <div class="flex items-center gap-2">
            <h1 class="text-base sm:text-xl font-cute text-[#4a3728] truncate">JW 퀀트 백테스트</h1>
            <span class="hidden sm:inline-block text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-sky-100 text-sky-700 border border-sky-200 shrink-0">Mathematix v2.5</span>
          </div>
          <p class="hidden sm:block text-[11px] text-amber-800/70 truncate">과매도 바닥 손절 차단 + 200 SMA 버블 이격도 분할 익절 백테스트</p>
        </div>
      </div>
      <div class="flex items-center gap-2 text-xs shrink-0">
        <a href="orders.html" class="flex items-center gap-1.5 bg-sky-100 hover:bg-sky-200 text-sky-800 font-bold px-2.5 sm:px-3.5 py-1.5 sm:py-2 rounded-2xl border-2 border-sky-200 transition">
          <span>📋</span>
          <span class="sm:hidden">주문표</span>
          <span class="hidden sm:inline">실전 주문표</span>
        </a>
        <div class="hidden sm:flex items-center gap-2 bg-amber-50 border-2 border-amber-200 px-3 py-1.5 rounded-2xl text-amber-900 font-semibold">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>자산: <strong>SOXL 1D</strong></span>
        </div>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 pt-4 sm:pt-6 space-y-4 sm:space-y-6">

    <!-- Control Bar: Period Selection & Capital -->
    <div class="glass-panel rounded-3xl p-4 sm:p-5 space-y-3.5 sm:space-y-4">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3.5 sm:gap-4">
        
        <!-- Preset Buttons -->
        <div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
          <span class="w-full sm:w-auto text-[11px] sm:text-xs font-bold text-[#6b5344] mr-1">⚡ 빠른 기간:</span>
          <button class="btn-preset active px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs" onclick="setPreset('2026-01-02', 'latest', this)">2026 (YTD)</button>
          <button class="btn-preset px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs" onclick="setPreset('2025-01-01', '2025-12-31', this)">2025</button>
          <button class="btn-preset px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs" onclick="setPreset('2025-01-01', 'latest', this)">최근 2년</button>
          <button class="btn-preset px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs" onclick="setPreset('2024-01-01', '2024-12-31', this)">2024</button>
          <button class="btn-preset px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs" onclick="setPreset('2022-01-01', '2022-12-31', this)">2022 폭락</button>
          <button class="btn-preset px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs" onclick="setPreset('2020-01-01', 'latest', this)">최근 7년</button>
          <button class="btn-preset px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs" onclick="setPreset('2010-03-11', 'latest', this)">16년 전체</button>
        </div>

        <!-- Custom Date Range & Capital Inputs -->
        <div class="flex flex-col sm:flex-row sm:flex-wrap sm:items-center gap-2.5 sm:gap-3">
          <div class="flex items-center justify-between sm:justify-start gap-1.5 sm:gap-2 bg-[#fffdfb] border-2 border-pink-100 rounded-2xl px-3 py-2 sm:py-1.5 w-full sm:w-auto">
            <span class="text-[11px] sm:text-xs text-[#6b5344] font-bold shrink-0">기간:</span>
            <input type="date" id="inStartDate" value="2026-01-02" class="bg-transparent text-[11px] sm:text-xs text-[#4a3728] font-mono font-bold focus:outline-none min-w-0">
            <span class="text-pink-400 text-xs font-bold">~</span>
            <input type="date" id="inEndDate" value="2026-11-02" class="bg-transparent text-[11px] sm:text-xs text-[#4a3728] font-mono font-bold focus:outline-none min-w-0">
          </div>

          <div class="flex items-center gap-2 w-full sm:w-auto">
            <div class="flex items-center gap-2 bg-[#fffdfb] border-2 border-pink-100 rounded-2xl px-3 py-2 sm:py-1.5 flex-1 sm:flex-initial">
              <span class="text-[11px] sm:text-xs text-[#6b5344] font-bold shrink-0">원금:</span>
              <span class="text-xs text-pink-400 font-bold">$</span>
              <input type="number" inputmode="numeric" id="inCapital" value="10000" step="1000" class="w-full sm:w-20 bg-transparent text-xs text-[#4a3728] font-mono font-bold focus:outline-none">
            </div>

            <button onclick="applyFilters()" class="px-4 py-2 rounded-2xl bg-pink-400 hover:bg-pink-500 text-white text-xs font-bold shadow-sm transition shrink-0 cursor-pointer">
              🚀 실행
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- Summary KPI Cards -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      <div class="glass-panel rounded-2xl p-4 bg-pink-50/70">
        <p class="text-[11px] text-pink-700 font-bold">최종 자산</p>
        <h3 id="kpiFinalEquity" class="text-lg sm:text-xl font-extrabold font-mono text-[#4a3728] mt-1">$0</h3>
        <p id="kpiNetProfit" class="text-[11px] font-mono mt-1 text-amber-800/70">순익 $0</p>
      </div>

      <div class="glass-panel rounded-2xl p-4 bg-emerald-50/70">
        <p class="text-[11px] text-emerald-800 font-bold">전략 수익률</p>
        <h3 id="kpiTotalReturn" class="text-lg sm:text-xl font-extrabold font-mono text-emerald-700 mt-1">+0.0%</h3>
        <p id="kpiSoxlBnh" class="text-[11px] font-mono mt-1 text-amber-800/70">SOXL B&H: +0.0%</p>
      </div>

      <div class="glass-panel rounded-2xl p-4 bg-rose-50/70">
        <p class="text-[11px] text-rose-700 font-bold">최대 낙폭 (MDD)</p>
        <h3 id="kpiMDD" class="text-lg sm:text-xl font-extrabold font-mono text-rose-600 mt-1">-0.0%</h3>
        <p id="kpiSoxlMdd" class="text-[11px] font-mono mt-1 text-amber-800/70">SOXL B&H: -0.0%</p>
      </div>

      <div class="glass-panel rounded-2xl p-4 bg-sky-50/70">
        <p class="text-[11px] text-sky-800 font-bold">총 실현 순익</p>
        <h3 id="kpiRealizedPnL" class="text-lg sm:text-xl font-extrabold font-mono text-sky-700 mt-1">+$0</h3>
        <p id="kpiSellTradesCount" class="text-[11px] font-mono mt-1 text-amber-800/70">매도 0건</p>
      </div>

      <div class="glass-panel rounded-2xl p-4 bg-amber-50/70">
        <p class="text-[11px] text-amber-800 font-bold">승률 & 손익비</p>
        <h3 id="kpiWinRate" class="text-lg sm:text-xl font-extrabold font-mono text-amber-700 mt-1">0.0%</h3>
        <p id="kpiPayoff" class="text-[11px] font-mono mt-1 text-amber-800/70">손익비: 0.0x</p>
      </div>

      <div class="glass-panel rounded-2xl p-4 bg-purple-50/70">
        <p class="text-[11px] text-purple-800 font-bold">완료 사이클 / 매매</p>
        <h3 id="kpiCycles" class="text-lg sm:text-xl font-extrabold font-mono text-purple-700 mt-1">0회</h3>
        <p id="kpiTotalTrades" class="text-[11px] font-mono mt-1 text-amber-800/70">총 0회 체결</p>
      </div>
    </div>

    <!-- Charts Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <!-- Main Equity Chart -->
      <div class="lg:col-span-2 glass-panel rounded-3xl p-4 sm:p-5 space-y-3">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div>
            <h2 class="text-xs sm:text-sm font-bold text-[#4a3728] flex items-center gap-2">
              <span>📈 자산 성장 곡선 (Equity Curve)</span>
              <span class="hidden sm:inline text-[10px] text-amber-800/70 font-normal">전략 vs SOXL 단순보유</span>
            </h2>
          </div>
          <div class="flex items-center gap-3 text-[11px] sm:text-xs font-mono font-semibold text-[#4a3728]">
            <span class="flex items-center gap-1.5"><span class="w-3 h-0.5 bg-pink-500 rounded"></span> JW 퀀트</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-0.5 bg-amber-400 rounded"></span> SOXL B&H</span>
          </div>
        </div>
        <div class="h-56 sm:h-72 w-full">
          <canvas id="chartEquity"></canvas>
        </div>
      </div>

      <!-- Asset Allocation Breakdown Chart -->
      <div class="glass-panel rounded-3xl p-4 sm:p-5 space-y-3">
        <div class="flex items-center justify-between">
          <h2 class="text-xs sm:text-sm font-bold text-[#4a3728]">💼 포트폴리오 자산 구성 (%)</h2>
          <span class="text-[10px] text-amber-800/70 font-semibold">현금 vs 앵커 vs 그리드</span>
        </div>
        <div class="h-56 sm:h-72 w-full">
          <canvas id="chartAllocation"></canvas>
        </div>
      </div>
    </div>

    <!-- Details Section with Tabs -->
    <div class="glass-panel rounded-3xl p-4 sm:p-5 space-y-4">
      <div class="sticky top-16 z-30 bg-white/95 backdrop-blur-md pb-3 pt-1 border-b-2 border-pink-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <!-- Tabs -->
        <div class="flex items-center gap-4 sm:gap-6 text-xs sm:text-sm overflow-x-auto whitespace-nowrap pb-1 sm:pb-0">
          <button id="tabBtn1" class="tab-btn active pb-2 font-bold transition" onclick="switchTab(1)">
            💰 매도 실현 손익 장부 (<span id="countSellTrades">0</span>건)
          </button>
          <button id="tabBtn2" class="tab-btn pb-2 font-semibold text-[#6b5344] hover:text-pink-600 transition" onclick="switchTab(2)">
            📜 전체 체결 내역 (<span id="countAllTrades">0</span>건)
          </button>
          <button id="tabBtn3" class="tab-btn pb-2 font-semibold text-[#6b5344] hover:text-pink-600 transition" onclick="switchTab(3)">
            📅 일별 계좌 장부 (<span id="countDailyRows">0</span>일)
          </button>
          <button id="tabBtn4" class="tab-btn pb-2 font-semibold text-[#6b5344] hover:text-pink-600 transition" onclick="switchTab(4)">
            🗓️ 월별 성과 요약
          </button>
        </div>

        <!-- Export CSV Button -->
        <button onclick="exportCurrentTableCsv()" class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-sky-50 hover:bg-sky-100 text-sky-800 border border-sky-200 text-xs font-bold self-end sm:self-auto shadow-sm cursor-pointer">
          <span>📥</span> <span>Excel CSV 다운로드</span>
        </button>
      </div>

      <!-- Tab Content 1: Sell Realized PnL Table -->
      <div id="tabContent1" class="tab-content overflow-x-auto max-h-[70vh] overflow-y-auto rounded-2xl border-2 border-pink-100 bg-white/80">
        <table class="w-full text-left text-xs font-mono">
          <thead class="sticky top-0 z-20 bg-pink-50/95 backdrop-blur-md text-[#6b5344] border-b-2 border-pink-100">
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
          <tbody id="tbodySellTrades" class="divide-y divide-pink-100/80 text-[#4a3728]">
          </tbody>
        </table>
      </div>

      <!-- Tab Content 2: All Trades Table -->
      <div id="tabContent2" class="tab-content hidden overflow-x-auto max-h-[70vh] overflow-y-auto rounded-2xl border-2 border-pink-100 bg-white/80">
        <table class="w-full text-left text-xs font-mono">
          <thead class="sticky top-0 z-20 bg-pink-50/95 backdrop-blur-md text-[#6b5344] border-b-2 border-pink-100">
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
          <tbody id="tbodyAllTrades" class="divide-y divide-pink-100/80 text-[#4a3728]">
          </tbody>
        </table>
      </div>

      <!-- Tab Content 3: Daily Ledger Table -->
      <div id="tabContent3" class="tab-content hidden overflow-x-auto max-h-[70vh] overflow-y-auto rounded-2xl border-2 border-pink-100 bg-white/80">
        <table class="w-full text-left text-xs font-mono">
          <thead class="sticky top-0 z-20 bg-pink-50/95 backdrop-blur-md text-[#6b5344] border-b-2 border-pink-100">
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
          <tbody id="tbodyDaily" class="divide-y divide-pink-100/80 text-[#4a3728]">
          </tbody>
        </table>
      </div>

      <!-- Tab Content 4: Monthly Matrix -->
      <div id="tabContent4" class="tab-content hidden overflow-x-auto max-h-[70vh] overflow-y-auto rounded-2xl border-2 border-pink-100 bg-white/80">
        <table class="w-full text-left text-xs font-mono">
          <thead class="sticky top-0 z-20 bg-pink-50/95 backdrop-blur-md text-[#6b5344] border-b-2 border-pink-100">
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
              borderColor: "#ec4899",
              backgroundColor: "rgba(236, 72, 153, 0.1)",
              borderWidth: 2,
              fill: true,
              pointRadius: 0,
              tension: 0.1
            }},
            {{
              label: "SOXL 단순보유 자산 ($)",
              data: bnhEquity,
              borderColor: "#f59e0b",
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
              backgroundColor: "rgba(255, 255, 255, 0.96)",
              titleColor: "#4a3728",
              bodyColor: "#4a3728",
              borderColor: "#fbcfe8",
              borderWidth: 1.5,
              callbacks: {{
                label: (ctx) => `${{ctx.dataset.label}}: $${{Math.round(ctx.parsed.y).toLocaleString()}}`
              }}
            }}
          }},
          scales: {{
            x: {{ grid: {{ display: false }}, ticks: {{ maxTicksLimit: 8, color: "#92400e", font: {{ size: 10 }} }} }},
            y: {{ grid: {{ color: "rgba(244, 114, 182, 0.12)" }}, ticks: {{ color: "#92400e", font: {{ size: 10 }}, callback: (v) => `$${{v.toLocaleString()}}` }} }}
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
            {{ label: "앵커 비중 (%)", data: anchorPct, borderColor: "#0ea5e9", backgroundColor: "rgba(14, 165, 233, 0.2)", fill: true, pointRadius: 0 }},
            {{ label: "그리드 비중 (%)", data: gridPct, borderColor: "#ec4899", backgroundColor: "rgba(236, 72, 153, 0.2)", fill: true, pointRadius: 0 }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          interaction: {{ mode: "index", intersect: false }},
          plugins: {{
            legend: {{ labels: {{ color: "#6b5344", font: {{ size: 10 }} }} }},
            tooltip: {{
              backgroundColor: "rgba(255, 255, 255, 0.96)",
              titleColor: "#4a3728",
              bodyColor: "#4a3728",
              borderColor: "#fbcfe8",
              borderWidth: 1.5,
              callbacks: {{ label: (ctx) => `${{ctx.dataset.label}}: ${{ctx.parsed.y.toFixed(1)}}%` }}
            }}
          }},
          scales: {{
            x: {{ grid: {{ display: false }}, ticks: {{ maxTicksLimit: 6, color: "#92400e", font: {{ size: 10 }} }} }},
            y: {{ stacked: true, max: 100, min: 0, grid: {{ color: "rgba(244, 114, 182, 0.12)" }}, ticks: {{ color: "#92400e", callback: (v) => `${{v}}%` }} }}
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
          ? `<span class="px-2 py-0.5 rounded-full text-[10px] bg-amber-100 text-amber-800 border border-amber-200 font-bold">🔥 과열익절</span>`
          : `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${{t.type === 'ANCHOR' ? 'bg-sky-100 text-sky-800' : 'bg-pink-100 text-pink-800'}}">${{t.type}}</span>`;
        return `
          <tr class="hover:bg-pink-50/50 transition">
            <td class="py-2 px-3 text-amber-800/60">${{idx + 1}}</td>
            <td class="py-2 px-3 text-[#4a3728]">${{t.date}}</td>
            <td class="py-2 px-3">${{typeBadge}}</td>
            <td class="py-2 px-3 text-right font-medium">${{t.qty}}주</td>
            <td class="py-2 px-3 text-right text-[#6b5344]">$${{t.costBasis.toFixed(2)}}</td>
            <td class="py-2 px-3 text-right text-[#4a3728]">$${{t.price.toFixed(2)}}</td>
            <td class="py-2 px-3 text-right font-bold ${{isWin ? 'text-emerald-700' : 'text-rose-600'}}">${{isWin ? '+' : ''}}$${{t.pnl.toFixed(2)}}</td>
            <td class="py-2 px-3 text-right font-bold ${{isWin ? 'text-emerald-700' : 'text-rose-600'}}">${{isWin ? '+' : ''}}$${{t.retPct.toFixed(1)}}%</td>
            <td class="py-2 px-3 text-right text-[#6b5344]">$${{Math.round(t.cumPnL).toLocaleString()}}</td>
            <td class="py-2 px-3 text-amber-800/70 text-[11px]">${{t.reason}}</td>
          </tr>
        `;
      }}).join("");

      // 2. All Trades Table
      const tbodyAll = document.getElementById("tbodyAllTrades");
      tbodyAll.innerHTML = currentTrades.map((t, idx) => {{
        const isBuy = t.side === "BUY";
        return `
          <tr class="hover:bg-pink-50/50 transition">
            <td class="py-2 px-3 text-amber-800/60">${{idx + 1}}</td>
            <td class="py-2 px-3 text-[#4a3728]">${{t.date}}</td>
            <td class="py-2 px-3"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${{t.type === 'ANCHOR' ? 'bg-sky-100 text-sky-800' : 'bg-pink-100 text-pink-800'}}">${{t.type}}</span></td>
            <td class="py-2 px-3"><span class="font-bold ${{isBuy ? 'text-sky-700' : 'text-pink-600'}}">${{isBuy ? '매수' : '매도'}}</span></td>
            <td class="py-2 px-3 text-right font-medium">${{t.qty}}주</td>
            <td class="py-2 px-3 text-right text-[#4a3728]">$${{t.price.toFixed(2)}}</td>
            <td class="py-2 px-3 text-right text-[#6b5344]">$${{Math.round(t.qty * t.price).toLocaleString()}}</td>
            <td class="py-2 px-3 text-amber-800/70 text-[11px]">${{t.reason}}</td>
          </tr>
        `;
      }}).join("");

      // 3. Daily Ledger Table
      const tbodyDaily = document.getElementById("tbodyDaily");
      tbodyDaily.innerHTML = currentDaily.map(d => {{
        const retSign = d.retVsAvg >= 0 ? '+' : '';
        return `
          <tr class="hover:bg-pink-50/50 transition">
            <td class="py-2 px-3 text-[#4a3728]">${{d.date}}</td>
            <td class="py-2 px-3 text-right text-[#4a3728] font-medium">$${{d.close.toFixed(2)}}</td>
            <td class="py-2 px-3 text-right text-sky-700">${{d.anchorQty}}주</td>
            <td class="py-2 px-3 text-right text-pink-600">${{d.gridQty + d.runnerQty}}주</td>
            <td class="py-2 px-3 text-right font-bold">${{d.totHolding}}주</td>
            <td class="py-2 px-3 text-right text-[#6b5344]">${{d.totAvg > 0 ? '$' + d.totAvg.toFixed(2) : '-'}}</td>
            <td class="py-2 px-3 text-right font-bold ${{d.retVsAvg >= 0 ? 'text-emerald-700' : 'text-rose-600'}}">${{d.totAvg > 0 ? retSign + d.retVsAvg.toFixed(1) + '%' : '-'}}</td>
            <td class="py-2 px-3 text-right text-[#6b5344]">$${{Math.round(d.cash).toLocaleString()}}</td>
            <td class="py-2 px-3 text-right font-bold text-[#4a3728]">$${{Math.round(d.equity).toLocaleString()}}</td>
            <td class="py-2 px-3 text-right text-rose-600">${{d.dd.toFixed(1)}}%</td>
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
          <tr class="hover:bg-pink-50/50 transition">
            <td class="py-2 px-3 font-bold text-[#4a3728]">${{m}}</td>
            <td class="py-2 px-3 text-right text-[#4a3728] font-medium">$${{last.close.toFixed(2)}}</td>
            <td class="py-2 px-3 text-right font-medium ${{soxlMRet >= 0 ? 'text-emerald-700' : 'text-rose-600'}}">${{soxlMRet >= 0 ? '+' : ''}}${{soxlMRet.toFixed(1)}}%</td>
            <td class="py-2 px-3 text-right font-bold text-[#4a3728]">$${{Math.round(eqEnd).toLocaleString()}}</td>
            <td class="py-2 px-3 text-right font-bold ${{mRet >= 0 ? 'text-emerald-700' : 'text-rose-600'}}">${{mRet >= 0 ? '+' : ''}}${{mRet.toFixed(2)}}%</td>
            <td class="py-2 px-3 text-right font-bold ${{cumRet >= 0 ? 'text-emerald-700' : 'text-rose-600'}}">${{cumRet >= 0 ? '+' : ''}}${{cumRet.toFixed(1)}}%</td>
            <td class="py-2 px-3 text-right text-[#6b5344]">$${{Math.round(last.cash).toLocaleString()}}</td>
            <td class="py-2 px-3 text-right font-medium text-[#4a3728]">${{last.totHolding}}주</td>
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
