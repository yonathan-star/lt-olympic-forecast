"""
Generate docs/index.html — interactive GitHub Pages site for the Lithuania LA 2028 forecast.

Features:
  - Funding slider (0.5x–4x): updates all charts live via precomputed JS data
  - Sport checkboxes: toggle sports on/off, expected total updates instantly
  - Per-sport probability bars (historical vs 2028)
  - Monte Carlo medal count distribution
  - Historical performance + 2028 projection
  - Scenario comparison
  - Medal type breakdown (gold/silver/bronze)
  - Peer country comparison
  - Athlete spotlight cards
"""

import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
from model.lithuania_2028 import predict_total_medals, ALL_2028_SPORTS
from simulation.simulator import load_reference_data

ROOT    = os.path.join(os.path.dirname(__file__), "..")
OUTFILE = os.path.join(ROOT, "docs", "index.html")

# ---------------------------------------------------------------------------
# PRECOMPUTE ALL DATA
# ---------------------------------------------------------------------------
FUNDING_LEVELS = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0]

print("Precomputing funding levels...")
precomputed = {}
for fm in FUNDING_LEVELS:
    r = predict_total_medals(funding_multiplier=fm, athletes_sent=50,
                             selected_sports=ALL_2028_SPORTS, n_simulations=10000)
    sim   = np.array(r["sim_distribution"])
    max_k = int(sim.max())
    mc    = {str(k): round(float((sim == k).mean()), 4) for k in range(0, max_k + 2)}
    precomputed[str(fm)] = {
        "expected":  round(r["expected_total"], 3),
        "p10":       round(r["p10"], 1),
        "p90":       round(r["p90"], 1),
        "per_sport": {s: round(d["medal_probability"], 4) for s, d in r["per_sport"].items()},
        "mc":        mc,
    }
    print(f"  {fm}x -> expected {r['expected_total']:.2f}")

# Medal type split (gold/silver/bronze fraction of the medal probability)
MEDAL_TYPE_SPLIT = {
    "Athletics":         {"gold": 0.50, "silver": 0.32, "bronze": 0.18},
    "Rowing":            {"gold": 0.18, "silver": 0.32, "bronze": 0.50},
    "3x3 Basketball":    {"gold": 0.12, "silver": 0.28, "bronze": 0.60},
    "Modern Pentathlon": {"gold": 0.28, "silver": 0.42, "bronze": 0.30},
    "Swimming":          {"gold": 0.22, "silver": 0.38, "bronze": 0.40},
    "Wrestling":         {"gold": 0.10, "silver": 0.40, "bronze": 0.50},
    "Canoe Sprint":      {"gold": 0.10, "silver": 0.30, "bronze": 0.60},
    "Shooting":          {"gold": 0.35, "silver": 0.30, "bronze": 0.35},
    "Weightlifting":     {"gold": 0.12, "silver": 0.35, "bronze": 0.53},
}

# Historical data
df  = load_reference_data()
ltu = df[df["iso3"] == "LTU"].sort_values("year")[["year","gold","silver","bronze","total_medals"]].fillna(0)
ltu = pd.concat([ltu, pd.DataFrame([{"year":2024,"gold":0,"silver":2,"bronze":2,"total_medals":4}])], ignore_index=True)
ltu = ltu.drop_duplicates("year").sort_values("year")

# Per-sport info (baseline)
r_base      = predict_total_medals(funding_multiplier=1.0, athletes_sent=50, selected_sports=ALL_2028_SPORTS)
sports_list = list(r_base["per_sport"].keys())
sports_info = {s: {
    "notes":        d["notes"],
    "hist_rate":    round(d["historical_win_rate"], 3),
    "games_medals": d["games_with_medals"],
    "games_total":  d["games_participated"],
    "medal_years":  d["medal_years"],
    "medal_type":   d["medal_type"],
} for s, d in r_base["per_sport"].items()}

# Peers
peers = [
    {"country":"Lithuania","medals":4, "gold":0,"silver":2,"bronze":2,"pop":2.8},
    {"country":"Estonia",  "medals":3, "gold":1,"silver":1,"bronze":1,"pop":1.3},
    {"country":"Latvia",   "medals":3, "gold":0,"silver":2,"bronze":1,"pop":1.8},
    {"country":"Slovenia", "medals":2, "gold":0,"silver":1,"bronze":1,"pop":2.1},
    {"country":"Slovakia", "medals":2, "gold":0,"silver":1,"bronze":1,"pop":5.4},
    {"country":"Croatia",  "medals":10,"gold":1,"silver":3,"bronze":6,"pop":3.9},
    {"country":"Denmark",  "medals":9, "gold":2,"silver":4,"bronze":3,"pop":5.9},
]

# Baseline reference values
B   = precomputed["1.0"]
exp = B["expected"]
p10 = B["p10"]
p90 = B["p90"]

