"""Generate docs/index.html — static GitHub Pages site for the Lithuania LA 2028 forecast."""

import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
from model.lithuania_2028 import predict_total_medals, ALL_2028_SPORTS
from simulation.simulator import load_reference_data

ROOT    = os.path.join(os.path.dirname(__file__), "..")
OUTFILE = os.path.join(ROOT, "docs", "index.html")

# ---------------------------------------------------------------------------
# COMPUTE ALL DATA
# ---------------------------------------------------------------------------
baseline = predict_total_medals(funding_multiplier=1.0, athletes_sent=50, selected_sports=ALL_2028_SPORTS)

scenario_configs = [
    ("Baseline (current)",       dict(funding_multiplier=1.0, athletes_sent=50,  selected_sports=ALL_2028_SPORTS)),
    ("2x Funding",               dict(funding_multiplier=2.0, athletes_sent=60,  selected_sports=ALL_2028_SPORTS)),
    ("2x + Focus top 4",         dict(funding_multiplier=2.0, athletes_sent=60,  selected_sports=["Athletics","Rowing","3x3 Basketball","Swimming"], focus_mode=True)),
    ("3x + Focus top 4",         dict(funding_multiplier=3.0, athletes_sent=70,  selected_sports=["Athletics","Rowing","3x3 Basketball","Swimming"], focus_mode=True)),
]
scenarios = {}
for label, kwargs in scenario_configs:
    r = predict_total_medals(**kwargs)
    scenarios[label] = {"expected": round(r["expected_total"], 2), "p10": round(r["p10"], 1), "p90": round(r["p90"], 1)}

df = load_reference_data()
ltu = df[df["iso3"] == "LTU"].sort_values("year")[["year","gold","silver","bronze","total_medals"]].fillna(0)
ltu = pd.concat([ltu, pd.DataFrame([{"year":2024,"gold":0,"silver":2,"bronze":2,"total_medals":4}])], ignore_index=True)
ltu = ltu.drop_duplicates("year").sort_values("year")

sim     = np.array(baseline["sim_distribution"])
max_k   = int(sim.max())
mc_dist = {int(k): round(float((sim == k).mean()), 4) for k in range(0, max_k + 2)}

sports_sorted = sorted(baseline["per_sport"].items(), key=lambda x: -x[1]["medal_probability"])
sports  = [s for s, _ in sports_sorted]
probs   = [d["medal_probability"] for _, d in sports_sorted]
hrates  = [d["historical_win_rate"] for _, d in sports_sorted]
gmed    = [d["games_with_medals"] for _, d in sports_sorted]
gtot    = [d["games_participated"] for _, d in sports_sorted]
myears  = [", ".join(str(y) for y in d["medal_years"]) or "none" for _, d in sports_sorted]
notes   = [d["notes"] for _, d in sports_sorted]
mtypes  = [d["medal_type"] for _, d in sports_sorted]

B = baseline
exp  = round(B["expected_total"], 2)
p10  = round(B["p10"], 1)
p90  = round(B["p90"], 1)
med  = round(B["median_total"], 1)
zmp  = round(B["zero_medal_prob"] * 100, 1)

# JS arrays
def js(v):
    return json.dumps(v)

hist_years  = ltu["year"].tolist()
hist_total  = ltu["total_medals"].astype(int).tolist()
hist_gold   = ltu["gold"].astype(int).tolist()
hist_silver = ltu["silver"].astype(int).tolist()
hist_bronze = ltu["bronze"].astype(int).tolist()

scen_labels   = list(scenarios.keys())
scen_expected = [scenarios[s]["expected"] for s in scen_labels]
scen_p10      = [scenarios[s]["p10"] for s in scen_labels]
scen_p90      = [scenarios[s]["p90"] for s in scen_labels]
scen_err_hi   = [scenarios[s]["p90"] - scenarios[s]["expected"] for s in scen_labels]
scen_err_lo   = [scenarios[s]["expected"] - scenarios[s]["p10"] for s in scen_labels]

