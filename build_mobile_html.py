import os
import json

def build_mobile_app_html():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "mobile_data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        data_json_str = f.read()

    html_content = f'''<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="OddsHub">
    <meta name="theme-color" content="#0f172a">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <link rel="manifest" href="./manifest.json">
    <link rel="apple-touch-icon" href="./apple-touch-icon.png">
    <link rel="icon" type="image/png" href="./icon.png">
    <title>OddsHub Mobile • Advantage Betting & Odds Screen</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    colors: {{
                        novig: '#00d26a',
                        dk: '#53d337',
                        fd: '#14805e',
                        mgm: '#cba052',
                        darkBg: '#0b0f19',
                        darkCard: '#131b2e',
                        darkSub: '#1c263f'
                    }}
                }}
            }}
        }}
    </script>
    <style>
        html, body {{
            overflow-x: hidden;
            width: 100%;
            -webkit-text-size-adjust: 100%;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            -webkit-tap-highlight-color: transparent;
            touch-action: manipulation;
        }}
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .no-scrollbar {{ -ms-overflow-style: none; scrollbar-width: none; }}
        .safe-bottom {{ padding-bottom: calc(4.8rem + env(safe-area-inset-bottom)); }}
        .safe-top {{ padding-top: env(safe-area-inset-top); }}
        input[type="number"]::-webkit-inner-spin-button,
        input[type="number"]::-webkit-outer-spin-button {{ -webkit-appearance: none; margin: 0; }}
        .line-clamp-1 {{ display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }}
    </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen safe-bottom selection:bg-emerald-500 selection:text-white dark" id="appBody">

    <!-- Top Sticky Mobile Header -->
    <header class="sticky top-0 z-40 bg-slate-900/95 backdrop-blur-md border-b border-slate-800 safe-top">
        <div class="px-3.5 pt-2.5 pb-2">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2">
                    <div class="w-7 h-7 rounded-lg bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center text-slate-950 font-black text-xs shadow-md shadow-emerald-500/20 shrink-0">
                        ⚡
                    </div>
                    <div class="min-w-0">
                        <div class="flex items-center space-x-1.5">
                            <h1 class="text-sm font-black tracking-tight text-white leading-tight">OddsHub</h1>
                            <span class="text-[9px] font-black px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">LIVE</span>
                        </div>
                        <p class="text-[9.5px] text-slate-400 font-medium truncate" id="headerUpdatedTime">Updated Today</p>
                    </div>
                </div>

                <!-- Header Actions -->
                <div class="flex items-center space-x-1 shrink-0">
                    <button onclick="toggleTheme()" class="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white active:scale-95 transition" title="Toggle Theme">
                        <span id="themeIcon" class="text-xs">☀️</span>
                    </button>
                    <button onclick="openSettingsModal()" class="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white active:scale-95 transition text-xs" title="Settings & Refresh">
                        ⚙️
                    </button>
                    <button onclick="refreshData()" id="refreshBtn" class="flex items-center space-x-1 px-2 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[11px] active:scale-95 shadow-sm transition">
                        <span>⟳</span>
                        <span>Sync</span>
                    </button>
                </div>
            </div>

            <!-- Sport Category Carousel (Scrollable Pills) -->
            <div class="flex items-center space-x-1.5 overflow-x-auto no-scrollbar pt-2 pb-0.5 -mx-3.5 px-3.5 text-xs font-semibold" id="sportPillsContainer">
                <button onclick="setSportFilter('ALL')" id="sportBtn_ALL" class="sport-pill px-2.5 py-1 rounded-full bg-emerald-500 text-slate-950 font-bold whitespace-nowrap shadow-sm text-[11px] transition">
                    🔥 All Sports
                </button>
                <button onclick="setSportFilter('WNBA')" id="sportBtn_WNBA" class="sport-pill px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 hover:text-white whitespace-nowrap text-[11px] transition">
                    🏀 WNBA
                </button>
                <button onclick="setSportFilter('NFL')" id="sportBtn_NFL" class="sport-pill px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 hover:text-white whitespace-nowrap text-[11px] transition">
                    🏈 NFL
                </button>
                <button onclick="setSportFilter('NHL')" id="sportBtn_NHL" class="sport-pill px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 hover:text-white whitespace-nowrap text-[11px] transition">
                    🏒 NHL
                </button>
                <button onclick="setSportFilter('MLB')" id="sportBtn_MLB" class="sport-pill px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 hover:text-white whitespace-nowrap text-[11px] transition">
                    ⚾ MLB
                </button>
                <button onclick="setSportFilter('NCAAF')" id="sportBtn_NCAAF" class="sport-pill px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 hover:text-white whitespace-nowrap text-[11px] transition">
                    🎓 NCAAF
                </button>
            </div>
        </div>

        <!-- Sub-Nav Filter / Full Width Search & Segmented Market Pills -->
        <div class="px-3.5 py-2 bg-slate-950/70 border-t border-slate-800/80 space-y-1.5" id="subFilterBar">
            <!-- Search bar with clear button -->
            <div class="relative w-full">
                <input type="text" id="searchInput" oninput="handleSearch(this.value)" placeholder="Search teams, players (e.g. Eagles, Hurts, Bears)..." 
                    class="w-full bg-slate-800/90 border border-slate-700/80 rounded-xl pl-8 pr-7 py-1.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-emerald-500 transition">
                <span class="absolute left-2.5 top-1.5 text-slate-400 text-xs">🔍</span>
                <button id="clearSearchBtn" onclick="clearSearch()" class="absolute right-2 top-1 text-slate-400 hover:text-white text-xs hidden p-0.5">✕</button>
            </div>
            
            <!-- Action Network Style Market Segmented Bar -->
            <div class="grid grid-cols-4 bg-slate-900/90 p-0.5 rounded-xl border border-slate-800 text-[11px] font-semibold text-center" id="marketPillsContainer">
                <button onclick="setMarketFilter('all')" id="mktBtn_all" class="market-pill py-1 rounded-lg bg-slate-700 text-white font-bold transition">All Lines</button>
                <button onclick="setMarketFilter('spreads')" id="mktBtn_spreads" class="market-pill py-1 rounded-lg text-slate-400 hover:text-white transition">Spread</button>
                <button onclick="setMarketFilter('totals')" id="mktBtn_totals" class="market-pill py-1 rounded-lg text-slate-400 hover:text-white transition">Total</button>
                <button onclick="setMarketFilter('h2h')" id="mktBtn_h2h" class="market-pill py-1 rounded-lg text-slate-400 hover:text-white transition">Moneyline</button>
            </div>

            <!-- Line Source Toggle (Retail Best vs Include Novig) -->
            <div id="sourceToggleContainer" class="flex items-center justify-between pt-0.5 text-[10.5px] px-0.5">
                <div class="flex items-center space-x-1 text-slate-400 font-medium">
                    <span>Source:</span>
                    <span id="activeSourceLabel" class="text-indigo-400 font-bold">6 Retail Books</span>
                </div>
                <div class="inline-flex p-0.5 bg-slate-900 rounded-lg border border-slate-800">
                    <button id="modeBtnRetail" onclick="setNovigDisplayMode('retail')" class="px-2 py-0.5 rounded-md font-bold text-[10px] bg-indigo-600 text-white shadow-xs transition">
                        🏢 Retail Best
                    </button>
                    <button id="modeBtnAll" onclick="setNovigDisplayMode('all')" class="px-2 py-0.5 rounded-md font-bold text-[10px] text-slate-400 hover:text-slate-200 transition">
                        ⚡ Inc. Novig
                    </button>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Views Container -->
    <main class="max-w-xl mx-auto px-3 py-2.5">

        <!-- VIEW 1: ODDS SCREEN (Action Network Style Matchups) -->
        <section id="viewOddsScreen" class="space-y-2.5">
            <div class="flex items-center justify-between text-[11px] text-slate-400 px-0.5 font-medium">
                <span id="matchupCountLabel">Showing Matchups</span>
                <span class="text-emerald-400 font-semibold flex items-center gap-1">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block animate-pulse"></span>
                    Best lines in Green
                </span>
            </div>

            <!-- Matchup Cards Container -->
            <div id="matchupsContainer" class="space-y-2.5">
                <!-- Dynamically injected via JS -->
            </div>
        </section>

        <!-- VIEW 2: +EV & ARBITRAGE CARDS (OddsShopper Style) -->
        <section id="viewArbsScreen" class="space-y-2.5 hidden">
            <!-- Filter Bar for Arbs -->
            <div class="flex items-center justify-between text-xs px-0.5">
                <span class="font-bold text-slate-300 text-[11px]" id="arbCountLabel">Active Arbitrage & +EV Spots</span>
                <div class="flex items-center space-x-1.5 text-[11px]">
                    <span class="text-slate-400">Default Bet:</span>
                    <div class="relative">
                        <span class="absolute left-1.5 top-0.5 text-slate-400 font-bold">$</span>
                        <input type="number" id="globalStakeInput" value="250" onchange="updateAllArbStakes(this.value)" class="w-16 bg-slate-800 border border-slate-700 rounded pl-4 pr-1 py-0.5 text-center text-emerald-400 font-bold text-xs focus:outline-none focus:border-emerald-500">
                    </div>
                </div>
            </div>

            <!-- Segmented Arb Filter (All | Retail Only | Inc. Novig) -->
            <div class="flex items-center space-x-1 p-0.5 bg-slate-900/90 rounded-xl border border-slate-800 text-[10px] font-bold">
                <button id="arbFilter_all" onclick="setArbFilter('all')" class="flex-1 py-1 rounded-lg bg-emerald-500 text-slate-950 font-bold shadow-xs transition text-center text-[10px]">
                    All Spots (<span id="arbPillAllCount">0</span>)
                </button>
                <button id="arbFilter_retail" onclick="setArbFilter('retail')" class="flex-1 py-1 rounded-lg text-slate-400 hover:text-white transition text-center text-[10px]">
                    🏢 Retail Only (<span id="arbPillRetailCount">0</span>)
                </button>
                <button id="arbFilter_novig" onclick="setArbFilter('novig')" class="flex-1 py-1 rounded-lg text-slate-400 hover:text-white transition text-center text-[10px]">
                    ⚡ Novig Hedge (<span id="arbPillNovigCount">0</span>)
                </button>
            </div>

            <div id="arbsContainer" class="space-y-2.5">
                <!-- Dynamically injected via JS -->
            </div>
        </section>

        <!-- VIEW 3: PLAYER PROPS EXPLORER -->
        <section id="viewPropsScreen" class="space-y-2.5 hidden">
            <!-- Prop Categories -->
            <div class="flex items-center space-x-1.5 overflow-x-auto no-scrollbar pb-0.5 text-[11px] font-semibold" id="propCategoryPills">
                <button onclick="setPropCategory('ALL')" class="prop-cat px-2.5 py-1 rounded-full bg-emerald-500 text-slate-950 font-bold whitespace-nowrap text-[11px]">All Props</button>
                <button onclick="setPropCategory('Passing Yards')" class="prop-cat px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 hover:text-white whitespace-nowrap text-[11px]">Passing Yds</button>
                <button onclick="setPropCategory('Rushing Yards')" class="prop-cat px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 hover:text-white whitespace-nowrap text-[11px]">Rushing Yds</button>
                <button onclick="setPropCategory('Receiving Yards')" class="prop-cat px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 hover:text-white whitespace-nowrap text-[11px]">Receiving Yds</button>
                <button onclick="setPropCategory('Anytime Touchdown')" class="prop-cat px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 hover:text-white whitespace-nowrap text-[11px]">Anytime TD</button>
                <button onclick="setPropCategory('Receptions')" class="prop-cat px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 hover:text-white whitespace-nowrap text-[11px]">Receptions</button>
            </div>

            <div id="propsContainer" class="space-y-2.5">
                <!-- Dynamically injected via JS -->
            </div>
        </section>

        <!-- VIEW 4: CALCULATORS -->
        <section id="viewCalcScreen" class="space-y-3.5 hidden">
            <!-- Segmented Sub-Nav for Calculators -->
            <div class="flex items-center space-x-1 p-1 bg-slate-900/90 rounded-xl border border-slate-800 text-[11px] font-bold">
                <button id="calcTab_arb" onclick="switchCalcSubTab('arb')" class="flex-1 py-1.5 rounded-lg bg-emerald-500 text-slate-950 font-bold shadow-xs transition text-center text-[11px]">
                    🧮 2-Way Arb
                </button>
                <button id="calcTab_freebet" onclick="switchCalcSubTab('freebet')" class="flex-1 py-1.5 rounded-lg text-slate-400 hover:text-white transition text-center text-[11px]">
                    🎁 Free Bet SNR
                </button>
                <button id="calcTab_convert" onclick="switchCalcSubTab('convert')" class="flex-1 py-1.5 rounded-lg text-slate-400 hover:text-white transition text-center text-[11px]">
                    🔄 Translator
                </button>
            </div>

            <!-- PANEL 1: 2-WAY ARBITRAGE -->
            <div id="calcPanel_arb" class="space-y-3">
                <div class="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-3.5 shadow-sm">
                    <div class="flex items-center justify-between mb-3 border-b border-slate-700/70 pb-2">
                        <div class="flex items-center space-x-2">
                            <span class="text-lg">🧮</span>
                            <div>
                                <h3 class="text-xs font-bold text-white uppercase tracking-wider">2-Way Arbitrage & Hedge Sizing</h3>
                                <p class="text-[9.5px] text-slate-400">Lock in risk-free profit across two sportsbooks</p>
                            </div>
                        </div>
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">Hedge Tool</span>
                    </div>

                    <!-- Bet 1 Box -->
                    <div class="bg-slate-900/80 border border-slate-700/60 rounded-xl p-2.5 mb-2.5">
                        <div class="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-emerald-400 mb-1.5">
                            <span>Bet 1 (Primary)</span>
                            <span class="text-[9.5px] text-slate-400 font-normal">Payout Total: <strong id="calcPayout1" class="text-emerald-400 font-extrabold text-xs">$476.70</strong></span>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block text-[9.5px] font-semibold text-slate-400 mb-1">Odds (US):</label>
                                <input type="text" id="calcOdds1" value="+127" oninput="calculateArb()" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-2 py-1.5 text-xs font-black text-emerald-400 text-center focus:border-emerald-500 focus:outline-none">
                            </div>
                            <div>
                                <label class="block text-[9.5px] font-semibold text-slate-400 mb-1">Stake ($):</label>
                                <input type="number" id="calcStake1" value="210" oninput="calculateArb()" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-2 py-1.5 text-xs font-black text-white text-center focus:border-emerald-500 focus:outline-none">
                            </div>
                        </div>
                    </div>

                    <!-- Bet 2 Box -->
                    <div class="bg-slate-900/80 border border-slate-700/60 rounded-xl p-2.5 mb-3">
                        <div class="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-cyan-400 mb-1.5">
                            <span>Bet 2 (Hedge)</span>
                            <span class="text-[9.5px] text-slate-400 font-normal">Payout Total: <strong id="calcPayout2" class="text-emerald-400 font-extrabold text-xs">$477.00</strong></span>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block text-[9.5px] font-semibold text-slate-400 mb-1">Hedge Odds (US):</label>
                                <input type="text" id="calcOdds2" value="-125" oninput="calculateArb()" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-2 py-1.5 text-xs font-black text-cyan-400 text-center focus:border-emerald-500 focus:outline-none">
                            </div>
                            <div>
                                <label class="block text-[9.5px] font-semibold text-slate-400 mb-1">Required Hedge ($):</label>
                                <div id="calcHedgeStake" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-2 py-1.5 text-xs font-black text-amber-400 text-center leading-[1.6]">$265.00</div>
                            </div>
                        </div>
                    </div>

                    <!-- Payout Summary Card -->
                    <div class="bg-slate-950 rounded-xl p-3 border border-slate-800 space-y-1.5">
                        <div class="flex justify-between items-center text-[11px]">
                            <span class="text-slate-400">Total Capital Outlay:</span>
                            <span class="font-bold text-white" id="calcTotalOutlay">$475.00</span>
                        </div>
                        <div class="grid grid-cols-2 gap-2 pt-1 border-t border-slate-900 text-[10px]">
                            <div class="bg-slate-900/90 rounded-lg px-2 py-1 border border-slate-800 flex justify-between items-center">
                                <span class="text-slate-400">Bet 1 Payout:</span>
                                <strong id="calcSummaryPayout1" class="text-emerald-400 font-bold">$476.70</strong>
                            </div>
                            <div class="bg-slate-900/90 rounded-lg px-2 py-1 border border-slate-800 flex justify-between items-center">
                                <span class="text-slate-400">Bet 2 Payout:</span>
                                <strong id="calcSummaryPayout2" class="text-emerald-400 font-bold">$477.00</strong>
                            </div>
                        </div>
                        <div class="flex justify-between items-center text-[11px] pt-1 border-t border-slate-900">
                            <span class="text-slate-400">Guaranteed Return:</span>
                            <span class="font-bold text-emerald-400" id="calcGuaranteedPayout">$476.70</span>
                        </div>
                        <div class="flex justify-between items-center text-xs pt-1.5 border-t border-slate-800">
                            <span class="text-slate-300 font-bold">Net Guaranteed Profit:</span>
                            <span class="font-extrabold text-xs text-emerald-400" id="calcNetProfit">+$1.70 (+0.36% ROI)</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- PANEL 2: FREE BET CONVERTER (SNR) -->
            <div id="calcPanel_freebet" class="space-y-3 hidden">
                <div class="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-3.5 shadow-sm">
                    <div class="flex items-center justify-between mb-3 border-b border-slate-700/70 pb-2">
                        <div class="flex items-center space-x-2">
                            <span class="text-lg">🎁</span>
                            <div>
                                <h3 class="text-xs font-bold text-white uppercase tracking-wider">Free Bet Converter</h3>
                                <p class="text-[9.5px] text-slate-400">Stake Not Returned (SNR) cash extraction</p>
                            </div>
                        </div>
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">SNR Model</span>
                    </div>

                    <div class="space-y-2.5 mb-3">
                        <div>
                            <label class="block text-[10.5px] font-semibold text-slate-400 mb-1">Free Bet Amount ($):</label>
                            <input type="number" id="fbAmount" value="100" oninput="calculateFreeBet()" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-black text-amber-400 text-center focus:border-amber-400 focus:outline-none">
                        </div>
                        <div class="grid grid-cols-2 gap-2.5">
                            <div>
                                <label class="block text-[10.5px] font-semibold text-slate-400 mb-1">Free Play Odds (Long):</label>
                                <input type="text" id="fbOdds" value="+300" oninput="calculateFreeBet()" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2 py-1.5 text-xs font-black text-emerald-400 text-center focus:border-emerald-500 focus:outline-none">
                            </div>
                            <div>
                                <label class="block text-[10.5px] font-semibold text-slate-400 mb-1">Hedge Odds (Short):</label>
                                <input type="text" id="fbHedgeOdds" value="-330" oninput="calculateFreeBet()" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2 py-1.5 text-xs font-black text-cyan-400 text-center focus:border-cyan-400 focus:outline-none">
                            </div>
                        </div>
                    </div>

                    <!-- Metric Cards -->
                    <div class="grid grid-cols-3 gap-2 mb-3">
                        <div class="bg-slate-950 p-2 rounded-xl border border-slate-800 text-center">
                            <span class="block text-[9.5px] text-slate-400 font-semibold mb-0.5">Required Hedge</span>
                            <span class="block text-xs font-black text-amber-400" id="fbHedgeStake">$230.23</span>
                        </div>
                        <div class="bg-slate-950 p-2 rounded-xl border border-slate-800 text-center">
                            <span class="block text-[9.5px] text-slate-400 font-semibold mb-0.5">Guaranteed Cash</span>
                            <span class="block text-xs font-black text-emerald-400" id="fbGuaranteedCash">+$69.77</span>
                        </div>
                        <div class="bg-slate-950 p-2 rounded-xl border border-slate-800 text-center">
                            <span class="block text-[9.5px] text-slate-400 font-semibold mb-0.5">Conversion %</span>
                            <span class="block text-xs font-black text-emerald-400" id="fbConversionRate">69.8%</span>
                        </div>
                    </div>

                    <!-- Scenario Breakdown -->
                    <div class="bg-slate-950 rounded-xl p-3 border border-slate-800 space-y-1.5">
                        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800/80 pb-1">
                            Equal Payout Scenarios
                        </div>
                        <div class="text-[10.5px] text-slate-300">
                            <span>If Free Bet Wins:</span>
                            <span class="font-bold text-emerald-400 ml-1" id="fbScenario1">+$300 win - $230.23 hedge = <strong class="text-white">+$69.77</strong></span>
                        </div>
                        <div class="text-[10.5px] text-slate-300 pt-1 border-t border-slate-900">
                            <span>If Hedge Wins:</span>
                            <span class="font-bold text-emerald-400 ml-1" id="fbScenario2">+$69.77 profit - $0 FB = <strong class="text-white">+$69.77</strong></span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- PANEL 3: UNIVERSAL ODDS TRANSLATOR -->
            <div id="calcPanel_convert" class="space-y-3 hidden">
                <div class="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-3.5 shadow-sm">
                    <div class="flex items-center justify-between mb-3 border-b border-slate-700/70 pb-2">
                        <div class="flex items-center space-x-2">
                            <span class="text-lg">🔄</span>
                            <div>
                                <h3 class="text-xs font-bold text-white uppercase tracking-wider">Odds Translator</h3>
                                <p class="text-[9.5px] text-slate-400">Bi-directional conversion across all formats</p>
                            </div>
                        </div>
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">Live Sync</span>
                    </div>

                    <div class="grid grid-cols-2 gap-2.5 mb-3">
                        <div>
                            <label class="block text-[10px] font-semibold text-slate-400 mb-1">American Odds:</label>
                            <input type="text" id="convAmerican" value="-150" oninput="translateFromAmerican(this.value)" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-black text-emerald-400 text-center focus:border-emerald-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-[10px] font-semibold text-slate-400 mb-1">Decimal Odds:</label>
                            <input type="number" step="0.01" id="convDecimal" value="1.67" oninput="translateFromDecimal(this.value)" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-black text-cyan-400 text-center focus:border-cyan-400 focus:outline-none">
                        </div>
                        <div>
                            <label class="block text-[10px] font-semibold text-slate-400 mb-1">Implied Probability:</label>
                            <div class="relative">
                                <input type="number" step="0.1" id="convProb" value="60.0" oninput="translateFromProb(this.value)" class="w-full bg-slate-900 border border-slate-700 rounded-lg pl-2 pr-6 py-1.5 text-xs font-black text-amber-400 text-center focus:border-amber-400 focus:outline-none">
                                <span class="absolute right-2 top-1.5 text-slate-500 text-xs font-bold">%</span>
                            </div>
                        </div>
                        <div>
                            <label class="block text-[10px] font-semibold text-slate-400 mb-1">Fractional Odds:</label>
                            <input type="text" id="convFractional" value="2/3" oninput="translateFromFractional(this.value)" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-black text-purple-400 text-center focus:border-purple-400 focus:outline-none">
                        </div>
                    </div>

                    <!-- Stake Payout Simulator -->
                    <div class="bg-slate-950 rounded-xl p-3 border border-slate-800 space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="text-[10.5px] font-semibold text-slate-400">Bet Stake Amount:</span>
                            <div class="relative w-24">
                                <span class="absolute left-2 top-1 text-slate-500 text-xs font-bold">$</span>
                                <input type="number" id="convStake" value="100" oninput="updatePayoutEstimate()" class="w-full bg-slate-900 border border-slate-700 rounded-lg pl-5 pr-2 py-1 text-xs font-black text-white text-right focus:border-emerald-500 focus:outline-none">
                            </div>
                        </div>
                        <div class="pt-1.5 border-t border-slate-800 flex justify-between items-center text-[11px]">
                            <span class="text-slate-400">Total Payout (Return):</span>
                            <span class="font-bold text-white" id="convTotalPayout">$166.67</span>
                        </div>
                        <div class="flex justify-between items-center text-xs">
                            <span class="text-slate-300 font-bold">Net Profit:</span>
                            <span class="font-black text-emerald-400" id="convNetProfit">+$66.67</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Link to Advanced Mobile Parlay Calculator -->
            <div class="bg-gradient-to-r from-indigo-900/40 to-purple-900/40 border border-indigo-500/30 rounded-2xl p-3.5">
                <div class="flex items-center justify-between gap-3">
                    <div class="min-w-0">
                        <div class="flex items-center space-x-1.5">
                            <span class="text-base">🚀</span>
                            <h4 class="text-xs font-bold text-indigo-300 truncate">Multi-Leg Parlay Hedge</h4>
                        </div>
                        <p class="text-[10px] text-slate-400 mt-0.5 leading-tight">Access the dedicated sequential parlay hedge calculator.</p>
                    </div>
                    <a href="parlay_calculator_mobile.html" class="px-2.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-[11px] font-bold shadow-sm whitespace-nowrap active:scale-95 transition shrink-0">
                        Open Tool →
                    </a>
                </div>
            </div>
        </section>

    </main>

    <!-- Bottom Mobile Navigation Bar (Native App Style) -->
    <nav class="fixed bottom-0 left-0 right-0 z-50 bg-slate-900/95 backdrop-blur-lg border-t border-slate-800 px-2 py-1 safe-bottom">
        <div class="max-w-md mx-auto grid grid-cols-4 gap-1">
            <button onclick="switchTab('odds')" id="navBtn_odds" class="nav-btn flex flex-col items-center justify-center py-1 text-emerald-400 font-bold transition">
                <span class="text-lg">📊</span>
                <span class="text-[9.5px] mt-0.5 leading-none">Odds Screen</span>
            </button>
            <button onclick="switchTab('arbs')" id="navBtn_arbs" class="nav-btn flex flex-col items-center justify-center py-1 text-slate-400 hover:text-white font-medium transition">
                <div class="relative">
                    <span class="text-lg">⚡</span>
                    <span id="arbBadgeCount" class="absolute -top-1 -right-2.5 bg-emerald-500 text-slate-950 font-black text-[8.5px] px-1 rounded-full leading-tight">125</span>
                </div>
                <span class="text-[9.5px] mt-0.5 leading-none">+EV & Arbs</span>
            </button>
            <button onclick="switchTab('props')" id="navBtn_props" class="nav-btn flex flex-col items-center justify-center py-1 text-slate-400 hover:text-white font-medium transition">
                <span class="text-lg">🎯</span>
                <span class="text-[9.5px] mt-0.5 leading-none">Props</span>
            </button>
            <button onclick="switchTab('calc')" id="navBtn_calc" class="nav-btn flex flex-col items-center justify-center py-1 text-slate-400 hover:text-white font-medium transition">
                <span class="text-lg">🧮</span>
                <span class="text-[9.5px] mt-0.5 leading-none">Calculator</span>
            </button>
        </div>
    </nav>

    <!-- Settings / Live Feed Modal -->
    <div id="settingsModal" class="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4 hidden">
        <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-sm w-full p-4 shadow-xl">
            <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                <div class="flex items-center space-x-2">
                    <span class="text-lg">⚙️</span>
                    <h3 class="text-sm font-bold text-white">Data Connection & Settings</h3>
                </div>
                <button onclick="closeSettingsModal()" class="text-slate-400 hover:text-white font-bold p-1">✕</button>
            </div>

            <div class="py-3 space-y-3 text-xs">
                <div>
                    <label class="block font-semibold text-slate-300 mb-1">Google Apps Script Web App URL (Optional):</label>
                    <input type="text" id="appsScriptUrlInput" placeholder="https://script.google.com/macros/s/.../exec"
                        class="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 text-xs focus:outline-none focus:border-emerald-500">
                    <p class="text-[10px] text-slate-400 mt-1">If provided, the app queries this URL directly on mobile to fetch live Google Sheet updates.</p>
                </div>

                <div class="bg-slate-800/80 rounded-lg p-2.5 border border-slate-700/60">
                    <div class="text-[11px] font-bold text-white mb-1">Current Data Status:</div>
                    <div class="flex justify-between text-slate-400 text-[10px]">
                        <span>Matchups Loaded:</span>
                        <strong class="text-emerald-400" id="modalMatchupCount">0</strong>
                    </div>
                    <div class="flex justify-between text-slate-400 text-[10px]">
                        <span>Player Props:</span>
                        <strong class="text-emerald-400" id="modalPropsCount">0</strong>
                    </div>
                    <div class="flex justify-between text-slate-400 text-[10px]">
                        <span>Last Refreshed:</span>
                        <strong class="text-slate-300" id="modalLastSync">-</strong>
                    </div>
                </div>
            </div>

            <div class="pt-2 flex gap-2">
                <button onclick="saveSettings()" class="flex-1 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg text-xs transition">
                    Save & Sync Now
                </button>
                <button onclick="closeSettingsModal()" class="px-4 py-2 bg-slate-800 text-slate-300 font-bold rounded-lg text-xs hover:bg-slate-700 transition">
                    Close
                </button>
            </div>
        </div>
    </div>

    <!-- EMBEDDED DATASET (Guarantees Instant Offline & Standalone Operation) -->
    <script>
        window.INITIAL_DATA = {data_json_str};
    </script>

    <!-- App Logic Script -->
    <script>
        // State
        let currentTab = 'odds';
        let currentSport = 'ALL';
        let currentMarket = 'all';
        let currentPropCategory = 'ALL';
        let searchQuery = '';
        let showNovigMode = 'retail'; // 'retail' (guaranteed books) or 'all' (includes Novig)
        let currentArbFilter = 'all'; // 'all', 'retail', 'novig'
        let currentCalcTab = 'arb'; // 'arb', 'freebet', 'convert'
        let appData = window.INITIAL_DATA || {{ matchups: [], arbs: [], props: [] }};

        // Odds conversion helper for comparison
        function americanToDec(p) {{
            if (p === null || p === undefined || p === '') return 0;
            const num = parseFloat(String(p).replace('+', ''));
            if (isNaN(num) || num === 0) return 0;
            return num > 0 ? (1 + num / 100) : (1 + 100 / Math.abs(num));
        }}

        // Bookmaker styling & compact 2-3 letter badges
        const BOOK_INFO = {{
            'Novig': {{ name: 'Novig', bg: 'bg-emerald-500 text-slate-950 font-black', code: 'NOV' }},
            'DraftKings': {{ name: 'DraftKings', bg: 'bg-lime-500/25 text-lime-300 border border-lime-500/40', code: 'DK' }},
            'FanDuel': {{ name: 'FanDuel', bg: 'bg-blue-500/25 text-blue-300 border border-blue-500/40', code: 'FD' }},
            'BetMGM': {{ name: 'BetMGM', bg: 'bg-amber-500/25 text-amber-300 border border-amber-500/40', code: 'MGM' }},
            'Caesars': {{ name: 'Caesars', bg: 'bg-yellow-500/25 text-yellow-300 border border-yellow-500/40', code: 'CZR' }},
            'Fanatics': {{ name: 'Fanatics', bg: 'bg-red-500/25 text-red-300 border border-red-500/40', code: 'FAN' }},
            'BetRivers': {{ name: 'BetRivers', bg: 'bg-indigo-500/25 text-indigo-300 border border-indigo-500/40', code: 'RIV' }}
        }};

        function formatAmericanOdds(price) {{
            if (price === null || price === undefined || price === '') return '-';
            const p = parseFloat(price);
            if (isNaN(p)) return price;
            return p > 0 ? `+${{p}}` : `${{p}}`;
        }}

        function getBookBadge(bookName) {{
            if (!bookName) return '';
            const info = BOOK_INFO[bookName] || {{ 
                name: bookName, 
                bg: 'bg-slate-700 text-slate-300 border border-slate-600', 
                code: (bookName || '').slice(0, 3).toUpperCase() 
            }};
            return `<span class="inline-flex items-center justify-center text-[7.5px] font-black px-1 py-0.5 rounded leading-none shrink-0 ${{info.bg}}">${{info.code}}</span>`;
        }}

        function getTeamNickname(fullName) {{
            if (!fullName) return '';
            const parts = fullName.trim().split(' ');
            if (parts.length <= 1) return fullName;
            if (parts.length >= 2 && (parts[parts.length - 2].toLowerCase() === 'red' || parts[parts.length - 2].toLowerCase() === 'white')) {{
                return parts.slice(-2).join(' ');
            }}
            return parts[parts.length - 1];
        }}

        function formatGameTime(timeStr) {{
            if (!timeStr) return '';
            try {{
                const parts = timeStr.trim().split(' ');
                if (parts.length >= 2) {{
                    const dateParts = parts[0].split('-');
                    const timeParts = parts[1].split(':');
                    const month = parseInt(dateParts[1], 10);
                    const day = parseInt(dateParts[2], 10);
                    let hour = parseInt(timeParts[0], 10);
                    const min = timeParts[1];
                    const ampm = hour >= 12 ? 'PM' : 'AM';
                    hour = hour % 12;
                    hour = hour ? hour : 12;
                    
                    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    const mName = monthNames[month - 1] || `${{month}}`;
                    return `${{mName}} ${{day}} • ${{hour}}:${{min}} ${{ampm}} ET`;
                }}
                return timeStr.replace(/^\\d{{4}}-/, '');
            }} catch(e) {{
                return timeStr;
            }}
        }}

        // Tab Navigation
        function switchTab(tab) {{
            currentTab = tab;
            ['odds', 'arbs', 'props', 'calc'].forEach(t => {{
                const view = document.getElementById(`view${{t.charAt(0).toUpperCase() + t.slice(1)}}Screen`);
                const btn = document.getElementById(`navBtn_${{t}}`);
                if (t === tab) {{
                    view.classList.remove('hidden');
                    btn.classList.add('text-emerald-400', 'font-bold');
                    btn.classList.remove('text-slate-400');
                }} else {{
                    view.classList.add('hidden');
                    btn.classList.remove('text-emerald-400', 'font-bold');
                    btn.classList.add('text-slate-400');
                }}
            }});

            // Toggle sub filter visibility & source toggle
            const subFilter = document.getElementById('subFilterBar');
            const sourceToggle = document.getElementById('sourceToggleContainer');
            if (tab === 'calc') {{
                subFilter.classList.add('hidden');
            }} else {{
                subFilter.classList.remove('hidden');
                document.getElementById('marketPillsContainer').style.display = (tab === 'odds') ? 'grid' : 'none';
                if (sourceToggle) {{
                    sourceToggle.style.display = (tab === 'odds') ? 'flex' : 'none';
                }}
            }}

            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        // Sport Icons & Dynamic Sport Carousel
        const SPORT_ICONS = {{
            'ALL': '🔥',
            'WNBA': '🏀',
            'NBA': '🏀',
            'NFL': '🏈',
            'NHL': '🏒',
            'MLB': '⚾',
            'NCAAF': '🎓',
            'NCAAB': '🏀',
            'TENNIS': '🎾',
            'SOCCER': '⚽'
        }};

        function updateSportPills() {{
            const container = document.getElementById('sportPillsContainer');
            if (!container) return;
            const availableSports = new Set();
            (appData.matchups || []).forEach(m => {{
                if (m.sport_label) availableSports.add(m.sport_label);
            }});
            (appData.arbs || []).forEach(a => {{
                if (a.sport) availableSports.add(a.sport);
            }});

            const priorityOrder = ['WNBA', 'NFL', 'NHL', 'MLB', 'NCAAF', 'NBA'];
            const sortedSports = Array.from(availableSports).sort((a, b) => {{
                const idxA = priorityOrder.indexOf(a);
                const idxB = priorityOrder.indexOf(b);
                if (idxA !== -1 && idxB !== -1) return idxA - idxB;
                if (idxA !== -1) return -1;
                if (idxB !== -1) return 1;
                return a.localeCompare(b);
            }});

            let html = `
                <button onclick="setSportFilter('ALL')" id="sportBtn_ALL" class="sport-pill px-2.5 py-1 rounded-full ${{currentSport === 'ALL' ? 'bg-emerald-500 text-slate-950 font-bold' : 'bg-slate-800 text-slate-300 hover:text-white'}} whitespace-nowrap shadow-sm text-[11px] transition">
                    🔥 All Sports
                </button>
            `;

            sortedSports.forEach(s => {{
                const icon = SPORT_ICONS[s] || '🏆';
                const active = currentSport === s;
                html += `
                    <button onclick="setSportFilter('${{s}}')" id="sportBtn_${{s}}" class="sport-pill px-2.5 py-1 rounded-full ${{active ? 'bg-emerald-500 text-slate-950 font-bold' : 'bg-slate-800 text-slate-300 hover:text-white'}} whitespace-nowrap text-[11px] transition">
                        ${{icon}} ${{s}}
                    </button>
                `;
            }});

            container.innerHTML = html;
        }}

        // Sport Filtering
        function setSportFilter(sport) {{
            currentSport = sport;
            updateSportPills();
            renderAll();
        }}

        function setMarketFilter(mkt) {{
            currentMarket = mkt;
            document.querySelectorAll('.market-pill').forEach(el => {{
                el.classList.remove('bg-slate-700', 'text-white', 'font-bold');
                el.classList.add('text-slate-400');
            }});
            const active = document.getElementById(`mktBtn_${{mkt}}`);
            if (active) {{
                active.classList.add('bg-slate-700', 'text-white', 'font-bold');
                active.classList.remove('text-slate-400');
            }}
            renderMatchups();
        }}

        function setPropCategory(cat) {{
            currentPropCategory = cat;
            document.querySelectorAll('.prop-cat').forEach(el => {{
                el.classList.remove('bg-emerald-500', 'text-slate-950', 'font-bold');
                el.classList.add('bg-slate-800', 'text-slate-300');
            }});
            const active = Array.from(document.querySelectorAll('.prop-cat')).find(b => b.textContent.includes(cat) || (cat === 'ALL' && b.textContent.includes('All')));
            if (active) {{
                active.classList.add('bg-emerald-500', 'text-slate-950', 'font-bold');
                active.classList.remove('bg-slate-800', 'text-slate-300');
            }}
            renderProps();
        }}

        function handleSearch(val) {{
            searchQuery = val.trim().toLowerCase();
            const clearBtn = document.getElementById('clearSearchBtn');
            if (searchQuery) {{
                clearBtn.classList.remove('hidden');
            }} else {{
                clearBtn.classList.add('hidden');
            }}
            renderAll();
        }}

        function clearSearch() {{
            document.getElementById('searchInput').value = '';
            document.getElementById('clearSearchBtn').classList.add('hidden');
            searchQuery = '';
            renderAll();
        }}

        // Helper to query book lines for a specific game
        function getBookMarketData(m, marketType, bookName, isAway) {{
            const markets = m.all_markets || {{}};
            const bookData = markets[marketType]?.[bookName] || [];
            const teamName = isAway ? m.away_team : m.home_team;
            
            if (marketType === 'h2h') {{
                const item = bookData.find(x => x.outcome === teamName);
                return item ? {{ price: item.price, book: bookName }} : null;
            }} else if (marketType === 'spreads') {{
                const item = bookData.find(x => x.outcome === teamName);
                return item ? {{ point: item.point, price: item.price, book: bookName }} : null;
            }} else if (marketType === 'totals') {{
                const targetOutcome = isAway ? 'over' : 'under';
                const item = bookData.find(x => x.outcome.toLowerCase() === targetOutcome);
                return item ? {{ point: item.point, price: item.price, book: bookName }} : null;
            }}
            return null;
        }}

        // Pixel-Perfect Stacked Odds Cell (Action Network Style: Point Top, Price Bottom, Corner Badge)
        function renderCell(type, data, isAway, novigAlt) {{
            if (!data || data.price === null || data.price === undefined || data.price === '') {{
                return `
                    <div class="h-11 bg-slate-900/60 border border-slate-800/80 rounded-xl flex items-center justify-center text-slate-600 font-bold text-xs select-none">
                        -
                    </div>
                `;
            }}

            const isNovig = data.book === 'Novig';
            const bookBadge = getBookBadge(data.book);
            const formattedPrice = formatAmericanOdds(data.price);

            // Check if Novig offers an edge when in Retail Best mode
            const hasNovigEdge = (showNovigMode === 'retail' && !isNovig && novigAlt && novigAlt.price !== null && (americanToDec(novigAlt.price) > americanToDec(data.price) + 0.001));
            const novigEdgeBadge = hasNovigEdge ? `<span class="inline-flex items-center text-[7px] font-black px-1 py-0.2 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 leading-none shrink-0" title="Novig Exchange: ${{formatAmericanOdds(novigAlt.price)}}">⚡${{formatAmericanOdds(novigAlt.price)}}</span>` : '';

            if (type === 'ml') {{
                return `
                    <div class="h-11 bg-slate-900/90 border ${{isNovig ? 'border-emerald-500/50 bg-emerald-950/20' : 'border-slate-700/60'}} rounded-xl px-1 flex flex-col items-center justify-center select-none active:scale-95 transition">
                        <span class="text-xs font-black ${{isNovig ? 'text-emerald-400' : 'text-white'}} leading-none tracking-tight">${{formattedPrice}}</span>
                        <div class="flex items-center justify-center space-x-1 mt-1 leading-none">
                            ${{novigEdgeBadge ? novigEdgeBadge : '<span class="text-[8.5px] font-medium text-slate-400">ML</span>'}}
                            ${{bookBadge}}
                        </div>
                    </div>
                `;
            }}

            if (type === 'spread') {{
                const pointStr = data.point > 0 ? `+${{data.point}}` : `${{data.point}}`;
                return `
                    <div class="h-11 bg-slate-900/90 border ${{isNovig ? 'border-emerald-500/50 bg-emerald-950/20' : 'border-slate-700/60'}} rounded-xl px-1 flex flex-col items-center justify-center select-none active:scale-95 transition">
                        <div class="flex items-center justify-center space-x-1 leading-none">
                            <span class="text-xs font-bold text-white tracking-tight">${{pointStr}}</span>
                            ${{bookBadge}}
                        </div>
                        <div class="flex items-center justify-center space-x-1 mt-1 leading-none">
                            <span class="text-[9.5px] font-extrabold ${{isNovig ? 'text-emerald-400' : 'text-slate-300'}}">${{formattedPrice}}</span>
                            ${{novigEdgeBadge}}
                        </div>
                    </div>
                `;
            }}

            if (type === 'total') {{
                const prefix = isAway ? 'o' : 'u';
                const pointStr = `${{prefix}}${{data.point}}`;
                return `
                    <div class="h-11 bg-slate-900/90 border ${{isNovig ? 'border-emerald-500/50 bg-emerald-950/20' : 'border-slate-700/60'}} rounded-xl px-1 flex flex-col items-center justify-center select-none active:scale-95 transition">
                        <div class="flex items-center justify-center space-x-1 leading-none">
                            <span class="text-xs font-bold text-white tracking-tight">${{pointStr}}</span>
                            ${{bookBadge}}
                        </div>
                        <div class="flex items-center justify-center space-x-1 mt-1 leading-none">
                            <span class="text-[9.5px] font-extrabold ${{isNovig ? 'text-emerald-400' : 'text-slate-300'}}">${{formattedPrice}}</span>
                            ${{novigEdgeBadge}}
                        </div>
                    </div>
                `;
            }}
        }}

        // Render Matchups
        function renderMatchups() {{
            const container = document.getElementById('matchupsContainer');
            let list = appData.matchups || [];

            if (currentSport !== 'ALL') {{
                list = list.filter(m => m.sport_label === currentSport);
            }}

            if (searchQuery) {{
                list = list.filter(m => 
                    m.home_team.toLowerCase().includes(searchQuery) ||
                    m.away_team.toLowerCase().includes(searchQuery) ||
                    m.home_abbr.toLowerCase().includes(searchQuery) ||
                    m.away_abbr.toLowerCase().includes(searchQuery)
                );
            }}

            document.getElementById('matchupCountLabel').textContent = `Showing ${{list.length}} ${{currentSport === 'ALL' ? 'Upcoming' : currentSport}} Games (${{showNovigMode === 'retail' ? 'Retail Best' : 'Retail + Novig'}})`;

            if (list.length === 0) {{
                container.innerHTML = `
                    <div class="text-center py-12 text-slate-500 text-xs">
                        No matchups found matching your filters.
                    </div>
                `;
                return;
            }}

            let html = '';
            list.forEach((m) => {{
                const lines = m.best_lines || {{}};
                
                // Select lines based on active mode
                const useLines = (showNovigMode === 'retail') ? {{
                    h2h_away: lines.retail_h2h_away || lines.h2h_away,
                    h2h_home: lines.retail_h2h_home || lines.h2h_home,
                    spread_away: lines.retail_spread_away || lines.spread_away,
                    spread_home: lines.retail_spread_home || lines.spread_home,
                    total_over: lines.retail_total_over || lines.total_over,
                    total_under: lines.retail_total_under || lines.total_under,
                }} : lines;

                const novigLines = {{
                    h2h_away: lines.novig_h2h_away,
                    h2h_home: lines.novig_h2h_home,
                    spread_away: lines.novig_spread_away,
                    spread_home: lines.novig_spread_home,
                    total_over: lines.novig_total_over,
                    total_under: lines.novig_total_under,
                }};

                const hasNovigEdgeAny = (
                    (novigLines.h2h_away && useLines.h2h_away && americanToDec(novigLines.h2h_away.price) > americanToDec(useLines.h2h_away.price) + 0.001) ||
                    (novigLines.h2h_home && useLines.h2h_home && americanToDec(novigLines.h2h_home.price) > americanToDec(useLines.h2h_home.price) + 0.001) ||
                    (novigLines.spread_away && useLines.spread_away && americanToDec(novigLines.spread_away.price) > americanToDec(useLines.spread_away.price) + 0.001) ||
                    (novigLines.spread_home && useLines.spread_home && americanToDec(novigLines.spread_home.price) > americanToDec(useLines.spread_home.price) + 0.001) ||
                    (novigLines.total_over && useLines.total_over && americanToDec(novigLines.total_over.price) > americanToDec(useLines.total_over.price) + 0.001) ||
                    (novigLines.total_under && useLines.total_under && americanToDec(novigLines.total_under.price) > americanToDec(useLines.total_under.price) + 0.001)
                );

                const hasNovigBest = (
                    lines.h2h_away?.book === 'Novig' || 
                    lines.h2h_home?.book === 'Novig' || 
                    lines.spread_away?.book === 'Novig' || 
                    lines.spread_home?.book === 'Novig' || 
                    lines.total_over?.book === 'Novig' || 
                    lines.total_under?.book === 'Novig'
                );

                let headerBadge = '';
                if (showNovigMode === 'retail') {{
                    if (hasNovigEdgeAny) {{
                        headerBadge = `<span class="inline-flex items-center gap-1 text-[9px] font-black px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shrink-0 whitespace-nowrap">⚡ Novig Edges</span>`;
                    }} else {{
                        headerBadge = `<span class="inline-flex items-center gap-1 text-[9px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 shrink-0 whitespace-nowrap">🏢 Guaranteed Retail</span>`;
                    }}
                }} else {{
                    if (hasNovigBest) {{
                        headerBadge = `<span class="inline-flex items-center gap-1 text-[9.5px] font-black px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shrink-0 whitespace-nowrap">⚡ Novig Best</span>`;
                    }}
                }}

                // Column Setup based on active Market Segment
                let colHeadersHtml = '';
                let awayCell1 = '', awayCell2 = '', awayCell3 = '';
                let homeCell1 = '', homeCell2 = '', homeCell3 = '';

                if (currentMarket === 'all') {{
                    colHeadersHtml = `
                        <div class="text-left font-bold text-slate-400">Teams</div>
                        <div class="truncate">Moneyline</div>
                        <div class="truncate">Spread</div>
                        <div class="truncate">Total</div>
                    `;
                    awayCell1 = renderCell('ml', useLines.h2h_away, true, novigLines.h2h_away);
                    awayCell2 = renderCell('spread', useLines.spread_away, true, novigLines.spread_away);
                    awayCell3 = renderCell('total', useLines.total_over, true, novigLines.total_over);

                    homeCell1 = renderCell('ml', useLines.h2h_home, false, novigLines.h2h_home);
                    homeCell2 = renderCell('spread', useLines.spread_home, false, novigLines.spread_home);
                    homeCell3 = renderCell('total', useLines.total_under, false, novigLines.total_under);
                }} else if (currentMarket === 'spreads') {{
                    colHeadersHtml = `
                        <div class="text-left font-bold text-slate-400">Teams</div>
                        <div class="text-emerald-400 truncate">Novig</div>
                        <div class="truncate">DraftKings</div>
                        <div class="truncate">FanDuel</div>
                    `;
                    const spdNovigAway = getBookMarketData(m, 'spreads', 'Novig', true) || novigLines.spread_away;
                    const spdDkAway = getBookMarketData(m, 'spreads', 'DraftKings', true);
                    const spdFdAway = getBookMarketData(m, 'spreads', 'FanDuel', true);

                    const spdNovigHome = getBookMarketData(m, 'spreads', 'Novig', false) || novigLines.spread_home;
                    const spdDkHome = getBookMarketData(m, 'spreads', 'DraftKings', false);
                    const spdFdHome = getBookMarketData(m, 'spreads', 'FanDuel', false);

                    awayCell1 = renderCell('spread', spdNovigAway, true);
                    awayCell2 = renderCell('spread', spdDkAway, true);
                    awayCell3 = renderCell('spread', spdFdAway, true);

                    homeCell1 = renderCell('spread', spdNovigHome, false);
                    homeCell2 = renderCell('spread', spdDkHome, false);
                    homeCell3 = renderCell('spread', spdFdHome, false);
                }} else if (currentMarket === 'totals') {{
                    colHeadersHtml = `
                        <div class="text-left font-bold text-slate-400">Teams</div>
                        <div class="text-emerald-400 truncate">Novig</div>
                        <div class="truncate">DraftKings</div>
                        <div class="truncate">FanDuel</div>
                    `;
                    const totNovigAway = getBookMarketData(m, 'totals', 'Novig', true) || novigLines.total_over;
                    const totDkAway = getBookMarketData(m, 'totals', 'DraftKings', true);
                    const totFdAway = getBookMarketData(m, 'totals', 'FanDuel', true);

                    const totNovigHome = getBookMarketData(m, 'totals', 'Novig', false) || novigLines.total_under;
                    const totDkHome = getBookMarketData(m, 'totals', 'DraftKings', false);
                    const totFdHome = getBookMarketData(m, 'totals', 'FanDuel', false);

                    awayCell1 = renderCell('total', totNovigAway, true);
                    awayCell2 = renderCell('total', totDkAway, true);
                    awayCell3 = renderCell('total', totFdAway, true);

                    homeCell1 = renderCell('total', totNovigHome, false);
                    homeCell2 = renderCell('total', totDkHome, false);
                    homeCell3 = renderCell('total', totFdHome, false);
                }} else if (currentMarket === 'h2h') {{
                    colHeadersHtml = `
                        <div class="text-left font-bold text-slate-400">Teams</div>
                        <div class="text-emerald-400 truncate">Novig</div>
                        <div class="truncate">DraftKings</div>
                        <div class="truncate">FanDuel</div>
                    `;
                    const mlNovigAway = getBookMarketData(m, 'h2h', 'Novig', true) || novigLines.h2h_away;
                    const mlDkAway = getBookMarketData(m, 'h2h', 'DraftKings', true);
                    const mlFdAway = getBookMarketData(m, 'h2h', 'FanDuel', true);

                    const mlNovigHome = getBookMarketData(m, 'h2h', 'Novig', false) || novigLines.h2h_home;
                    const mlDkHome = getBookMarketData(m, 'h2h', 'DraftKings', false);
                    const mlFdHome = getBookMarketData(m, 'h2h', 'FanDuel', false);

                    awayCell1 = renderCell('ml', mlNovigAway, true);
                    awayCell2 = renderCell('ml', mlDkAway, true);
                    awayCell3 = renderCell('ml', mlFdAway, true);

                    homeCell1 = renderCell('ml', mlNovigHome, false);
                    homeCell2 = renderCell('ml', mlDkHome, false);
                    homeCell3 = renderCell('ml', mlFdHome, false);
                }}

                html += `
                    <div class="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-3 shadow-sm hover:border-slate-600 transition">
                        <!-- Matchup Header -->
                        <div class="flex items-center justify-between text-xs pb-2 border-b border-slate-700/70 mb-2">
                            <div class="flex items-center space-x-1.5 font-bold text-slate-300 min-w-0 pr-1">
                                <span class="px-1.5 py-0.5 rounded bg-slate-700 text-[9.5px] font-black uppercase shrink-0">${{m.sport_label}}</span>
                                <span class="text-[11px] text-slate-400 font-medium truncate">${{formatGameTime(m.commence_time)}}</span>
                            </div>
                            ${{headerBadge}}
                        </div>

                        <!-- 4-Column Grid Headers -->
                        <div class="grid grid-cols-4 gap-1 text-center text-[9.5px] font-bold text-slate-400 uppercase tracking-wider mb-1.5 px-0.5">
                            ${{colHeadersHtml}}
                        </div>

                        <!-- Away Team Row -->
                        <div class="grid grid-cols-4 gap-1 items-center mb-1">
                            <div class="flex items-center space-x-1.5 pr-1 min-w-0">
                                <div class="w-6 h-6 rounded-full bg-slate-700/70 border border-slate-600/80 flex items-center justify-center text-[9px] font-black text-slate-200 shrink-0">
                                    ${{m.away_abbr.slice(0, 3)}}
                                </div>
                                <div class="min-w-0 flex-1">
                                    <div class="text-xs font-black text-white leading-tight truncate">${{m.away_abbr}}</div>
                                    <div class="text-[9.5px] text-slate-400 font-medium leading-tight truncate">${{getTeamNickname(m.away_team)}}</div>
                                </div>
                            </div>
                            <div class="min-w-0">${{awayCell1}}</div>
                            <div class="min-w-0">${{awayCell2}}</div>
                            <div class="min-w-0">${{awayCell3}}</div>
                        </div>

                        <!-- Home Team Row -->
                        <div class="grid grid-cols-4 gap-1 items-center">
                            <div class="flex items-center space-x-1.5 pr-1 min-w-0">
                                <div class="w-6 h-6 rounded-full bg-slate-700/70 border border-slate-600/80 flex items-center justify-center text-[9px] font-black text-slate-200 shrink-0">
                                    ${{m.home_abbr.slice(0, 3)}}
                                </div>
                                <div class="min-w-0 flex-1">
                                    <div class="text-xs font-black text-white leading-tight truncate">${{m.home_abbr}}</div>
                                    <div class="text-[9.5px] text-slate-400 font-medium leading-tight truncate">${{getTeamNickname(m.home_team)}}</div>
                                </div>
                            </div>
                            <div class="min-w-0">${{homeCell1}}</div>
                            <div class="min-w-0">${{homeCell2}}</div>
                            <div class="min-w-0">${{homeCell3}}</div>
                        </div>

                        <!-- Expand Accordion Button -->
                        <div class="mt-2 pt-1.5 border-t border-slate-700/60 flex items-center justify-between text-[11px]">
                            <button onclick="toggleGameDetails('${{m.id}}')" class="text-indigo-400 hover:text-indigo-300 font-semibold flex items-center space-x-1 active:scale-95 transition">
                                <span>Compare All Books</span>
                                <span id="arrow_${{m.id}}">▾</span>
                            </button>
                            <span class="text-slate-400 text-[10px]">7 sportsbooks tracked</span>
                        </div>

                        <!-- Hidden Detailed Breakdown -->
                        <div id="details_${{m.id}}" class="hidden mt-2 pt-2 border-t border-slate-700/80 text-xs">
                            <div class="overflow-x-auto no-scrollbar">
                                <table class="w-full text-left text-[10px]">
                                    <thead>
                                        <tr class="text-slate-400 border-b border-slate-700">
                                            <th class="py-1 px-1">Book</th>
                                            <th class="py-1 px-1">Away ML</th>
                                            <th class="py-1 px-1">Home ML</th>
                                            <th class="py-1 px-1">Spread</th>
                                            <th class="py-1 px-1">Total</th>
                                        </tr>
                                    </thead>
                                    <tbody class="divide-y divide-slate-800">
                                        ${{renderBookRows(m)}}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                `;
            }});

            container.innerHTML = html;
        }}

        function renderBookRows(m) {{
            const markets = m.all_markets || {{}};
            const allBooks = ['Novig', 'DraftKings', 'FanDuel', 'BetMGM', 'Caesars', 'Fanatics', 'BetRivers'];
            let rows = '';

            allBooks.forEach(b => {{
                const h2hList = markets.h2h?.[b] || [];
                const awayMl = h2hList.find(x => x.outcome === m.away_team)?.price;
                const homeMl = h2hList.find(x => x.outcome === m.home_team)?.price;

                const spreadList = markets.spreads?.[b] || [];
                const awaySpd = spreadList.find(x => x.outcome === m.away_team);

                const totalList = markets.totals?.[b] || [];
                const overTot = totalList.find(x => x.outcome.toLowerCase() === 'over');

                const isNovig = b === 'Novig';

                if (awayMl || homeMl || awaySpd || overTot) {{
                    rows += `
                        <tr class="${{isNovig ? 'bg-emerald-500/10' : 'hover:bg-slate-800/40'}}">
                            <td class="py-1.5 px-1 font-bold ${{isNovig ? 'text-emerald-400' : 'text-slate-300'}} flex items-center space-x-1">
                                ${{getBookBadge(b)}}
                                <span>${{b}}</span>
                            </td>
                            <td class="py-1.5 px-1 ${{b === m.best_lines?.h2h_away?.book ? 'text-emerald-400 font-black' : 'text-slate-300'}}">${{formatAmericanOdds(awayMl)}}</td>
                            <td class="py-1.5 px-1 ${{b === m.best_lines?.h2h_home?.book ? 'text-emerald-400 font-black' : 'text-slate-300'}}">${{formatAmericanOdds(homeMl)}}</td>
                            <td class="py-1.5 px-1 text-slate-300">${{awaySpd ? `${{awaySpd.point > 0 ? '+' : ''}}${{awaySpd.point}} (${{formatAmericanOdds(awaySpd.price)}})` : '-'}}</td>
                            <td class="py-1.5 px-1 text-slate-300">${{overTot ? `${{overTot.point}} (${{formatAmericanOdds(overTot.price)}})` : '-'}}</td>
                        </tr>
                    `;
                }}
            }});
            return rows || '<tr><td colspan="5" class="py-2 text-center text-slate-500">No expanded lines available</td></tr>';
        }}

        function toggleGameDetails(id) {{
            const el = document.getElementById(`details_${{id}}`);
            const arrow = document.getElementById(`arrow_${{id}}`);
            if (el.classList.contains('hidden')) {{
                el.classList.remove('hidden');
                arrow.textContent = '▴';
            }} else {{
                el.classList.add('hidden');
                arrow.textContent = '▾';
            }}
        }}

        function setArbFilter(filter) {{
            currentArbFilter = filter;
            ['all', 'retail', 'novig'].forEach(f => {{
                const btn = document.getElementById(`arbFilter_${{f}}`);
                if (!btn) return;
                if (f === filter) {{
                    btn.className = 'flex-1 py-1 rounded-lg bg-emerald-500 text-slate-950 font-bold shadow-xs transition text-center text-[10px]';
                }} else {{
                    btn.className = 'flex-1 py-1 rounded-lg text-slate-400 hover:text-white transition text-center text-[10px]';
                }}
            }});
            renderArbs();
        }}

        // Render Arbitrage / +EV Cards (OddsShopper Screenshot 1 Style)
        function renderArbs() {{
            const container = document.getElementById('arbsContainer');
            let allList = appData.arbs || [];

            // Rule: Novig can only be AT MOST ONE side of the bet!
            allList = allList.filter(a => !(a.side_a.book === 'Novig' && a.side_b.book === 'Novig'));

            if (currentSport !== 'ALL') {{
                allList = allList.filter(a => a.sport === currentSport);
            }}

            if (searchQuery) {{
                allList = allList.filter(a => 
                    a.matchup.toLowerCase().includes(searchQuery) ||
                    a.market.toLowerCase().includes(searchQuery) ||
                    a.side_a.outcome.toLowerCase().includes(searchQuery) ||
                    a.side_b.outcome.toLowerCase().includes(searchQuery)
                );
            }}

            // Sort by guaranteed profit / ROI from most to least!
            allList.sort((a, b) => (parseFloat(b.roi) || 0) - (parseFloat(a.roi) || 0));

            // Count metrics across all filtered arbs
            const totalCount = allList.length;
            const retailCount = allList.filter(a => !a.is_novig).length;
            const novigCount = allList.filter(a => a.is_novig).length;

            const pillAll = document.getElementById('arbPillAllCount');
            const pillRetail = document.getElementById('arbPillRetailCount');
            const pillNovig = document.getElementById('arbPillNovigCount');
            if (pillAll) pillAll.textContent = totalCount;
            if (pillRetail) pillRetail.textContent = retailCount;
            if (pillNovig) pillNovig.textContent = novigCount;

            let list = allList;
            if (currentArbFilter === 'retail') {{
                list = allList.filter(a => !a.is_novig);
            }} else if (currentArbFilter === 'novig') {{
                list = allList.filter(a => a.is_novig);
            }}

            document.getElementById('arbBadgeCount').textContent = list.length;
            const filterLabel = currentArbFilter === 'retail' ? 'Retail Only' : (currentArbFilter === 'novig' ? 'Novig Hedge' : 'All Spots');
            document.getElementById('arbCountLabel').textContent = `${{list.length}} Active Spots (${{filterLabel}} • Sorted by Profit)`;

            if (list.length === 0) {{
                container.innerHTML = `
                    <div class="text-center py-12 text-slate-500 text-xs">
                        No active arbitrage or low-hold spots found matching your filter.
                    </div>
                `;
                return;
            }}

            const globalStake = parseFloat(document.getElementById('globalStakeInput').value) || 250;

            let html = '';
            list.forEach((arb, idx) => {{
                const p1 = arb.side_a.price;
                const p2 = arb.side_b.price;
                const stakes = computeHedge(p1, p2, globalStake);

                const roiClass = arb.roi > 0.5 ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30';
                const roiLabel = arb.is_middle ? `🎯 MIDDLE SPOT` : (arb.roi > 0 ? `+${{arb.roi}}% ROI` : `⚡ ${{arb.hold}}% Low Hold`);

                const isNovigArb = arb.is_novig;
                const edgeBadge = isNovigArb ? 
                    `<span class="text-[8.5px] font-bold text-amber-300 bg-amber-500/15 border border-amber-500/30 px-1.5 py-0.5 rounded shrink-0">⚡ Novig Hedge</span>` :
                    `<span class="text-[8.5px] font-bold text-emerald-300 bg-emerald-500/15 border border-emerald-500/30 px-1.5 py-0.5 rounded shrink-0">🏢 Retail Only</span>`;

                html += `
                    <div class="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-3 shadow-sm hover:border-slate-600 transition">
                        <!-- Card Top Bar -->
                        <div class="flex items-center justify-between mb-2 pb-2 border-b border-slate-700/70">
                            <div class="min-w-0 flex-1 pr-2">
                                <div class="flex items-center space-x-1.5">
                                    <span class="text-[9.5px] px-1.5 py-0.5 rounded bg-slate-700 text-slate-200 font-bold uppercase shrink-0">${{arb.sport}}</span>
                                    <h3 class="text-xs font-bold text-white truncate">${{arb.matchup}}</h3>
                                </div>
                                <div class="flex items-center space-x-1.5 mt-0.5">
                                    <span class="text-[10px] text-slate-400 truncate">${{arb.market}} • ${{formatGameTime(arb.commence_time)}}</span>
                                    ${{edgeBadge}}
                                </div>
                            </div>
                            <span class="text-[9.5px] font-black px-2 py-0.5 rounded-full border ${{roiClass}} shadow-xs shrink-0 whitespace-nowrap">
                                ${{roiLabel}}
                            </span>
                        </div>

                        <!-- 2-Way Comparison Columns (OddsShopper Style) -->
                        <div class="grid grid-cols-2 gap-2 my-2.5">
                            <!-- Side A -->
                            <div class="bg-slate-900/90 rounded-xl p-2.5 border border-slate-700/60 relative">
                                <div class="flex items-center justify-between mb-1">
                                    <div class="flex items-center space-x-1 min-w-0">
                                        ${{getBookBadge(arb.side_a.book)}}
                                        <span class="text-xs font-bold text-white truncate">${{arb.side_a.book}}</span>
                                    </div>
                                    ${{arb.side_a.liquidity ? `<span class="text-[9px] text-emerald-400 font-semibold shrink-0">Liq $${{arb.side_a.liquidity}}</span>` : ''}}
                                </div>
                                <div class="text-[11px] font-bold text-slate-200 truncate">${{arb.side_a.outcome}}</div>
                                <div class="text-sm font-black text-cyan-400 my-0.5">${{formatAmericanOdds(arb.side_a.price)}}</div>
                                
                                <div class="mt-1.5 pt-1.5 border-t border-slate-800 text-[10px]">
                                    <div class="text-slate-400">Bet Size:</div>
                                    <input type="number" id="stakeA_${{idx}}" value="${{stakes.stakeA}}" oninput="recalcArbCard('${{idx}}', '${{p1}}', '${{p2}}', 'A')"
                                        class="w-full bg-slate-950 border border-slate-700 rounded px-1.5 py-1 text-xs font-bold text-white my-0.5 text-center focus:border-emerald-500 focus:outline-none">
                                    <div class="flex justify-between text-[10px] text-slate-400 mt-1">
                                        <span>Payout:</span>
                                        <strong id="payoutA_${{idx}}" class="text-emerald-400 font-extrabold">$${{stakes.payoutA}}</strong>
                                    </div>
                                </div>
                            </div>

                            <!-- Side B -->
                            <div class="bg-slate-900/90 rounded-xl p-2.5 border border-slate-700/60 relative">
                                <div class="flex items-center justify-between mb-1">
                                    <div class="flex items-center space-x-1 min-w-0">
                                        ${{getBookBadge(arb.side_b.book)}}
                                        <span class="text-xs font-bold text-white truncate">${{arb.side_b.book}}</span>
                                    </div>
                                    ${{arb.side_b.liquidity ? `<span class="text-[9px] text-emerald-400 font-semibold shrink-0">Liq $${{arb.side_b.liquidity}}</span>` : ''}}
                                </div>
                                <div class="text-[11px] font-bold text-slate-200 truncate">${{arb.side_b.outcome}}</div>
                                <div class="text-sm font-black text-cyan-400 my-0.5">${{formatAmericanOdds(arb.side_b.price)}}</div>
                                
                                <div class="mt-1.5 pt-1.5 border-t border-slate-800 text-[10px]">
                                    <div class="text-slate-400">Hedge Size:</div>
                                    <input type="number" id="stakeB_${{idx}}" value="${{stakes.stakeB}}" oninput="recalcArbCard('${{idx}}', '${{p1}}', '${{p2}}', 'B')"
                                        class="w-full bg-slate-950 border border-slate-700 rounded px-1.5 py-1 text-xs font-bold text-white my-0.5 text-center focus:border-emerald-500 focus:outline-none">
                                    <div class="flex justify-between text-[10px] text-slate-400 mt-1">
                                        <span>Payout:</span>
                                        <strong id="payoutB_${{idx}}" class="text-emerald-400 font-extrabold">$${{stakes.payoutB}}</strong>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Card Footer / Actions -->
                        <div class="flex items-center justify-between pt-1.5 border-t border-slate-700/60 text-xs">
                            <span class="text-slate-400 font-medium text-[11px]" id="profitBadge_${{idx}}">
                                ${{parseFloat(stakes.profit) >= 0 ? 'Guaranteed Profit:' : 'Hedge Hold Cost:'}} <strong class="${{parseFloat(stakes.profit) >= 0 ? 'text-emerald-400' : 'text-slate-400'}} font-extrabold">${{formatProfit(stakes.profit)}}</strong>
                            </span>
                            ${{isNovigArb ? `
                                <span class="text-[9.5px] text-amber-300 font-bold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
                                    ⚡ Fill Novig First
                                </span>
                            ` : `
                                <span class="text-[9.5px] text-emerald-300 font-semibold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
                                    🏢 Bet ${{arb.side_a.book}} First
                                </span>
                            `}}
                        </div>
                    </div>
                `;
            }});

            container.innerHTML = html;
        }}

        function formatProfit(profit) {{
            const num = parseFloat(profit);
            if (isNaN(num)) return '$0.00';
            if (num >= 0) return `+$${{num.toFixed(2)}}`;
            return `-$${{Math.abs(num).toFixed(2)}}`;
        }}

        function computeHedge(p1, p2, stakeA) {{
            const dec1 = p1 > 0 ? (1 + p1 / 100) : (1 + 100 / Math.abs(p1));
            const dec2 = p2 > 0 ? (1 + p2 / 100) : (1 + 100 / Math.abs(p2));
            const payoutA = stakeA * dec1;
            const stakeB = Math.round((payoutA / dec2) * 100) / 100;
            const payoutB = stakeB * dec2;
            const totalOutlay = stakeA + stakeB;
            const netProfit = Math.round((Math.min(payoutA, payoutB) - totalOutlay) * 100) / 100;

            return {{
                stakeA: stakeA.toFixed(2),
                stakeB: stakeB.toFixed(2),
                payoutA: payoutA.toFixed(2),
                payoutB: payoutB.toFixed(2),
                profit: netProfit.toFixed(2)
            }};
        }}

        function recalcArbCard(idx, p1, p2, changedSide) {{
            let sA = parseFloat(document.getElementById(`stakeA_${{idx}}`).value) || 0;
            const dec1 = p1 > 0 ? (1 + p1 / 100) : (1 + 100 / Math.abs(p1));
            const dec2 = p2 > 0 ? (1 + p2 / 100) : (1 + 100 / Math.abs(p2));

            if (changedSide === 'A') {{
                const payoutA = sA * dec1;
                const sB = Math.round((payoutA / dec2) * 100) / 100;
                const payoutB = sB * dec2;
                document.getElementById(`stakeB_${{idx}}`).value = sB.toFixed(2);
                document.getElementById(`payoutA_${{idx}}`).textContent = `$${{payoutA.toFixed(2)}}`;
                document.getElementById(`payoutB_${{idx}}`).textContent = `$${{payoutB.toFixed(2)}}`;
                const profit = Math.round((payoutA - (sA + sB)) * 100) / 100;
                document.getElementById(`profitBadge_${{idx}}`).innerHTML = `${{profit >= 0 ? 'Guaranteed Profit:' : 'Hedge Hold Cost:'}} <strong class="${{profit >= 0 ? 'text-emerald-400' : 'text-slate-400'}} font-extrabold">${{formatProfit(profit)}}</strong>`;
            }} else {{
                let sB = parseFloat(document.getElementById(`stakeB_${{idx}}`).value) || 0;
                const payoutB = sB * dec2;
                sA = Math.round((payoutB / dec1) * 100) / 100;
                const payoutA = sA * dec1;
                document.getElementById(`stakeA_${{idx}}`).value = sA.toFixed(2);
                document.getElementById(`payoutA_${{idx}}`).textContent = `$${{payoutA.toFixed(2)}}`;
                document.getElementById(`payoutB_${{idx}}`).textContent = `$${{payoutB.toFixed(2)}}`;
                const profit = Math.round((payoutB - (sA + sB)) * 100) / 100;
                document.getElementById(`profitBadge_${{idx}}`).innerHTML = `${{profit >= 0 ? 'Guaranteed Profit:' : 'Hedge Hold Cost:'}} <strong class="${{profit >= 0 ? 'text-emerald-400' : 'text-slate-400'}} font-extrabold">${{formatProfit(profit)}}</strong>`;
            }}
        }}

        function updateAllArbStakes(val) {{
            renderArbs();
        }}

        // Render Player Props
        function renderProps() {{
            const container = document.getElementById('propsContainer');
            let list = appData.props || [];

            if (currentPropCategory !== 'ALL') {{
                list = list.filter(p => p.market.toLowerCase().includes(currentPropCategory.toLowerCase()));
            }}

            if (searchQuery) {{
                list = list.filter(p => 
                    p.player.toLowerCase().includes(searchQuery) ||
                    p.matchup.toLowerCase().includes(searchQuery) ||
                    p.market.toLowerCase().includes(searchQuery)
                );
            }}

            if (list.length === 0) {{
                container.innerHTML = `
                    <div class="text-center py-12 text-slate-500 text-xs">
                        No player props found matching your criteria.
                    </div>
                `;
                return;
            }}

            let html = '';
            list.forEach((p, idx) => {{
                const bestOver = p.best_over;
                const bestUnder = p.best_under;
                const bestYes = p.best_yes;

                html += `
                    <div class="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-3 shadow-xs">
                        <div class="flex items-center justify-between mb-2">
                            <div class="min-w-0 flex-1 pr-2">
                                <h3 class="text-xs font-black text-white truncate">${{p.player}}</h3>
                                <p class="text-[10px] text-slate-400 truncate">${{p.market}} • ${{p.matchup}}</p>
                            </div>
                            ${{p.discrepancy ? `<span class="text-[9.5px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 shrink-0 whitespace-nowrap">⚡ ${{p.discrepancy}}</span>` : ''}}
                        </div>

                        ${{bestYes ? `
                            <div class="bg-slate-900/90 rounded-xl p-2.5 border border-slate-700/60 flex items-center justify-between">
                                <span class="text-xs font-semibold text-slate-300">Anytime TD Best Price:</span>
                                <div class="flex items-center space-x-1.5">
                                    <span class="text-xs font-black text-emerald-400">${{formatAmericanOdds(bestYes.price)}}</span>
                                    ${{getBookBadge(bestYes.book)}}
                                </div>
                            </div>
                        ` : `
                            <div class="grid grid-cols-2 gap-2 text-xs">
                                <div class="bg-slate-900/90 rounded-xl p-2 border border-slate-700/60 flex items-center justify-between">
                                    <div>
                                        <div class="text-[9px] font-bold text-slate-400 uppercase">Over ${{bestOver ? bestOver.line : ''}}</div>
                                        <div class="text-xs font-black text-emerald-400 mt-0.5">${{bestOver ? formatAmericanOdds(bestOver.price) : '-'}}</div>
                                    </div>
                                    <div>${{bestOver ? getBookBadge(bestOver.book) : ''}}</div>
                                </div>
                                <div class="bg-slate-900/90 rounded-xl p-2 border border-slate-700/60 flex items-center justify-between">
                                    <div>
                                        <div class="text-[9px] font-bold text-slate-400 uppercase">Under ${{bestUnder ? bestUnder.line : ''}}</div>
                                        <div class="text-xs font-black text-emerald-400 mt-0.5">${{bestUnder ? formatAmericanOdds(bestUnder.price) : '-'}}</div>
                                    </div>
                                    <div>${{bestUnder ? getBookBadge(bestUnder.book) : ''}}</div>
                                </div>
                            </div>
                        `}}

                        <!-- Book Breakdown Accordion -->
                        <div class="mt-2 pt-1.5 border-t border-slate-700/60 flex justify-between items-center text-[10px]">
                            <button onclick="togglePropDetails('${{idx}}')" class="text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1">
                                <span>View ${{p.all_lines.length}} Sportsbook Lines</span>
                                <span id="propArrow_${{idx}}">▾</span>
                            </button>
                            <span class="text-slate-500">${{p.all_lines.length}} books</span>
                        </div>

                        <div id="propDetails_${{idx}}" class="hidden mt-2 pt-2 border-t border-slate-700/60">
                            <div class="grid grid-cols-2 gap-1.5 text-[10px]">
                                ${{p.all_lines.map(l => `
                                    <div class="flex items-center justify-between bg-slate-900/60 p-1.5 rounded-lg border border-slate-800">
                                        <div class="flex items-center space-x-1 min-w-0">
                                            ${{getBookBadge(l.book)}}
                                            <span class="text-slate-300 text-[9.5px] truncate">${{l.outcome}} ${{l.line !== null ? l.line : ''}}</span>
                                        </div>
                                        <span class="font-black text-white shrink-0 ml-1">${{formatAmericanOdds(l.price)}}</span>
                                    </div>
                                `).join('')}}
                            </div>
                        </div>
                    </div>
                `;
            }});

            container.innerHTML = html;
        }}

        function togglePropDetails(idx) {{
            const el = document.getElementById(`propDetails_${{idx}}`);
            const arrow = document.getElementById(`propArrow_${{idx}}`);
            if (el.classList.contains('hidden')) {{
                el.classList.remove('hidden');
                arrow.textContent = '▴';
            }} else {{
                el.classList.add('hidden');
                arrow.textContent = '▾';
            }}
        }}

        // Novig Mode Control (Retail Best vs All/Novig)
        function setNovigDisplayMode(mode) {{
            showNovigMode = mode;
            updateNovigModeButtons();
            renderMatchups();
        }}

        function updateNovigModeButtons() {{
            const btnRetail = document.getElementById('modeBtnRetail');
            const btnAll = document.getElementById('modeBtnAll');
            const label = document.getElementById('activeSourceLabel');
            if (!btnRetail || !btnAll) return;
            if (showNovigMode === 'retail') {{
                btnRetail.className = 'px-2 py-0.5 rounded-md font-bold text-[10px] bg-indigo-600 text-white shadow-xs transition';
                btnAll.className = 'px-2 py-0.5 rounded-md font-bold text-[10px] text-slate-400 hover:text-slate-200 transition';
                if (label) label.textContent = '6 Retail Books';
            }} else {{
                btnRetail.className = 'px-2 py-0.5 rounded-md font-bold text-[10px] text-slate-400 hover:text-slate-200 transition';
                btnAll.className = 'px-2 py-0.5 rounded-md font-bold text-[10px] bg-emerald-500 text-slate-950 shadow-xs transition';
                if (label) label.textContent = 'Retail + Novig';
            }}
        }}

        // Calculator Tab Switching
        function switchCalcSubTab(subTab) {{
            currentCalcTab = subTab;
            ['arb', 'freebet', 'convert'].forEach(t => {{
                const btn = document.getElementById(`calcTab_${{t}}`);
                const panel = document.getElementById(`calcPanel_${{t}}`);
                if (!btn || !panel) return;
                if (t === subTab) {{
                    btn.className = 'flex-1 py-1.5 rounded-lg bg-emerald-500 text-slate-950 font-bold shadow-xs transition text-center text-[11px]';
                    panel.classList.remove('hidden');
                }} else {{
                    btn.className = 'flex-1 py-1.5 rounded-lg text-slate-400 hover:text-white transition text-center text-[11px]';
                    panel.classList.add('hidden');
                }}
            }});
        }}

        // Calculator 1: 2-Way Arbitrage
        function calculateArb() {{
            const odds1 = parseFloat(document.getElementById('calcOdds1').value) || 0;
            const odds2 = parseFloat(document.getElementById('calcOdds2').value) || 0;
            const stake1 = parseFloat(document.getElementById('calcStake1').value) || 0;

            const res = computeHedge(odds1, odds2, stake1);
            const stakeB = parseFloat(res.stakeB) || 0;
            const totalOutlay = stake1 + stakeB;
            const payoutA = parseFloat(res.payoutA) || 0;
            const payoutB = parseFloat(res.payoutB) || 0;
            const minPayout = Math.min(payoutA, payoutB);
            const profit = Math.round((minPayout - totalOutlay) * 100) / 100;
            const roi = totalOutlay > 0 ? ((profit / totalOutlay) * 100).toFixed(2) : '0.00';

            document.getElementById('calcHedgeStake').textContent = `$${{res.stakeB}}`;
            const p1El = document.getElementById('calcPayout1');
            if (p1El) p1El.textContent = `$${{res.payoutA}}`;
            const p2El = document.getElementById('calcPayout2');
            if (p2El) p2El.textContent = `$${{res.payoutB}}`;
            const sumP1 = document.getElementById('calcSummaryPayout1');
            if (sumP1) sumP1.textContent = `$${{res.payoutA}}`;
            const sumP2 = document.getElementById('calcSummaryPayout2');
            if (sumP2) sumP2.textContent = `$${{res.payoutB}}`;

            document.getElementById('calcTotalOutlay').textContent = `$${{totalOutlay.toFixed(2)}}`;
            document.getElementById('calcGuaranteedPayout').textContent = `$${{minPayout.toFixed(2)}}`;
            document.getElementById('calcNetProfit').textContent = `${{profit >= 0 ? '+' : ''}}$${{profit.toFixed(2)}} (${{profit >= 0 ? '+' : ''}}${{roi}}% ROI)`;
        }}

        // Helper to parse American odds string into decimal
        function parseAmericanToDecimal(oddsStr) {{
            if (!oddsStr) return 0;
            const cleaned = String(oddsStr).replace('+', '').trim();
            const val = parseFloat(cleaned);
            if (isNaN(val) || val === 0) return 0;
            if (val > 0) {{
                return 1 + (val / 100);
            }} else {{
                return 1 + (100 / Math.abs(val));
            }}
        }}

        // Helper to convert decimal into clean fraction string
        function decimalToFraction(d) {{
            const target = d - 1;
            if (target <= 0.001) return '0/1';
            let bestNum = 1, bestDen = 1, bestDiff = 999;
            for (let den = 1; den <= 20; den++) {{
                const num = Math.round(target * den);
                const diff = Math.abs((num / den) - target);
                if (diff < bestDiff) {{
                    bestDiff = diff;
                    bestNum = num;
                    bestDen = den;
                }}
                if (diff < 0.001) break;
            }}
            return `${{bestNum}}/${{bestDen}}`;
        }}

        // Calculator 2: Free Bet Converter (SNR Model)
        function calculateFreeBet() {{
            const fbVal = parseFloat(document.getElementById('fbAmount').value) || 0;
            const fbOddsRaw = document.getElementById('fbOdds').value;
            const hedgeOddsRaw = document.getElementById('fbHedgeOdds').value;

            const dFb = parseAmericanToDecimal(fbOddsRaw);
            const dH = parseAmericanToDecimal(hedgeOddsRaw);

            if (fbVal <= 0 || dFb <= 1 || dH <= 1) {{
                document.getElementById('fbHedgeStake').textContent = '$0.00';
                document.getElementById('fbGuaranteedCash').textContent = '$0.00';
                document.getElementById('fbConversionRate').textContent = '0.0%';
                document.getElementById('fbScenario1').innerHTML = 'Enter valid odds & stake';
                document.getElementById('fbScenario2').innerHTML = 'Enter valid odds & stake';
                return;
            }}

            // SNR Model: Free Bet payout excludes initial stake
            const winFb = fbVal * (dFb - 1);
            const hedgeStake = Math.round((winFb / dH) * 100) / 100;
            const profitFbWin = winFb - hedgeStake;
            const profitHedgeWin = Math.round((hedgeStake * (dH - 1)) * 100) / 100;
            const guaranteedCash = Math.min(profitFbWin, profitHedgeWin);
            const conversionPct = fbVal > 0 ? ((guaranteedCash / fbVal) * 100) : 0;

            document.getElementById('fbHedgeStake').textContent = `$${{hedgeStake.toFixed(2)}}`;
            document.getElementById('fbGuaranteedCash').textContent = `+$${{guaranteedCash.toFixed(2)}}`;
            document.getElementById('fbConversionRate').textContent = `${{conversionPct.toFixed(1)}}%`;

            document.getElementById('fbScenario1').innerHTML = `+$${{winFb.toFixed(2)}} win - $${{hedgeStake.toFixed(2)}} hedge = <strong class="text-white">+$${{profitFbWin.toFixed(2)}}</strong>`;
            document.getElementById('fbScenario2').innerHTML = `+$${{(hedgeStake * dH).toFixed(2)}} payout - $${{hedgeStake.toFixed(2)}} hedge = <strong class="text-white">+$${{profitHedgeWin.toFixed(2)}}</strong>`;
        }}

        // Calculator 3: Universal Odds Translator & Payout Simulator
        function translateFromAmerican(val) {{
            if (document.getElementById('convAmerican').value !== val) {{
                document.getElementById('convAmerican').value = val;
            }}
            const d = parseAmericanToDecimal(val);
            if (d <= 1) return;
            const prob = (1 / d) * 100;
            const frac = decimalToFraction(d);
            document.getElementById('convDecimal').value = d.toFixed(2);
            document.getElementById('convProb').value = prob.toFixed(1);
            document.getElementById('convFractional').value = frac;
            updatePayoutEstimate();
        }}

        function translateFromDecimal(val) {{
            const d = parseFloat(val);
            if (isNaN(d) || d <= 1) return;
            let am = 0;
            if (d >= 2.0) {{
                am = Math.round((d - 1) * 100);
            }} else {{
                am = Math.round(-100 / (d - 1));
            }}
            const prob = (1 / d) * 100;
            const frac = decimalToFraction(d);
            document.getElementById('convAmerican').value = am > 0 ? `+${{am}}` : `${{am}}`;
            document.getElementById('convProb').value = prob.toFixed(1);
            document.getElementById('convFractional').value = frac;
            updatePayoutEstimate();
        }}

        function translateFromProb(val) {{
            const p = parseFloat(val);
            if (isNaN(p) || p <= 0 || p >= 100) return;
            const d = 100 / p;
            let am = 0;
            if (d >= 2.0) {{
                am = Math.round((d - 1) * 100);
            }} else {{
                am = Math.round(-100 / (d - 1));
            }}
            const frac = decimalToFraction(d);
            document.getElementById('convAmerican').value = am > 0 ? `+${{am}}` : `${{am}}`;
            document.getElementById('convDecimal').value = d.toFixed(2);
            document.getElementById('convFractional').value = frac;
            updatePayoutEstimate();
        }}

        function translateFromFractional(val) {{
            if (!val || !val.includes('/')) return;
            const parts = val.split('/');
            const num = parseFloat(parts[0]);
            const den = parseFloat(parts[1]);
            if (isNaN(num) || isNaN(den) || den === 0) return;
            const d = 1 + (num / den);
            if (d <= 1) return;
            let am = 0;
            if (d >= 2.0) {{
                am = Math.round((d - 1) * 100);
            }} else {{
                am = Math.round(-100 / (d - 1));
            }}
            const prob = (1 / d) * 100;
            document.getElementById('convAmerican').value = am > 0 ? `+${{am}}` : `${{am}}`;
            document.getElementById('convDecimal').value = d.toFixed(2);
            document.getElementById('convProb').value = prob.toFixed(1);
            updatePayoutEstimate();
        }}

        function updatePayoutEstimate() {{
            const stake = parseFloat(document.getElementById('convStake').value) || 0;
            const d = parseFloat(document.getElementById('convDecimal').value) || 0;
            if (stake <= 0 || d <= 0) {{
                document.getElementById('convTotalPayout').textContent = '$0.00';
                document.getElementById('convNetProfit').textContent = '$0.00';
                return;
            }}
            const payout = stake * d;
            const profit = stake * (d - 1);
            document.getElementById('convTotalPayout').textContent = `$${{payout.toFixed(2)}}`;
            document.getElementById('convNetProfit').textContent = `${{profit >= 0 ? '+' : ''}}$${{profit.toFixed(2)}}`;
        }}

        // Master Render
        function renderAll() {{
            updateSportPills();
            renderMatchups();
            renderArbs();
            renderProps();
            document.getElementById('headerUpdatedTime').textContent = appData.updated_at || 'Just now';
            document.getElementById('modalMatchupCount').textContent = appData.matchups_count || 0;
            document.getElementById('modalPropsCount').textContent = appData.props_count || 0;
            document.getElementById('modalLastSync').textContent = appData.updated_at || '-';
        }}

        // Data Refresh (Local File & Google Apps Script Support)
        async function refreshData() {{
            const btn = document.getElementById('refreshBtn');
            btn.innerHTML = `<span class="animate-spin">⟳</span><span>Syncing...</span>`;

            const customUrl = localStorage.getItem('oddshub_apps_script_url');
            let success = false;

            if (customUrl) {{
                try {{
                    const res = await fetch(customUrl);
                    const json = await res.json();
                    if (json && json.matchups) {{
                        appData = json;
                        localStorage.setItem('oddshub_cached_data', JSON.stringify(json));
                        success = true;
                    }}
                }} catch (e) {{
                    console.warn('Could not fetch custom Apps Script URL:', e);
                }}
            }}

            if (!success) {{
                try {{
                    const res = await fetch('./mobile_data.json?t=' + Date.now());
                    const json = await res.json();
                    if (json && json.matchups) {{
                        appData = json;
                        localStorage.setItem('oddshub_cached_data', JSON.stringify(json));
                        success = true;
                    }}
                }} catch (e) {{
                    console.log('Using embedded dataset');
                }}
            }}

            btn.innerHTML = `<span>⟳</span><span>Sync</span>`;
            renderAll();
        }}

        // Settings Modal
        function openSettingsModal() {{
            document.getElementById('appsScriptUrlInput').value = localStorage.getItem('oddshub_apps_script_url') || '';
            document.getElementById('settingsModal').classList.remove('hidden');
        }}

        function closeSettingsModal() {{
            document.getElementById('settingsModal').classList.add('hidden');
        }}

        function saveSettings() {{
            const url = document.getElementById('appsScriptUrlInput').value.trim();
            if (url) {{
                localStorage.setItem('oddshub_apps_script_url', url);
            }} else {{
                localStorage.removeItem('oddshub_apps_script_url');
            }}
            closeSettingsModal();
            refreshData();
        }}

        // Dark / Light Theme Toggle
        function toggleTheme() {{
            const body = document.getElementById('appBody');
            const icon = document.getElementById('themeIcon');
            if (body.classList.contains('dark')) {{
                body.classList.remove('dark', 'bg-slate-900', 'text-slate-100');
                body.classList.add('bg-slate-100', 'text-slate-900');
                icon.textContent = '🌙';
            }} else {{
                body.classList.add('dark', 'bg-slate-900', 'text-slate-100');
                body.classList.remove('bg-slate-100', 'text-slate-900');
                icon.textContent = '☀️';
            }}
        }}

        // Initialization
        window.addEventListener('DOMContentLoaded', () => {{
            const cached = localStorage.getItem('oddshub_cached_data');
            let useEmbedded = true;
            if (cached) {{
                try {{
                    const parsed = JSON.parse(cached);
                    const parseTime = (tStr) => {{
                        if (!tStr) return 0;
                        try {{
                            return new Date(tStr.replace(' ET', '').trim()).getTime() || 0;
                        }} catch(e) {{
                            return 0;
                        }}
                    }};
                    const cachedTime = parseTime(parsed.updated_at);
                    const initialTime = parseTime(window.INITIAL_DATA?.updated_at);
                    if (cachedTime > initialTime && parsed.matchups && parsed.matchups.length > 0) {{
                        appData = parsed;
                        useEmbedded = false;
                    }}
                }} catch(e) {{}}
            }}
            if (useEmbedded) {{
                appData = window.INITIAL_DATA || {{ matchups: [], arbs: [], props: [] }};
                try {{
                    localStorage.setItem('oddshub_cached_data', JSON.stringify(appData));
                }} catch(e) {{}}
            }}
            updateNovigModeButtons();
            renderAll();
            calculateArb();
            calculateFreeBet();
            updatePayoutEstimate();
        }});
    </script>
</body>
</html>'''

    out_file = os.path.join(base_dir, "mobile_odds_hub.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    index_file = os.path.join(base_dir, "index.html")
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Successfully built mobile_odds_hub.html and index.html!")

if __name__ == "__main__":
    build_mobile_app_html()