# Sorted sport list by baseline probability
sports_sorted = sorted(sports_list, key=lambda s: -B["per_sport"][s])
probs_base    = [B["per_sport"][s] for s in sports_sorted]
hrates        = [sports_info[s]["hist_rate"] for s in sports_sorted]
gmed          = [sports_info[s]["games_medals"] for s in sports_sorted]
gtot          = [sports_info[s]["games_total"] for s in sports_sorted]
myears        = [", ".join(str(y) for y in sports_info[s]["medal_years"]) or "none" for s in sports_sorted]
notes_list    = [sports_info[s]["notes"] for s in sports_sorted]

def pill(p):
    if p >= 0.6:  return '<span class="pill high">Strong</span>'
    if p >= 0.25: return '<span class="pill med">Realistic</span>'
    if p >= 0.12: return '<span class="pill low">Possible</span>'
    return '<span class="pill dark">Dark horse</span>'

sport_rows = ""
for i, s in enumerate(sports_sorted):
    note = notes_list[i][:110] + ("..." if len(notes_list[i]) > 110 else "")
    sport_rows += f"""<tr>
      <td><strong>{s}</strong></td>
      <td class="prob-cell" data-sport="{s}"><strong>{probs_base[i]:.0%}</strong></td>
      <td>{gmed[i]}/{gtot[i]} Games ({hrates[i]:.0%})</td>
      <td class="muted small">{myears[i]}</td>
      <td>{pill(probs_base[i])}</td>
      <td class="muted small">{note}</td>
    </tr>"""

# Medal type breakdown data for chart
type_sports = [s for s in sports_sorted if s in MEDAL_TYPE_SPLIT]
gold_probs   = [B["per_sport"][s] * MEDAL_TYPE_SPLIT[s]["gold"]   for s in type_sports]
silver_probs = [B["per_sport"][s] * MEDAL_TYPE_SPLIT[s]["silver"] for s in type_sports]
bronze_probs = [B["per_sport"][s] * MEDAL_TYPE_SPLIT[s]["bronze"] for s in type_sports]

mc_x = [int(k) for k in B["mc"].keys()]
mc_y = list(B["mc"].values())

hist_years  = ltu["year"].tolist()
hist_total  = ltu["total_medals"].astype(int).tolist()
hist_gold   = ltu["gold"].astype(int).tolist()
hist_silver = ltu["silver"].astype(int).tolist()
hist_bronze = ltu["bronze"].astype(int).tolist()

peer_countries = [p["country"] for p in peers]
peer_medals    = [p["medals"] for p in peers]
peer_gold      = [p["gold"] for p in peers]
peer_silver    = [p["silver"] for p in peers]
peer_bronze    = [p["bronze"] for p in peers]
peer_per_m_pop = [round(p["medals"] / p["pop"], 1) for p in peers]

def js(v): return json.dumps(v)

