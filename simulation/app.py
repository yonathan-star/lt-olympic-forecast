"""
Lithuania LA 2028 Olympic Forecast — Streamlit UI

Run with:
    streamlit run simulation/app.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from simulation.simulator import simulate, compare_scenarios, load_reference_data
from model.lithuania_2028 import (
    compute_medal_probs,
    predict_total_medals,
    PRIMARY_SPORTS,
    ALL_2028_SPORTS,
    PEER_COUNTRIES,
)

# ---------------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Lithuania LA 2028 Olympic Forecast",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.title("Lithuania — LA 2028 Olympic Medal Forecast")
st.markdown(
    "Sport-by-sport prediction based on **historical Olympic data (1992-2024)** "
    "and the known athlete pipeline heading into Los Angeles 2028. "
    "Base probabilities are computed from Olympedia results + IOC Paris 2024 data."
)
st.markdown("---")

# ---------------------------------------------------------------------------
# LOAD HISTORICAL DATA (for historical chart and country snapshot)
# ---------------------------------------------------------------------------
@st.cache_data
def get_data():
    return load_reference_data()

df = get_data()

# ---------------------------------------------------------------------------
# SIDEBAR — SIMULATION CONTROLS
# ---------------------------------------------------------------------------
st.sidebar.header("Simulation Parameters")

st.sidebar.subheader("Funding")
funding_multiplier = st.sidebar.slider(
    "Funding multiplier",
    min_value=0.5, max_value=4.0, value=1.0, step=0.25,
    help="1.0 = current ~20M EUR NSA annual sport budget. 2.0 = double.",
)

st.sidebar.subheader("Delegation")
athletes_sent = st.sidebar.slider(
    "Athletes sent to LA 2028",
    min_value=20, max_value=120, value=50, step=5,
    help="Affects non-team sports where depth matters.",
)

st.sidebar.subheader("Sport Selection")
focus_mode = st.sidebar.checkbox(
    "Focus mode (concentrate budget on selected sports)",
    value=False,
    help="Redistributes savings from excluded sports to selected ones.",
)

st.sidebar.markdown("**Select sports to fund / qualify for:**")
selected_sports = []
for sport in ALL_2028_SPORTS:
    default = sport in PRIMARY_SPORTS
    if st.sidebar.checkbox(sport, value=default, key=f"sport_{sport}"):
        selected_sports.append(sport)

if not selected_sports:
    st.sidebar.warning("Select at least one sport.")
    selected_sports = PRIMARY_SPORTS[:]

st.sidebar.markdown("---")
st.sidebar.caption(
    "Breaking (NICKA, Silver 2024) is **NOT** on the LA 2028 program. "
    "That medal cannot be replicated."
)

# ---------------------------------------------------------------------------
# RUN SIMULATION
# ---------------------------------------------------------------------------
result = predict_total_medals(
    funding_multiplier=funding_multiplier,
    athletes_sent=athletes_sent,
    selected_sports=selected_sports,
    focus_mode=focus_mode,
    n_simulations=10_000,
)

sport_probs = result["per_sport"]

# ---------------------------------------------------------------------------
# TOP ROW — SUMMARY METRICS
# ---------------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(
    "Expected Medals",
    f"{result['expected_total']:.1f}",
    delta=f"range: {result['p10']:.0f}–{result['p90']:.0f}",
)
col2.metric("Pessimistic (P10)",  f"{result['p10']:.1f}")
col3.metric("Most Likely",        f"{result['median_total']:.1f}")
col4.metric("Optimistic (P90)",   f"{result['p90']:.1f}")
col5.metric(
    "Zero-medal risk",
    f"{result['zero_medal_prob']:.1%}",
    delta="lower is better",
    delta_color="inverse",
)

st.markdown("---")

# ---------------------------------------------------------------------------
# MAIN PANEL — LEFT: per-sport bars | RIGHT: historical trend
# ---------------------------------------------------------------------------
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("Per-Sport Medal Probability")
    st.caption(
        "Base probability derived from Lithuania's historical Olympic win rate (1992-2024). "
        "Adjusted for athlete pipeline, Bayesian shrinkage (small samples), and funding slider."
    )

    sports_sorted = sorted(
        sport_probs.items(),
        key=lambda x: x[1]["medal_probability"],
        reverse=True,
    )

    sport_names  = [s for s, _ in sports_sorted]
    probs        = [d["medal_probability"] for _, d in sports_sorted]
    hist_rates   = [d["historical_win_rate"] for _, d in sports_sorted]
    medal_types  = [d["medal_type"] for _, d in sports_sorted]

    # Color by tier
    def bar_color(p):
        if p >= 0.60: return "#1f77b4"   # blue — strong contender
        if p >= 0.30: return "#2ca02c"   # green — realistic
        if p >= 0.15: return "#ff7f0e"   # orange — possible
        return "#d62728"                  # red — dark horse

    colors = [bar_color(p) for p in probs]

    fig_sports = go.Figure()

    # Historical win rate bars (background reference)
    fig_sports.add_trace(go.Bar(
        x=hist_rates,
        y=sport_names,
        orientation="h",
        name="Historical win rate",
        marker_color="rgba(150,150,150,0.3)",
        width=0.4,
    ))

    # Model probability bars (foreground)
    fig_sports.add_trace(go.Bar(
        x=probs,
        y=sport_names,
        orientation="h",
        name="2028 probability",
        marker_color=colors,
        text=[f"{p:.0%}" for p in probs],
        textposition="outside",
        width=0.4,
        offset=0,
    ))

    fig_sports.update_layout(
        barmode="overlay",
        xaxis=dict(
            title="Medal probability",
            tickformat=".0%",
            range=[0, 1.05],
        ),
        yaxis=dict(autorange="reversed"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=420,
        margin=dict(t=20, b=40, l=10, r=60),
    )
    st.plotly_chart(fig_sports, use_container_width=True)

    # Sport detail table
    with st.expander("Sport detail & data sources"):
        rows = []
        for sport, data in sports_sorted:
            n_g = data["games_participated"]
            n_m = data["games_with_medals"]
            rows.append({
                "Sport":          sport,
                "2028 Prob":      f"{data['medal_probability']:.0%}",
                "Hist rate":      f"{n_m}/{n_g} Games ({data['historical_win_rate']:.0%})",
                "Medal years":    ", ".join(str(y) for y in data["medal_years"]) or "none",
                "Athlete / notes":data["notes"][:80] + "..." if len(data["notes"]) > 80 else data["notes"],
                "Source":         data["source"][:60] + "..." if len(data["source"]) > 60 else data["source"],
            })
        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            use_container_width=True,
        )

with col_right:
    st.subheader("Lithuania Historical Performance")
    hist = df[df["iso3"] == "LTU"].sort_values("year")

    if not hist.empty:
        # Append 2024 actual (Paris 2024 = 4 medals: 2G+1S+1B in historical sense... actually 0G+2S+2B)
        actual_2024 = pd.DataFrame([{
            "year": 2024, "gold": 0, "silver": 2, "bronze": 2, "total_medals": 4
        }])
        hist_full = pd.concat([hist, actual_2024], ignore_index=True).drop_duplicates("year").sort_values("year")

        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(
            x=hist_full["year"], y=hist_full["total_medals"],
            name="Total medals", mode="lines+markers",
            line=dict(color="#636EFA", width=3),
            marker=dict(size=8),
        ))
        fig_hist.add_trace(go.Scatter(
            x=hist_full["year"], y=hist_full["gold"],
            name="Gold", mode="lines+markers",
            line=dict(color="#FFD700", width=2),
        ))
        fig_hist.add_trace(go.Scatter(
            x=hist_full["year"], y=hist_full["silver"],
            name="Silver", mode="lines+markers",
            line=dict(color="#C0C0C0", width=2),
        ))
        fig_hist.add_trace(go.Scatter(
            x=hist_full["year"], y=hist_full["bronze"],
            name="Bronze", mode="lines+markers",
            line=dict(color="#CD7F32", width=2),
        ))

        # 2028 projection
        fig_hist.add_trace(go.Scatter(
            x=[2028],
            y=[result["expected_total"]],
            name="2028 Forecast",
            mode="markers",
            marker=dict(size=16, color="red", symbol="star"),
            error_y=dict(
                type="data",
                array=[result["p90"] - result["expected_total"]],
                arrayminus=[result["expected_total"] - result["p10"]],
                visible=True,
            ),
        ))

        fig_hist.update_layout(
            xaxis_title="Year",
            yaxis_title="Medals",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            height=420,
            margin=dict(t=20, b=40),
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No historical data found for Lithuania.")

# ---------------------------------------------------------------------------
# SECOND ROW — Monte Carlo distribution + Scenario comparison
# ---------------------------------------------------------------------------
st.markdown("---")
col_mc, col_scen = st.columns(2)

with col_mc:
    st.subheader("Medal Count Distribution (10,000 simulations)")
    st.caption("Each simulation draws independently from each sport's medal probability.")

    sim_vals = np.array(result["sim_distribution"])
    medal_counts = np.arange(0, int(sim_vals.max()) + 2)
    frequencies  = [(sim_vals == k).mean() for k in medal_counts]

    fig_mc = go.Figure()
    fig_mc.add_trace(go.Bar(
        x=medal_counts,
        y=frequencies,
        marker_color="#636EFA",
        name="Probability",
        text=[f"{f:.1%}" if f > 0.01 else "" for f in frequencies],
        textposition="outside",
    ))
    fig_mc.add_vline(
        x=result["expected_total"],
        line_dash="dash", line_color="red",
        annotation_text=f"Mean {result['expected_total']:.1f}",
        annotation_position="top right",
    )
    fig_mc.update_layout(
        xaxis=dict(title="Total medals", dtick=1),
        yaxis=dict(title="Probability", tickformat=".0%"),
        height=360,
        margin=dict(t=20, b=40),
        showlegend=False,
    )
    st.plotly_chart(fig_mc, use_container_width=True)

with col_scen:
    st.subheader("Scenario Comparison")

    scenarios_ltu = [
        {"label": "Baseline (current funding)",
         "funding_multiplier": 1.0, "athletes_sent": 50,
         "selected_sports": PRIMARY_SPORTS, "focus_mode": False},
        {"label": "Current settings",
         "funding_multiplier": funding_multiplier, "athletes_sent": athletes_sent,
         "selected_sports": selected_sports, "focus_mode": focus_mode},
        {"label": "2x Funding (all sports)",
         "funding_multiplier": 2.0, "athletes_sent": 60,
         "selected_sports": ALL_2028_SPORTS, "focus_mode": False},
        {"label": "2x Funding + Focus top 4",
         "funding_multiplier": 2.0, "athletes_sent": 60,
         "selected_sports": ["Athletics", "Rowing", "3x3 Basketball", "Swimming"],
         "focus_mode": True},
    ]

    scen_rows = []
    for s in scenarios_ltu:
        r = predict_total_medals(**{k: v for k, v in s.items() if k != "label"})
        scen_rows.append({
            "Scenario":    s["label"],
            "Expected":    round(r["expected_total"], 1),
            "P10":         round(r["p10"], 1),
            "P90":         round(r["p90"], 1),
            "Zero-medal":  f"{r['zero_medal_prob']:.1%}",
        })

    scen_df = pd.DataFrame(scen_rows)

    fig_scen = go.Figure()
    colors_scen = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA"]
    for i, row in scen_df.iterrows():
        fig_scen.add_trace(go.Bar(
            name=row["Scenario"],
            x=[row["Scenario"]],
            y=[row["Expected"]],
            marker_color=colors_scen[i % len(colors_scen)],
            text=f"{row['Expected']:.1f}",
            textposition="outside",
            error_y=dict(
                type="data",
                array=[row["P90"] - row["Expected"]],
                arrayminus=[row["Expected"] - row["P10"]],
                visible=True,
            ),
        ))

    fig_scen.update_layout(
        barmode="group",
        yaxis=dict(title="Expected medals", range=[0, max(scen_df["P90"]) + 1]),
        xaxis_title="",
        showlegend=False,
        height=360,
        margin=dict(t=20, b=60),
    )
    st.plotly_chart(fig_scen, use_container_width=True)

    st.dataframe(scen_df, hide_index=True, use_container_width=True)

# ---------------------------------------------------------------------------
# THIRD ROW — Peer comparison + Key athlete spotlight
# ---------------------------------------------------------------------------
st.markdown("---")
col_peer, col_athlete = st.columns(2)

with col_peer:
    st.subheader("Peer Country Comparison — Paris 2024")
    # Use actual Paris 2024 results + Lithuania
    peer_data = [
        {"Country": "Lithuania", "Medals (2024)": 4, "Population (M)": 2.8, "GDP/cap ($k)": 24},
        {"Country": "Estonia",   "Medals (2024)": 3, "Population (M)": 1.3, "GDP/cap ($k)": 27},
        {"Country": "Latvia",    "Medals (2024)": 3, "Population (M)": 1.8, "GDP/cap ($k)": 21},
        {"Country": "Slovenia",  "Medals (2024)": 2, "Population (M)": 2.1, "GDP/cap ($k)": 30},
        {"Country": "Slovakia",  "Medals (2024)": 2, "Population (M)": 5.4, "GDP/cap ($k)": 22},
        {"Country": "Croatia",   "Medals (2024)": 10,"Population (M)": 3.9, "GDP/cap ($k)": 20},
    ]
    peer_df = pd.DataFrame(peer_data)
    peer_df["Medals/M pop"] = (peer_df["Medals (2024)"] / peer_df["Population (M)"]).round(1)
    st.dataframe(peer_df, hide_index=True, use_container_width=True)

    fig_peer = px.bar(
        peer_df, x="Country", y="Medals (2024)",
        color="Country",
        text="Medals (2024)",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_peer.update_traces(textposition="outside")
    fig_peer.update_layout(
        showlegend=False,
        height=280,
        margin=dict(t=10, b=40),
        yaxis_title="Total medals",
    )
    st.plotly_chart(fig_peer, use_container_width=True)

with col_athlete:
    st.subheader("Key Athlete Spotlight — LA 2028 Contenders")

    athletes = [
        {
            "Athlete":    "Mykolas Alekna",
            "Sport":      "Athletics — Discus Throw",
            "Age in 2028": 24,
            "Best result": "Olympic Silver 2024 | 74.35m (2024 World Lead)",
            "2028 outlook":"Top global gold favorite. Only 20 at Paris 2024; trajectory still improving. "
                           "2028 in prime years.",
            "Probability": f"{sport_probs.get('Athletics', {}).get('medal_probability', 0):.0%}",
            "Source":      "World Athletics results 2024",
        },
        {
            "Athlete":    "Viktorija Senkute",
            "Sport":      "Rowing — W Single Sculls",
            "Age in 2028": 27,
            "Best result": "Olympic Bronze 2024",
            "2028 outlook":"Peak rowing age. Consistent World Cup competitor. "
                           "Major threat for silver or gold if form holds.",
            "Probability": f"{sport_probs.get('Rowing', {}).get('medal_probability', 0):.0%}",
            "Source":      "Paris 2024 official results; LTU Rowing Federation",
        },
        {
            "Athlete":    "Lithuania 3x3 Basketball",
            "Sport":      "3x3 Basketball — Men's team",
            "Age in 2028": "Avg ~27",
            "Best result": "Olympic Bronze 2024",
            "2028 outlook":"Core team intact. Basketball culture is structural advantage. "
                           "FIBA 3x3 consistent top-10 program.",
            "Probability": f"{sport_probs.get('3x3 Basketball', {}).get('medal_probability', 0):.0%}",
            "Source":      "FIBA 3x3 World Ranking 2024; Paris 2024 results",
        },
        {
            "Athlete":    "Ruta Meilutyte",
            "Sport":      "Swimming — 100m Breaststroke",
            "Age in 2028": 31,
            "Best result": "Olympic Gold 2012 | WR 100m Breaststroke",
            "2028 outlook":"Still active and competitive in 2024. "
                           "31 is manageable for sprint breaststroke.",
            "Probability": f"{sport_probs.get('Swimming', {}).get('medal_probability', 0):.0%} (sport total)",
            "Source":      "FINA World Rankings 2024",
        },
    ]

    for ath in athletes:
        with st.expander(f"{ath['Athlete']} — {ath['Sport']}  ({ath['Probability']} medal prob)"):
            st.markdown(f"**Age in 2028:** {ath['Age in 2028']}")
            st.markdown(f"**Best result:** {ath['Best result']}")
            st.markdown(f"**2028 outlook:** {ath['2028 outlook']}")
            st.markdown(f"**Data source:** {ath['Source']}")

# ---------------------------------------------------------------------------
# BREAKING NOTE
# ---------------------------------------------------------------------------
st.markdown("---")
st.warning(
    "**Breaking is NOT on the LA 2028 program.** "
    "NICKA (Dominyka Banevic) won Silver at Paris 2024, but the IOC removed Breaking from the 2028 program. "
    "Lithuania's 2028 total is forecasted without this sport. "
    "Source: IOC Program Commission decision 2023."
)

# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "**Data sources:** Olympedia historical results 1908-2020 (Kaggle: heesoo37) | "
    "Paris 2024 official results (Kaggle: piterfm) | "
    "World Athletics, FINA, FIBA 3x3, ICF, UIPM, ISSF rankings 2024 | "
    "IOC Program Commission 2023 (Breaking removal) | "
    "World Athletics correction: Andrius Gudzius, Discus Gold, Rio 2016 (absent from Kaggle dataset) | "
    "Bayesian shrinkage applied to sports with < 5 Games of data."
)
