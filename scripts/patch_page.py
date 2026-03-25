"""Patch docs/index.html with decomposition chart, outlier table, partner notes."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

ROOT = os.path.join(os.path.dirname(__file__), "..")

with open(os.path.join(ROOT, "data/processed/ltu_sport_probs.json"), encoding="utf-8") as f:
    probs_data = json.load(f)

sports = [s for s in probs_data if not s.startswith("_") and s != "Breaking"]
decomp = sorted([{
    "sport":   s,
    "final":   probs_data[s]["base_prob_2028"],
    "athlete": probs_data[s].get("athlete_model_prob", probs_data[s]["base_prob_2028"]),
    "hist":    probs_data[s].get("bayesian_weighted_rate", probs_data[s]["historical_win_rate"]),
} for s in sports], key=lambda x: -x["final"])

outliers = [o for o in probs_data.get("_outlier_candidates", []) if not o.get("known_contender")]
outliers.sort(key=lambda x: x["age_2028"])

contender_rows = []
for s in sorted(sports, key=lambda x: -probs_data[x]["base_prob_2028"]):
    for c in probs_data[s].get("contenders", []):
        ep = c.get("event_medal_prob", 0)
        if ep >= 0.03:
            contender_rows.append({
                "sport": s, "athlete": c["athlete"], "event": c["event"],
                "rank": c["rank_2024"], "age": c["age_2028"],
                "prob": ep, "psych": c["psych"],
                "notes": c["notes"][:90] + ("..." if len(c["notes"]) > 90 else ""),
            })

meta = probs_data.get("_meta", {})
m50 = meta.get("meilutyte_50m_prob_if_confirmed", 0.42)

def js(v):
    return json.dumps(v)

# Decomposition chart data
d_sports  = js([d["sport"]  for d in decomp])
d_final   = js([d["final"]  for d in decomp])
d_athlete = js([d["athlete"]for d in decomp])
d_hist    = js([d["hist"]   for d in decomp])

# Outlier table rows
out_rows = ""
for o in outliers[:12]:
    out_rows += (
        f"<tr><td><strong>{o['name']}</strong></td>"
        f"<td>{o['sport']}</td>"
        f"<td>{o['age_2028']}</td>"
        f"<td>{o.get('birth_year','')}</td>"
        f'<td><span class="pill med">Prime 2028</span></td></tr>'
    )

# Contender table rows
cont_rows = ""
for c in contender_rows:
    if c["psych"] >= 1.0:
        psych_color = "var(--green)"
        psych_label = "Normal"
    elif c["psych"] >= 0.9:
        psych_color = "var(--accent)"
        psych_label = "Slight discount"
    else:
        psych_color = "var(--orange)"
        psych_label = "Olympic underperformer"
    cont_rows += (
        f"<tr>"
        f"<td><strong>{c['athlete']}</strong></td>"
        f'<td class="muted small">{c["event"]}</td>'
        f"<td><strong>#{c['rank']}</strong></td>"
        f"<td>{c['age']}</td>"
        f"<td><strong>{c['prob']:.0%}</strong></td>"
        f'<td style="color:{psych_color};font-size:.76rem">{psych_label}</td>'
        f'<td class="muted small">{c["notes"]}</td>'
        f"</tr>"
    )

new_html = f"""
<!-- PROBABILITY DECOMPOSITION -->
<section>
  <h2>How Each Sport Probability Is Built</h2>
  <div class="grid grid-2">
    <div class="card">
      <h2>Athlete Model vs Historical Rate</h2>
      <p class="caption">Grey = recency-weighted historical win rate. Blue = athlete ranking model (union of contenders). Red diamond = final blended estimate.</p>
      <div id="chart-decomp"></div>
    </div>
    <div class="card">
      <h2>Athlete Pipeline &amp; World Rankings</h2>
      <p class="caption">Event medal prob = rank_prob x psych_factor x age_factor. Union across contenders = sport probability.</p>
      <div style="overflow-x:auto">
      <table>
        <tr><th>Athlete</th><th>Event</th><th>Rank</th><th>Age 2028</th><th>Event prob</th><th>Olympic factor</th><th>Notes</th></tr>
        {cont_rows}
      </table>
      </div>
    </div>
  </div>
</section>