# ---------------------------------------------------------------------------
# BUILD HTML
# ---------------------------------------------------------------------------
PRE_JS = json.dumps(precomputed)
SPORTS_JS = js(sports_sorted)
HRATES_JS = js(hrates)
TYPE_SPORTS_JS = js(type_sports)
GOLD_PROBS_JS = js(gold_probs)
SILVER_PROBS_JS = js(silver_probs)
BRONZE_PROBS_JS = js(bronze_probs)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lithuania LA 2028 Olympic Medal Forecast</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root {{
  --bg:#0f1117; --card:#1a1d27; --card2:#1e2235; --border:#2d3148;
  --text:#e8eaf0; --muted:#8b91a8; --accent:#4f8ef7; --accent2:#7ab3ff;
  --gold:#ffd700; --silver:#c0c0c0; --bronze:#cd7f32;
  --green:#2ca02c; --orange:#ff7f0e; --red:#d62728;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;padding-bottom:80px}}

/* HERO */
.hero{{background:linear-gradient(135deg,#0a1540 0%,#1a2d6e 55%,#0f1117 100%);
  padding:52px 32px 44px;text-align:center;border-bottom:1px solid var(--border)}}
.hero .flag{{font-size:3.2rem;margin-bottom:14px;display:block}}
.hero h1{{font-size:clamp(1.7rem,4.5vw,2.6rem);font-weight:800;margin-bottom:8px;letter-spacing:-0.5px}}
.hero h1 span{{color:var(--accent)}}
.hero .sub{{color:var(--muted);font-size:.95rem;max-width:640px;margin:0 auto 6px;line-height:1.6}}
.hero .datasrc{{font-size:.73rem;color:#636882;margin-top:10px}}

/* METRICS */
.metrics{{display:flex;flex-wrap:wrap;gap:14px;padding:24px 28px;justify-content:center}}
.metric{{background:var(--card);border:1px solid var(--border);border-radius:14px;
  padding:20px 24px;min-width:130px;text-align:center;flex:1;max-width:190px;
  transition:border-color .2s}}
.metric:hover{{border-color:var(--accent)}}
.metric .val{{font-size:2.1rem;font-weight:700;color:var(--accent);line-height:1;
  transition:all .3s}}
.metric .lbl{{font-size:.68rem;color:var(--muted);margin-top:6px;text-transform:uppercase;letter-spacing:.7px}}
.metric .sub{{font-size:.76rem;color:var(--text);margin-top:3px;transition:all .3s}}
#metric-expected .val{{font-size:2.6rem}}

/* SIMULATOR BAR */
.sim-bar{{background:var(--card2);border:1px solid var(--border);border-radius:14px;
  margin:0 28px 20px;padding:20px 28px}}
.sim-bar h3{{font-size:.85rem;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);margin-bottom:16px}}
.sim-controls{{display:flex;flex-wrap:wrap;gap:24px;align-items:flex-start}}
.sim-block{{flex:1;min-width:200px}}
.sim-block label{{font-size:.78rem;color:var(--muted);display:block;margin-bottom:6px}}
.sim-block .val-display{{font-size:1.1rem;font-weight:700;color:var(--accent2);float:right}}
input[type=range]{{width:100%;accent-color:var(--accent);cursor:pointer;height:6px}}
.sport-toggles{{display:flex;flex-wrap:wrap;gap:8px}}
.sport-toggle{{background:var(--card);border:1px solid var(--border);border-radius:20px;
  padding:4px 12px;font-size:.76rem;cursor:pointer;transition:all .2s;user-select:none}}
.sport-toggle.active{{background:#1b3a6b;border-color:var(--accent);color:var(--accent2)}}
.sport-toggle:hover{{border-color:var(--accent)}}

/* GRID */
.grid{{display:grid;gap:18px;padding:0 28px 18px}}
.grid-2{{grid-template-columns:1fr 1fr}}
.grid-3-2{{grid-template-columns:3fr 2fr}}
@media(max-width:860px){{.grid-2,.grid-3-2{{grid-template-columns:1fr}}}}

/* CARD */
.card{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:22px}}
.card h2{{font-size:1rem;font-weight:700;margin-bottom:4px}}
.card .caption{{font-size:.74rem;color:var(--muted);margin-bottom:14px;line-height:1.5}}

/* SECTION */
section{{padding:0 28px 10px}}
section h2{{font-size:1.15rem;font-weight:700;margin:28px 0 14px;
  border-left:3px solid var(--accent);padding-left:12px}}

/* TABLE */
table{{width:100%;border-collapse:collapse;font-size:.82rem}}
th{{text-align:left;padding:8px 10px;color:var(--muted);font-weight:500;
  border-bottom:1px solid var(--border);font-size:.7rem;text-transform:uppercase;letter-spacing:.3px}}
td{{padding:9px 10px;border-bottom:1px solid #222640;vertical-align:top}}
tr:last-child td{{border-bottom:none}}
tr:hover td{{background:#1e2235}}
.muted{{color:var(--muted)}}.small{{font-size:.74rem}}

/* PILLS */
.pill{{display:inline-block;padding:2px 8px;border-radius:20px;font-size:.68rem;font-weight:600}}
.pill.high{{background:#1b3a6b;color:#7ab3ff}}
.pill.med{{background:#1b3d1b;color:#6fcf6f}}
.pill.low{{background:#3d2b0f;color:#ffb347}}
.pill.dark{{background:#2b1b1b;color:#ff8080}}

/* ATHLETE CARDS */
.athlete-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}}
.acard{{background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:18px;transition:border-color .2s}}
.acard:hover{{border-color:var(--accent)}}
.acard .aname{{font-size:.96rem;font-weight:700;margin-bottom:2px}}
.acard .asport{{font-size:.74rem;color:var(--accent);margin-bottom:10px}}
.acard .abadge{{float:right;background:var(--accent);color:#fff;font-weight:700;
  font-size:.86rem;padding:3px 10px;border-radius:8px}}
.acard p{{font-size:.78rem;color:var(--muted);line-height:1.55}}
.acard .astat{{font-size:.74rem;color:var(--text);margin-top:7px;padding-top:7px;
  border-top:1px solid var(--border)}}

/* WARN */
.warn{{background:#2b1f0a;border:1px solid #6b4a12;border-radius:12px;
  padding:14px 18px;font-size:.82rem;color:#ffc97a;margin:0 28px 22px}}

/* FOOTER */
.footer{{text-align:center;color:var(--muted);font-size:.7rem;padding:0 28px;line-height:2}}

/* FADE TRANSITION */
.fade{{transition:opacity .25s}}
</style>
</head>
<body>

<!-- HERO -->
<div class="hero">
  <span class="flag">&#x1F1F1;&#x1F1F9;</span>
  <h1>Lithuania <span>LA 2028</span> Olympic Medal Forecast</h1>
  <p class="sub">Sport-by-sport prediction based on historical Olympic data (1992&ndash;2024) and the known athlete pipeline heading into Los Angeles.</p>
  <p class="datasrc">Base probabilities computed from Olympedia + IOC Paris 2024 data &bull; Bayesian shrinkage on small samples &bull; Known correction: Gudzius Discus Gold Rio 2016</p>
</div>

<!-- LIVE METRICS (update with slider) -->
<div class="metrics">
  <div class="metric" id="metric-expected">
    <div class="val" id="val-expected">{exp}</div>
    <div class="lbl">Expected medals</div>
    <div class="sub" id="sub-expected">P10&ndash;P90: {int(p10)}&ndash;{int(p90)}</div>
  </div>
  <div class="metric">
    <div class="val" id="val-range">{int(p10)}&ndash;{int(p90)}</div>
    <div class="lbl">Likely range</div>
    <div class="sub">P10 &ndash; P90</div>
  </div>
  <div class="metric">
    <div class="val">3.7%</div>
    <div class="lbl">Zero-medal risk</div>
    <div class="sub">baseline funding</div>
  </div>
  <div class="metric">
    <div class="val">82%</div>
    <div class="lbl">Athletics</div>
    <div class="sub">Alekna &mdash; gold favourite</div>
  </div>
  <div class="metric">
    <div class="val">4</div>
    <div class="lbl">Paris 2024 actual</div>
    <div class="sub">2S + 2B (excl. Breaking)</div>
  </div>
</div>

<!-- SIMULATOR CONTROLS -->
<div class="sim-bar">
  <h3>Simulator &mdash; adjust and charts update live</h3>
  <div class="sim-controls">
    <div class="sim-block" style="min-width:280px">
      <label>Funding multiplier <span class="val-display" id="funding-display">1.0x</span></label>
      <input type="range" id="funding-slider" min="0" max="9" value="2" step="1">
      <div style="display:flex;justify-content:space-between;font-size:.68rem;color:var(--muted);margin-top:4px">
        <span>0.5x (cut)</span><span>1.0x (current)</span><span>2.0x</span><span>4.0x</span>
      </div>
    </div>
    <div class="sim-block" style="flex:2;min-width:300px">
      <label>Sports to include (toggle off to exclude from total)</label>
      <div class="sport-toggles" id="sport-toggles"></div>
    </div>
  </div>
</div>

<!-- CHARTS ROW 1 -->
<div class="grid grid-3-2">
  <div class="card">
    <h2>Per-Sport Medal Probability</h2>
    <p class="caption">Grey = historical win rate from data &bull; Coloured = 2028 forecast &bull; Updates with slider</p>
    <div id="chart-sports"></div>
  </div>
  <div class="card">
    <h2>Medal Count Distribution</h2>
    <p class="caption">10,000 Monte Carlo simulations at current funding level</p>
    <div id="chart-mc"></div>
  </div>
</div>

<!-- CHARTS ROW 2 -->
<div class="grid grid-2">
  <div class="card">
    <h2>Historical Performance 1992&ndash;2024</h2>
    <p class="caption">Red star = 2028 forecast with P10&ndash;P90 interval &bull; Updates with slider</p>
    <div id="chart-hist"></div>
  </div>
  <div class="card">
    <h2>Medal Type Breakdown</h2>
    <p class="caption">Estimated gold / silver / bronze probability per sport at current funding</p>
    <div id="chart-type"></div>
  </div>
</div>

<!-- CHARTS ROW 3 -->
<div class="grid grid-2">
  <div class="card">
    <h2>Scenario Comparison</h2>
    <p class="caption">Four preset scenarios vs current slider value</p>
    <div id="chart-scen"></div>
  </div>
  <div class="card">
    <h2>Peer Country Comparison &mdash; Paris 2024</h2>
    <p class="caption">Lithuania vs similar small European nations</p>
    <div id="chart-peers"></div>
  </div>
</div>

<!-- SPORT DETAIL TABLE -->
<section>
  <h2>Per-Sport Detail &amp; Data Sources</h2>
  <div class="card">
    <table>
      <tr><th>Sport</th><th>2028 Prob</th><th>Historical</th><th>Medal years</th><th>Outlook</th><th>Notes</th></tr>
      {sport_rows}
    </table>
  </div>
</section>

<!-- ATHLETES -->
<section>
  <h2>Key Athletes &mdash; LA 2028 Contenders</h2>
  <div class="athlete-grid">
    <div class="acard">
      <span class="abadge">82%</span>
      <div class="aname">Mykolas Alekna</div>
      <div class="asport">Athletics &mdash; Discus Throw</div>
      <p>Top global gold favorite. Olympic silver Paris 2024 aged 20. 74.35m world lead 2024. Father Virgilijus won discus gold 2000 &amp; 2004. Will be 24 in LA &mdash; absolute prime.</p>
      <div class="astat">Paris 2024: Silver &bull; 74.35m WL &bull; Age in 2028: 24</div>
    </div>
    <div class="acard">
      <span class="abadge">32%</span>
      <div class="aname">Viktorija Senkute</div>
      <div class="asport">Rowing &mdash; Women's Single Sculls</div>
      <p>Olympic bronze Paris 2024. Will be 27 in 2028 &mdash; peak rowing age. Consistent World Cup top-5 competitor with strong upside.</p>
      <div class="astat">Paris 2024: Bronze &bull; Age in 2028: 27</div>
    </div>
    <div class="acard">
      <span class="abadge">34%</span>
      <div class="aname">Lithuania 3x3 Basketball</div>
      <div class="asport">3x3 Basketball &mdash; Men's Team</div>
      <p>Olympic bronze 2024. Core roster averages ~27 in 2028. Basketball is Lithuania's structural sport &mdash; FIBA 3x3 consistent top-10 globally. LA outdoor courts suit physical play.</p>
      <div class="astat">Paris 2024: Bronze &bull; FIBA 3x3 World Ranking top-10</div>
    </div>
    <div class="acard">
      <span class="abadge">19%</span>
      <div class="aname">Ruta Meilutyte &amp; Danas Rapsys</div>
      <div class="asport">Swimming</div>
      <p>Meilutyte: WR holder 100m breaststroke, Olympic gold 2012, still active at 31 in 2028. Rapsys: 3 Olympic A-finals, European champion. Two contenders in one sport.</p>
      <div class="astat">Meilutyte age: 31 &bull; Rapsys age: 33 &bull; Two podium threats</div>
    </div>
    <div class="acard">
      <span class="abadge">22%</span>
      <div class="aname">Gintare Venckauskaite</div>
      <div class="asport">Modern Pentathlon</div>
      <p>Next-generation pentathlete following Laura Asadauskaite (5 Olympic medals, 2012 gold). Venckauskaite is the senior pipeline. Asadauskaite will be 44 in 2028 &mdash; certain to retire.</p>
      <div class="astat">Rising senior competitor &bull; Asadauskaite: 44 in 2028 (retired)</div>
    </div>
  </div>
</section>

<div style="height:20px"></div>
<div class="warn">
  <strong>Breaking is NOT on the LA 2028 program.</strong>
  NICKA (Dominyka Banevic) won Silver at Paris 2024, but the IOC removed Breaking from the 2028 Games.
  Lithuania's 2028 forecast is calculated without this sport. &nbsp;<em>Source: IOC Program Commission, 2023.</em>
</div>

<div class="footer">
  <strong>Data sources:</strong>
  Olympedia historical results 1992&ndash;2020 (Kaggle) &bull;
  Paris 2024 official results (IOC) &bull;
  World Athletics, FINA, FIBA 3x3, ICF, UIPM, ISSF rankings 2024 &bull;
  IOC Program Commission 2023 (Breaking removal) &bull;
  Known correction: Gudzius Discus Gold Rio 2016 (absent from source dataset) &bull;
  Bayesian shrinkage applied to sports with &lt;5 Games of data &bull;
  Macro ensemble: XGBoost + RF trained on 137 countries 1960&ndash;2024
  <br>
  Generated 2026-03-25 &bull;
  <a href="https://github.com/yonathan-star/lt-olympic-forecast" style="color:var(--accent)">GitHub</a>
</div>

<script>
// =========================================================
// PRECOMPUTED DATA
// =========================================================
const PRE = {PRE_JS};
const FUNDING_LEVELS = {js(FUNDING_LEVELS)};
const SPORTS = {SPORTS_JS};
const HRATES = {HRATES_JS};
const TYPE_SPORTS = {TYPE_SPORTS_JS};
const GOLD_BASE   = {GOLD_PROBS_JS};
const SILVER_BASE = {SILVER_PROBS_JS};
const BRONZE_BASE = {BRONZE_PROBS_JS};

const HIST_YEARS  = {js(hist_years)};
const HIST_TOTAL  = {js(hist_total)};
const HIST_GOLD   = {js(hist_gold)};
const HIST_SILVER = {js(hist_silver)};
const HIST_BRONZE = {js(hist_bronze)};

const PEER_COUNTRIES = {js(peer_countries)};
const PEER_MEDALS    = {js(peer_medals)};
const PEER_GOLD      = {js(peer_gold)};
const PEER_SILVER    = {js(peer_silver)};
const PEER_BRONZE    = {js(peer_bronze)};
const PEER_PER_POP   = {js(peer_per_m_pop)};

// =========================================================
// STATE
// =========================================================
let currentFundingIdx = 2; // 1.0x
let selectedSports = new Set(SPORTS);

const DARK = {{
  paper_bgcolor:'#1a1d27', plot_bgcolor:'#1a1d27',
  font:{{color:'#e8eaf0', size:11}},
  xaxis:{{gridcolor:'#2d3148', zerolinecolor:'#2d3148'}},
  yaxis:{{gridcolor:'#2d3148', zerolinecolor:'#2d3148'}}
}};
const CFG = {{responsive:true, displayModeBar:false}};

// =========================================================
// HELPERS
// =========================================================
function getPreData() {{
  return PRE[String(FUNDING_LEVELS[currentFundingIdx])];
}}

function getActiveSportProbs() {{
  const d = getPreData();
  return SPORTS.map(s => selectedSports.has(s) ? (d.per_sport[s] || 0) : 0);
}}

function getExpected() {{
  const probs = getActiveSportProbs();
  return probs.reduce((a,b)=>a+b, 0);
}}

// Approximate MC dist from sum of independent Bernoullis
function approxMCDist(probs) {{
  let dist = [1.0];
  for (const p of probs) {{
    const newDist = new Array(dist.length + 1).fill(0);
    for (let k = 0; k < dist.length; k++) {{
      newDist[k]   += dist[k] * (1-p);
      newDist[k+1] += dist[k] * p;
    }}
    dist = newDist;
  }}
  return dist;
}}

// =========================================================
// SPORT TOGGLES
// =========================================================
function buildToggles() {{
  const container = document.getElementById('sport-toggles');
  SPORTS.forEach(s => {{
    const btn = document.createElement('div');
    btn.className = 'sport-toggle active';
    btn.textContent = s;
    btn.dataset.sport = s;
    btn.addEventListener('click', () => {{
      if (selectedSports.has(s)) {{
        if (selectedSports.size > 1) {{ // keep at least 1
          selectedSports.delete(s);
          btn.classList.remove('active');
        }}
      }} else {{
        selectedSports.add(s);
        btn.classList.add('active');
      }}
      updateAll();
    }});
    container.appendChild(btn);
  }});
}}

// =========================================================
// UPDATE METRICS
// =========================================================
function updateMetrics() {{
  const d = getPreData();
  const expected = getExpected().toFixed(2);
  // Rough range from precomputed (scale by ratio of active/all)
  const ratio = getExpected() / d.expected;
  const p10 = Math.max(0, Math.round(d.p10 * ratio));
  const p90 = Math.round(d.p90 * ratio);
  document.getElementById('val-expected').textContent = expected;
  document.getElementById('sub-expected').textContent = `P10\u2013P90: ${{p10}}\u2013${{p90}}`;
  document.getElementById('val-range').textContent = `${{p10}}\u2013${{p90}}`;
}}

// =========================================================
// CHART: PER-SPORT BARS
// =========================================================
let sportsChartInit = false;
function updateSportsChart() {{
  const d = getPreData();
  const probs = SPORTS.map(s => selectedSports.has(s) ? (d.per_sport[s]||0) : 0);
  const colors = probs.map((p,i) => {{
    if (!selectedSports.has(SPORTS[i])) return 'rgba(100,100,100,0.2)';
    return p>=0.6?'#4f8ef7': p>=0.25?'#2ca02c': p>=0.12?'#ff7f0e':'#d62728';
  }});

  const traces = [
    {{x:HRATES, y:SPORTS, type:'bar', orientation:'h', name:'Historical win rate',
      marker:{{color:'rgba(150,150,150,0.2)'}}, width:0.5}},
    {{x:probs, y:SPORTS, type:'bar', orientation:'h', name:'2028 probability',
      marker:{{color:colors}}, width:0.32,
      text:probs.map(p=>p>0.01?(p*100).toFixed(0)+'%':''), textposition:'outside'}}
  ];
  const layout = {{...DARK, barmode:'overlay',
    xaxis:{{...DARK.xaxis, title:'Medal probability', tickformat:'.0%', range:[0,1.1]}},
    yaxis:{{...DARK.yaxis, autorange:'reversed'}},
    legend:{{orientation:'h', yanchor:'bottom', y:1.02, bgcolor:'rgba(0,0,0,0)'}},
    height:320, margin:{{t:10,b:40,l:10,r:72}}
  }};
  if (!sportsChartInit) {{
    Plotly.newPlot('chart-sports', traces, layout, CFG);
    sportsChartInit = true;
  }} else {{
    Plotly.react('chart-sports', traces, layout);
  }}
  // Update table cells
  document.querySelectorAll('.prob-cell').forEach(cell => {{
    const s = cell.dataset.sport;
    const p = d.per_sport[s]||0;
    cell.innerHTML = `<strong>${{(p*100).toFixed(0)}}%</strong>`;
    cell.style.opacity = selectedSports.has(s) ? '1' : '0.3';
  }});
}}

// =========================================================
// CHART: MONTE CARLO DISTRIBUTION
// =========================================================
let mcChartInit = false;
function updateMCChart() {{
  const probs = getActiveSportProbs().filter(p=>p>0);
  const dist  = approxMCDist(probs);
  const mcX   = dist.map((_,i)=>i);
  const mcY   = dist;
  const exp   = getExpected();

  const trace = {{x:mcX, y:mcY, type:'bar', marker:{{color:'#4f8ef7',opacity:0.82}},
    text:mcY.map(v=>v>0.02?(v*100).toFixed(0)+'%':''), textposition:'outside'}};
  const layout = {{...DARK,
    xaxis:{{...DARK.xaxis, title:'Total medals', dtick:1}},
    yaxis:{{...DARK.yaxis, title:'Probability', tickformat:'.0%'}},
    shapes:[{{type:'line',x0:exp,x1:exp,y0:0,y1:1,yref:'paper',
              line:{{color:'#ff4444',dash:'dash',width:2}}}}],
    annotations:[{{x:exp,y:0.97,yref:'paper',text:`Mean ${{exp.toFixed(1)}}`,
                   showarrow:false,font:{{color:'#ff4444',size:11}}}}],
    height:300, margin:{{t:20,b:40,l:50,r:20}}
  }};
  if (!mcChartInit) {{
    Plotly.newPlot('chart-mc', [trace], layout, CFG);
    mcChartInit = true;
  }} else {{
    Plotly.react('chart-mc', [trace], layout);
  }}
}}

// =========================================================
// CHART: HISTORICAL
// =========================================================
function initHistChart() {{
  const d = getPreData();
  const exp = getExpected();
  const ratio = exp / d.expected;
  const p10 = Math.max(0, d.p10 * ratio);
  const p90 = d.p90 * ratio;

  Plotly.newPlot('chart-hist', [
    {{x:HIST_YEARS, y:HIST_TOTAL, mode:'lines+markers', name:'Total',
      line:{{color:'#4f8ef7',width:3}}, marker:{{size:7}}}},
    {{x:HIST_YEARS, y:HIST_GOLD, mode:'lines+markers', name:'Gold',
      line:{{color:'#ffd700',width:2}}}},
    {{x:HIST_YEARS, y:HIST_SILVER, mode:'lines+markers', name:'Silver',
      line:{{color:'#c0c0c0',width:2}}}},
    {{x:HIST_YEARS, y:HIST_BRONZE, mode:'lines+markers', name:'Bronze',
      line:{{color:'#cd7f32',width:2}}}},
    {{x:[2028], y:[exp], mode:'markers', name:'2028 Forecast',
      marker:{{size:16,color:'#ff4444',symbol:'star'}},
      error_y:{{type:'data',array:[p90-exp],arrayminus:[exp-p10],visible:true,color:'#ff4444'}}}}
  ], {{...DARK,
    xaxis:{{...DARK.xaxis,title:'Year'}},
    yaxis:{{...DARK.yaxis,title:'Medals',rangemode:'tozero'}},
    legend:{{orientation:'h',yanchor:'bottom',y:1.02,bgcolor:'rgba(0,0,0,0)'}},
    height:290,margin:{{t:10,b:40,l:40,r:20}}
  }}, CFG);
}}
function updateHistChart() {{
  const d = getPreData();
  const exp = getExpected();
  const ratio = exp / d.expected;
  const p10 = Math.max(0, d.p10 * ratio);
  const p90 = d.p90 * ratio;
  Plotly.restyle('chart-hist', {{x:[[2028]], y:[[exp]],
    'error_y.array':[[p90-exp]], 'error_y.arrayminus':[[exp-p10]]}}, [4]);
  Plotly.relayout('chart-hist', {{
    shapes:[],
    annotations:[]
  }});
}}

// =========================================================
// CHART: MEDAL TYPE BREAKDOWN
// =========================================================
function initTypeChart() {{
  const d = getPreData();
  const golds   = TYPE_SPORTS.map((s,i) => selectedSports.has(s) ? (d.per_sport[s]||0)*GOLD_BASE[i]/(GOLD_BASE[i]+SILVER_BASE[i]+BRONZE_BASE[i]) : 0);
  // Simpler: just scale base split by current prob
  const gP = TYPE_SPORTS.map((s,i) => {{
    const p = selectedSports.has(s) ? (d.per_sport[s]||0) : 0;
    const split = {{gold:GOLD_BASE[i],silver:SILVER_BASE[i],bronze:BRONZE_BASE[i]}};
    const tot = split.gold+split.silver+split.bronze;
    return [p*split.gold/tot, p*split.silver/tot, p*split.bronze/tot];
  }});
  Plotly.newPlot('chart-type', [
    {{x:gP.map(x=>x[0]), y:TYPE_SPORTS, type:'bar', orientation:'h', name:'Gold',
      marker:{{color:'#ffd700'}}, text:gP.map(x=>x[0]>0.02?(x[0]*100).toFixed(0)+'%':''), textposition:'outside'}},
    {{x:gP.map(x=>x[1]), y:TYPE_SPORTS, type:'bar', orientation:'h', name:'Silver',
      marker:{{color:'#c0c0c0'}}}},
    {{x:gP.map(x=>x[2]), y:TYPE_SPORTS, type:'bar', orientation:'h', name:'Bronze',
      marker:{{color:'#cd7f32'}}}}
  ], {{...DARK, barmode:'stack',
    xaxis:{{...DARK.xaxis,title:'Medal probability',tickformat:'.0%',range:[0,0.95]}},
    yaxis:{{...DARK.yaxis,autorange:'reversed'}},
    legend:{{orientation:'h',yanchor:'bottom',y:1.02,bgcolor:'rgba(0,0,0,0)'}},
    height:290, margin:{{t:10,b:40,l:10,r:80}}
  }}, CFG);
}}
function updateTypeChart() {{
  const d = getPreData();
  const gP = TYPE_SPORTS.map((s,i) => {{
    const p = selectedSports.has(s) ? (d.per_sport[s]||0) : 0;
    const tot = GOLD_BASE[i]+SILVER_BASE[i]+BRONZE_BASE[i];
    return [p*GOLD_BASE[i]/tot, p*SILVER_BASE[i]/tot, p*BRONZE_BASE[i]/tot];
  }});
  Plotly.restyle('chart-type', {{x:[gP.map(x=>x[0])]}}, [0]);
  Plotly.restyle('chart-type', {{x:[gP.map(x=>x[1])]}}, [1]);
  Plotly.restyle('chart-type', {{x:[gP.map(x=>x[2])]}}, [2]);
}}

// =========================================================
// CHART: SCENARIOS
// =========================================================
function initScenChart() {{
  const scens = [
    ['Baseline\\n(1x)',  PRE['1.0']],
    ['2x Funding',       PRE['2.0']],
    ['Current',         getPreData()],
    ['3x Funding',      PRE['3.0']],
  ];
  Plotly.newPlot('chart-scen',
    scens.map(([lbl,d],i) => ({{
      x:[lbl], y:[d.expected], type:'bar',
      name:lbl, marker:{{color:['#4f8ef7','#2ca02c','#EF553B','#AB63FA'][i]}},
      text:[d.expected.toFixed(1)], textposition:'outside',
      error_y:{{type:'data',array:[d.p90-d.expected],arrayminus:[d.expected-d.p10],visible:true}}
    }})),
  {{...DARK, barmode:'group', showlegend:false,
    yaxis:{{...DARK.yaxis,title:'Expected medals',rangemode:'tozero'}},
    height:280, margin:{{t:20,b:60,l:50,r:20}}
  }}, CFG);
}}
function updateScenChart() {{
  const d = getPreData();
  Plotly.restyle('chart-scen', {{y:[[d.expected]],'error_y.array':[[d.p90-d.expected]],'error_y.arrayminus':[[d.expected-d.p10]]}}, [2]);
}}

// =========================================================
// CHART: PEERS (static, init once)
// =========================================================
function initPeersChart() {{
  Plotly.newPlot('chart-peers', [
    {{x:PEER_COUNTRIES, y:PEER_GOLD,   type:'bar', name:'Gold',   marker:{{color:'#ffd700'}}}},
    {{x:PEER_COUNTRIES, y:PEER_SILVER, type:'bar', name:'Silver', marker:{{color:'#c0c0c0'}}}},
    {{x:PEER_COUNTRIES, y:PEER_BRONZE, type:'bar', name:'Bronze', marker:{{color:'#cd7f32'}}}},
  ], {{...DARK, barmode:'stack',
    yaxis:{{...DARK.yaxis, title:'Medals (Paris 2024)'}},
    legend:{{orientation:'h',yanchor:'bottom',y:1.02,bgcolor:'rgba(0,0,0,0)'}},
    height:280, margin:{{t:10,b:50,l:50,r:20}}
  }}, CFG);
}}

// =========================================================
// MAIN UPDATE
// =========================================================
function updateAll() {{
  updateMetrics();
  updateSportsChart();
  updateMCChart();
  updateHistChart();
  updateTypeChart();
  updateScenChart();
}}

// =========================================================
// FUNDING SLIDER
// =========================================================
const slider = document.getElementById('funding-slider');
const fundingDisplay = document.getElementById('funding-display');
slider.addEventListener('input', () => {{
  currentFundingIdx = parseInt(slider.value);
  fundingDisplay.textContent = FUNDING_LEVELS[currentFundingIdx].toFixed(2) + 'x';
  updateAll();
}});

// =========================================================
// INIT
// =========================================================
buildToggles();
initHistChart();
initTypeChart();
initScenChart();
initPeersChart();
updateAll();
</script>
</body>
</html>"""

os.makedirs(os.path.dirname(OUTFILE), exist_ok=True)
with open(OUTFILE, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Written: {OUTFILE}  ({len(html):,} bytes)")