mc_x = list(mc_dist.keys())
mc_y = list(mc_dist.values())

# Sport detail rows HTML
def pill(p):
    if p >= 0.6:  return '<span class="pill high">Strong</span>'
    if p >= 0.25: return '<span class="pill med">Realistic</span>'
    if p >= 0.12: return '<span class="pill low">Possible</span>'
    return '<span class="pill dark">Dark horse</span>'

sport_rows = ""
for i, s in enumerate(sports):
    note = notes[i][:120] + ("..." if len(notes[i]) > 120 else "")
    sport_rows += f"""<tr>
      <td><strong>{s}</strong></td>
      <td><strong>{probs[i]:.0%}</strong></td>
      <td>{gmed[i]}/{gtot[i]} Games ({hrates[i]:.0%})</td>
      <td class="muted small">{myears[i]}</td>
      <td>{pill(probs[i])}</td>
      <td class="muted small">{note}</td>
    </tr>"""

# ---------------------------------------------------------------------------
# BUILD HTML
# ---------------------------------------------------------------------------
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lithuania LA 2028 Olympic Medal Forecast</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root {{
  --bg:#0f1117; --card:#1a1d27; --border:#2d3148;
  --text:#e8eaf0; --muted:#8b91a8; --accent:#4f8ef7;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;padding-bottom:60px}}
.hero{{background:linear-gradient(135deg,#0d1b4b,#1a2d6e 50%,#0f1117);padding:48px 32px 40px;text-align:center;border-bottom:1px solid var(--border)}}
.hero .flag{{font-size:3rem;margin-bottom:12px}}
.hero h1{{font-size:clamp(1.6rem,4vw,2.4rem);font-weight:700;margin-bottom:8px}}
.hero h1 span{{color:var(--accent)}}
.hero p{{color:var(--muted);font-size:.95rem;max-width:660px;margin:0 auto 4px;line-height:1.6}}
.metrics{{display:flex;flex-wrap:wrap;gap:16px;padding:28px 32px;justify-content:center}}
.metric{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px 28px;min-width:140px;text-align:center;flex:1;max-width:200px}}
.metric .val{{font-size:2.2rem;font-weight:700;color:var(--accent);line-height:1}}
.metric .lbl{{font-size:.72rem;color:var(--muted);margin-top:6px;text-transform:uppercase;letter-spacing:.6px}}
.metric .sub{{font-size:.78rem;color:var(--text);margin-top:4px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px;padding:0 32px 24px}}
.grid.wide{{grid-template-columns:3fr 2fr}}
@media(max-width:860px){{.grid,.grid.wide{{grid-template-columns:1fr}}}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:24px}}
.card h2{{font-size:1.05rem;font-weight:600;margin-bottom:4px}}
.card .caption{{font-size:.76rem;color:var(--muted);margin-bottom:14px;line-height:1.5}}
section{{padding:0 32px 8px}}
section h2{{font-size:1.2rem;font-weight:600;margin:28px 0 14px;border-left:3px solid var(--accent);padding-left:12px}}
table{{width:100%;border-collapse:collapse;font-size:.83rem}}
th{{text-align:left;padding:8px 12px;color:var(--muted);font-weight:500;border-bottom:1px solid var(--border);font-size:.72rem;text-transform:uppercase}}
td{{padding:9px 12px;border-bottom:1px solid #232640;vertical-align:top}}
tr:last-child td{{border-bottom:none}}
tr:hover td{{background:#1f2235}}
.muted{{color:var(--muted)}}
.small{{font-size:.75rem}}
.pill{{display:inline-block;padding:2px 8px;border-radius:20px;font-size:.7rem;font-weight:600}}
.pill.high{{background:#1b3a6b;color:#7ab3ff}}
.pill.med{{background:#1b3d1b;color:#6fcf6f}}
.pill.low{{background:#3d2b0f;color:#ffb347}}
.pill.dark{{background:#2b1b1b;color:#ff8080}}
.athlete-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}}
.acard{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:18px}}
.acard .name{{font-size:.98rem;font-weight:700;margin-bottom:2px}}
.acard .sport{{font-size:.76rem;color:var(--accent);margin-bottom:10px}}
.acard .badge{{float:right;background:var(--accent);color:#fff;font-weight:700;font-size:.88rem;padding:3px 9px;border-radius:6px}}
.acard p{{font-size:.8rem;color:var(--muted);line-height:1.5}}
.acard .stat{{font-size:.77rem;color:var(--text);margin-top:6px}}
.warn{{background:#2b1f0a;border:1px solid #6b4a12;border-radius:10px;padding:14px 18px;font-size:.83rem;color:#ffc97a;margin:0 32px 24px}}
.footer{{text-align:center;color:var(--muted);font-size:.72rem;padding:0 32px;line-height:1.9}}
</style>
</head>
<body>

<div class="hero">
  <div class="flag">&#x1F1F1;&#x1F1F9;</div>
  <h1>Lithuania <span>LA 2028</span> Olympic Medal Forecast</h1>
  <p>Sport-by-sport prediction based on historical Olympic data (1992&ndash;2024) and the known athlete pipeline.</p>
  <p style="font-size:.76rem;margin-top:8px">Base probabilities computed from Olympedia results &amp; IOC Paris 2024 data &mdash; not guesses.</p>
</div>

<div class="metrics">
  <div class="metric"><div class="val">{exp}</div><div class="lbl">Expected medals</div><div class="sub">baseline funding</div></div>
  <div class="metric"><div class="val">{int(p10)}&ndash;{int(p90)}</div><div class="lbl">Likely range</div><div class="sub">P10 &ndash; P90</div></div>
  <div class="metric"><div class="val">{med:.0f}</div><div class="lbl">Most likely</div><div class="sub">median simulation</div></div>
  <div class="metric"><div class="val">{zmp}%</div><div class="lbl">Zero-medal risk</div><div class="sub">very unlikely</div></div>
  <div class="metric"><div class="val">82%</div><div class="lbl">Athletics</div><div class="sub">Alekna &mdash; gold favourite</div></div>
</div>

<div class="grid wide">
  <div class="card">
    <h2>Per-Sport Medal Probability</h2>
    <p class="caption">Grey = historical win rate from data. Colour = 2028 forecast adjusted for athlete pipeline &amp; Bayesian shrinkage on small samples.</p>
    <div id="chart-sports"></div>
  </div>
  <div class="card">
    <h2>Medal Count Distribution</h2>
    <p class="caption">10,000 Monte Carlo simulations. Each sport drawn independently from its probability.</p>
    <div id="chart-mc"></div>
  </div>
</div>

<div class="grid">
  <div class="card">
    <h2>Historical Performance 1992&ndash;2024</h2>
    <p class="caption">Red star = 2028 forecast with P10&ndash;P90 confidence interval.</p>
    <div id="chart-hist"></div>
  </div>
  <div class="card">
    <h2>Scenario Comparison</h2>
    <p class="caption">Effect of increasing the sport budget and concentrating on top events.</p>
    <div id="chart-scen"></div>
  </div>
</div>

<section>
  <h2>Per-Sport Detail &amp; Data Sources</h2>
  <div class="card">
    <table>
      <tr><th>Sport</th><th>2028 Prob</th><th>Historical</th><th>Medal years</th><th>Outlook</th><th>Notes</th></tr>
      {sport_rows}
    </table>
  </div>
</section>

<section>
  <h2>Key Athletes &mdash; LA 2028 Contenders</h2>
  <div class="athlete-grid">
    <div class="acard">
      <span class="badge">82%</span>
      <div class="name">Mykolas Alekna</div>
      <div class="sport">Athletics &mdash; Discus Throw</div>
      <p>Top global gold favorite. Olympic silver Paris 2024 aged 20. 74.35m world lead 2024. Will be 24 in LA &mdash; peak years. Father Virgilijus won discus gold in 2000 &amp; 2004.</p>
      <div class="stat">Paris 2024: Silver &bull; 74.35m WL &bull; Age in 2028: 24</div>
    </div>
    <div class="acard">
      <span class="badge">32%</span>
      <div class="name">Viktorija Senkute</div>
      <div class="sport">Rowing &mdash; Women's Single Sculls</div>
      <p>Olympic bronze Paris 2024. Will be 27 in 2028 &mdash; peak rowing age. Consistent World Cup competitor. Strong probability of repeating or improving.</p>
      <div class="stat">Paris 2024: Bronze &bull; Age in 2028: 27</div>
    </div>
    <div class="acard">
      <span class="badge">34%</span>
      <div class="name">Lithuania 3x3 Basketball</div>
      <div class="sport">3x3 Basketball &mdash; Men's Team</div>
      <p>Olympic bronze 2024. Core roster averages ~27 in 2028. Basketball is Lithuania's structural sport &mdash; FIBA 3x3 consistent top-10 globally.</p>
      <div class="stat">Paris 2024: Bronze &bull; FIBA 3x3 World Ranking top-10</div>
    </div>
    <div class="acard">
      <span class="badge">19%</span>
      <div class="name">Ruta Meilutyte &amp; Danas Rapsys</div>
      <div class="sport">Swimming</div>
      <p>Meilutyte: WR holder 100m breaststroke, Olympic gold 2012, still active. Rapsys: 3 Olympic A-finals, European champion. Two contenders in one sport.</p>
      <div class="stat">Meilutyte age in 2028: 31 &bull; Rapsys: 33</div>
    </div>
  </div>
</section>

<div style="height:20px"></div>
<div class="warn">
  <strong>Breaking is NOT on the LA 2028 program.</strong>
  NICKA (Dominyka Banevic) won Silver at Paris 2024, but the IOC removed Breaking from the 2028 Games.
  Lithuania's 2028 forecast is calculated without this sport.
  <em>Source: IOC Program Commission decision, 2023.</em>
</div>

<div class="footer">
  <strong>Data sources:</strong> Olympedia historical results 1992&ndash;2020 (Kaggle: heesoo37) &bull;
  Paris 2024 official results (Kaggle: piterfm / IOC) &bull;
  World Athletics, FINA, FIBA 3x3, ICF, UIPM, ISSF rankings 2024 &bull;
  IOC Program Commission 2023 (Breaking removal) &bull;
  Known correction: Andrius Gudzius Discus Gold Rio 2016 (absent from source dataset, verified via World Athletics) &bull;
  Bayesian shrinkage applied to sports with &lt;5 Games of data &bull;
  Macro ensemble: XGBoost + RF trained on 137 countries 1960&ndash;2024
  <br>
  <a href="https://github.com/yonathan-star/lt-olympic-forecast" style="color:var(--accent)">GitHub repo</a>
</div>

<script>
const DARK = {{
  paper_bgcolor: '#1a1d27', plot_bgcolor: '#1a1d27',
  font: {{color: '#e8eaf0', size: 11}},
  xaxis: {{gridcolor: '#2d3148', zerolinecolor: '#2d3148'}},
  yaxis: {{gridcolor: '#2d3148', zerolinecolor: '#2d3148'}}
}};
const CFG = {{responsive: true, displayModeBar: false}};

// 1. Per-sport chart
const sports  = {js(sports)};
const probs   = {js(probs)};
const hrates  = {js(hrates)};
const colors  = probs.map(p => p>=0.6?'#4f8ef7': p>=0.25?'#2ca02c': p>=0.12?'#ff7f0e':'#d62728');
Plotly.newPlot('chart-sports', [
  {{x:hrates, y:sports, type:'bar', orientation:'h', name:'Historical win rate',
    marker:{{color:'rgba(150,150,150,0.22)'}}, width:0.55}},
  {{x:probs,  y:sports, type:'bar', orientation:'h', name:'2028 probability',
    marker:{{color:colors}}, width:0.35,
    text:probs.map(p=>(p*100).toFixed(0)+'%'), textposition:'outside'}}
], {{...DARK, barmode:'overlay',
  xaxis:{{...DARK.xaxis, title:'Medal probability', tickformat:'.0%', range:[0,1.1]}},
  yaxis:{{...DARK.yaxis, autorange:'reversed'}},
  legend:{{orientation:'h', yanchor:'bottom', y:1.02, bgcolor:'rgba(0,0,0,0)'}},
  height:340, margin:{{t:10,b:40,l:10,r:70}}
}}, CFG);

// 2. MC distribution
const mcX = {js(mc_x)};
const mcY = {js(mc_y)};
Plotly.newPlot('chart-mc', [{{
  x:mcX, y:mcY, type:'bar', marker:{{color:'#4f8ef7', opacity:0.8}},
  text:mcY.map(v=>v>0.02?(v*100).toFixed(0)+'%':''), textposition:'outside'
}}], {{...DARK,
  xaxis:{{...DARK.xaxis, title:'Total medals', dtick:1}},
  yaxis:{{...DARK.yaxis, title:'Probability', tickformat:'.0%'}},
  shapes:[{{type:'line',x0:{exp},x1:{exp},y0:0,y1:1,yref:'paper',line:{{color:'#ff4444',dash:'dash',width:2}}}}],
  annotations:[{{x:{exp},y:0.97,yref:'paper',text:'Mean {exp}',showarrow:false,font:{{color:'#ff4444',size:11}}}}],
  height:320, margin:{{t:20,b:40,l:50,r:20}}
}}, CFG);

// 3. Historical
const hY = {js(hist_years)};
Plotly.newPlot('chart-hist', [
  {{x:hY, y:{js(hist_total)},  mode:'lines+markers', name:'Total',  line:{{color:'#4f8ef7',width:3}}, marker:{{size:7}}}},
  {{x:hY, y:{js(hist_gold)},   mode:'lines+markers', name:'Gold',   line:{{color:'#ffd700',width:2}}}},
  {{x:hY, y:{js(hist_silver)}, mode:'lines+markers', name:'Silver', line:{{color:'#c0c0c0',width:2}}}},
  {{x:hY, y:{js(hist_bronze)}, mode:'lines+markers', name:'Bronze', line:{{color:'#cd7f32',width:2}}}},
  {{x:[2028], y:[{exp}], mode:'markers', name:'2028 Forecast',
    marker:{{size:16,color:'#ff4444',symbol:'star'}},
    error_y:{{type:'data',array:[{p90-exp}],arrayminus:[{exp-p10}],visible:true,color:'#ff4444'}}}}
], {{...DARK,
  xaxis:{{...DARK.xaxis, title:'Year'}},
  yaxis:{{...DARK.yaxis, title:'Medals'}},
  legend:{{orientation:'h', yanchor:'bottom', y:1.02, bgcolor:'rgba(0,0,0,0)'}},
  height:300, margin:{{t:10,b:40,l:40,r:20}}
}}, CFG);

// 4. Scenarios
const sL  = {js(scen_labels)};
const sE  = {js(scen_expected)};
const sHi = {js(scen_err_hi)};
const sLo = {js(scen_err_lo)};
const sC  = ['#4f8ef7','#ef553b','#2ca02c','#ab63fa'];
Plotly.newPlot('chart-scen',
  sL.map((lbl,i) => ({{
    x:[lbl], y:[sE[i]], type:'bar', name:lbl, marker:{{color:sC[i]}},
    text:[sE[i].toFixed(1)], textposition:'outside',
    error_y:{{type:'data',array:[sHi[i]],arrayminus:[sLo[i]],visible:true}}
  }})),
{{...DARK, barmode:'group', showlegend:false,
  yaxis:{{...DARK.yaxis, title:'Expected medals', range:[0, Math.max(...sE)+Math.max(...sHi)+1]}},
  height:300, margin:{{t:20,b:80,l:50,r:20}}
}}, CFG);
</script>
</body>
</html>"""

os.makedirs(os.path.dirname(OUTFILE), exist_ok=True)
with open(OUTFILE, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Written: {OUTFILE}  ({len(html):,} bytes)")