<!-- OUTLIERS -->
<section>
  <h2>Emerging Athletes &mdash; Not in Current Predictions</h2>
  <p style="color:var(--muted);font-size:.82rem;margin-bottom:14px">
    Partner insight: NICKA and Senkute were not in predictions for 2024 either.
    These athletes competed at Paris 2024, are at prime age in 2028, but have no identified
    medal path yet. Worth tracking as 2028 approaches.
  </p>
  <div class="grid grid-2">
    <div class="card">
      <table>
        <tr><th>Athlete</th><th>Sport</th><th>Age 2028</th><th>Born</th><th>Status</th></tr>
        {out_rows}
      </table>
    </div>
    <div class="card">
      <h2>50m Breaststroke &mdash; Conditional Scenario</h2>
      <p class="caption">
        Ruta Meilutyte is world champion and record holder in 50m breaststroke (partner note).
        If confirmed for LA 2028, her probability in that event alone is estimated at {m50:.0%}.
      </p>
      <div style="background:#1b3a1b;border:1px solid #2d5a2d;border-radius:8px;padding:14px;margin-top:8px;font-size:.81rem;color:#6fcf6f;line-height:1.8">
        <strong>Current model (100m breast only):</strong> Swimming = 27%<br>
        <strong>If 50m breast confirmed for LA 2028:</strong> Swimming approx 50%<br>
        <strong>Source:</strong> World Aquatics Programme Commission lobbying, 2024<br>
        <strong>Status:</strong> Pending IOC confirmation
      </div>
      <div style="margin-top:12px;font-size:.78rem;color:var(--muted);line-height:1.6">
        <em>Partner note: "She is the 50m world champion and record holder, and the 50m is a new discipline
        at the Olympics, so she has an advantage. That said, she also needs to work on the psychological aspect,
        as she doesn't always perform well at the Olympics." Last Olympic medal: gold 2012.</em>
      </div>
    </div>
  </div>
</section>

<!-- PARTNER NOTES -->
<section>
  <h2>Model Revisions from Partner Analysis</h2>
  <div class="card">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px">
      <div>
        <div style="font-size:.8rem;font-weight:700;color:var(--accent);margin-bottom:6px">Alekna: 82% to 58% (psychological factor)</div>
        <div style="font-size:.78rem;color:var(--muted);line-height:1.6">
          World #1 rank gives 62% base probability. Psych factor 0.90 applied: silver (not gold) at Paris despite world lead.
          Age corrected to 25/26 in 2028 (born Sept 2002, not 2004). Competition field will improve.
          Still the top gold candidate globally, just not a near-certainty.
        </div>
      </div>
      <div>
        <div style="font-size:.8rem;font-weight:700;color:var(--accent);margin-bottom:6px">Senkute: age corrected to 32 (not 27)</div>
        <div style="font-size:.78rem;color:var(--muted);line-height:1.6">
          Born 1996-04-12 from Paris 2024 athletes data. Partner was correct: age 32 in 2028.
          32 is near the upper range of peak sculling age but not past it. Still a serious contender.
        </div>
      </div>
      <div>
        <div style="font-size:.8rem;font-weight:700;color:var(--accent);margin-bottom:6px">Venckauskaite: age 35-36, not "next gen"</div>
        <div style="font-size:.78rem;color:var(--muted);line-height:1.6">
          Born 1992-11-04. Same generation as Asadauskaite (born 1984). Modern Pentathlon
          probability revised down sharply. No clear next-generation pentathlete identified.
        </div>
      </div>
      <div>
        <div style="font-size:.8rem;font-weight:700;color:var(--accent);margin-bottom:6px">Martynas Alekna: outlier find</div>
        <div style="font-size:.78rem;color:var(--muted);line-height:1.6">
          Mykolas's brother, born 2000, age 28 in 2028. Also a discus thrower at Paris 2024.
          Not in original model. Added as secondary contender in Athletics via union formula,
          contributing ~3% independently at current world ranking ~18.
        </div>
      </div>
    </div>
  </div>
</section>

<script>
Plotly.newPlot('chart-decomp', [
  {{x:{d_hist},    y:{d_sports}, type:'bar', orientation:'h', name:'Historical (recency-weighted)',
    marker:{{color:'rgba(140,140,170,0.35)'}}, width:0.55}},
  {{x:{d_athlete}, y:{d_sports}, type:'bar', orientation:'h', name:'Athlete model (rankings)',
    marker:{{color:'rgba(79,142,247,0.55)'}}, width:0.35}},
  {{x:{d_final},   y:{d_sports}, type:'scatter', mode:'markers+text', name:'Final blended',
    marker:{{color:'#ff4444', size:9, symbol:'diamond'}},
    text:{d_final}.map(p=>(p*100).toFixed(0)+'%'), textposition:'middle right'}}
], {{
  paper_bgcolor:'#1a1d27', plot_bgcolor:'#1a1d27',
  font:{{color:'#e8eaf0', size:11}},
  barmode:'overlay',
  xaxis:{{gridcolor:'#2d3148', title:'Probability', tickformat:'.0%', range:[0,0.85]}},
  yaxis:{{gridcolor:'#2d3148', autorange:'reversed'}},
  legend:{{orientation:'h', yanchor:'bottom', y:1.02, bgcolor:'rgba(0,0,0,0)'}},
  height:320, margin:{{t:10, b:40, l:10, r:80}}
}}, {{responsive:true, displayModeBar:false}});
</script>
"""

page_path = os.path.join(ROOT, "docs/index.html")
with open(page_path, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("</body>", new_html + "\n</body>")

with open(page_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Patched docs/index.html -> {len(html):,} bytes")
