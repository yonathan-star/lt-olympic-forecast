"""
Lithuania-specific LA 2028 Olympic predictor.

Unlike the macro model (which uses GDP/population), this module models
Lithuania's medal chances sport-by-sport based on:
  - Historical medal rates per sport (computed from Olympedia + Paris 2024 data)
  - Known athlete pipeline (active medal contenders as of 2024-2025)
  - Sport funding allocation slider
  - LA 2028 specific factors (Breaking removed, new sports, travel)

Base probabilities are derived from:
  scripts/compute_ltu_sport_probs.py  ->  data/processed/ltu_sport_probs.json

Method:
  - Historical win rate = Games_with_medal / Games_participated (post-1988)
  - Bayesian shrinkage applied to sports with < 5 Games of data
  - Forward-looking pipeline_factor applied (athlete age, active contenders)
  - Data sources: Olympedia 1908-2020, IOC Paris 2024, World Athletics,
    FINA, FIBA 3x3, ICF, UIPM, ISSF rankings 2024

This is the primary prediction engine for the Lithuania simulation.
"""

import json, os
import numpy as np
import pandas as pd

ROOT       = os.path.join(os.path.dirname(__file__), "..")
PROBS_FILE = os.path.join(ROOT, "data", "processed", "ltu_sport_probs.json")

# ---------------------------------------------------------------------------
# LOAD DATA-DERIVED BASE PROBABILITIES
# ---------------------------------------------------------------------------
def _load_sport_probs() -> dict:
    """Load per-sport base probabilities computed from historical data."""
    if not os.path.exists(PROBS_FILE):
        raise FileNotFoundError(
            f"Sport probabilities file not found: {PROBS_FILE}\n"
            f"Run: python scripts/compute_ltu_sport_probs.py"
        )
    with open(PROBS_FILE, encoding="utf-8") as f:
        return json.load(f)

# ---------------------------------------------------------------------------
# SPORT METADATA — funding sensitivity, team flag, display info
# These do NOT include base_prob (loaded from JSON computed from real data).
# funding_sensitivity: how much prob increases per unit of eff_funding above 1.0
# ---------------------------------------------------------------------------
SPORT_META = {
    "Athletics": {
        "funding_sensitivity": 0.03,  # Alekna already world-class; funding helps less
        "is_team": False,
        "medal_type": "Gold/Silver contender",
        "la_2028_note": "Mykolas Alekna (21 in 2028): Olympic silver 2024, world lead 74.35m. "
                        "Top global favorite. Andrius Gudzius may also compete.",
        "in_2028": True,
    },
    "Rowing": {
        "funding_sensitivity": 0.07,
        "is_team": False,
        "medal_type": "Bronze/Silver contender",
        "la_2028_note": "Viktorija Senkute (27 in 2028): Olympic bronze 2024 (W Single Sculls). "
                        "Peak rowing age. Strong program with funding upside.",
        "in_2028": True,
    },
    "Modern Pentathlon": {
        "funding_sensitivity": 0.06,
        "is_team": False,
        "medal_type": "Unlikely without new contender",
        "la_2028_note": "Laura Asadauskaite (44 in 2028): virtually certain to have retired. "
                        "Gintare Venckauskaite is the development pipeline but unproven at senior level.",
        "in_2028": True,
    },
    "Swimming": {
        "funding_sensitivity": 0.08,
        "is_team": False,
        "medal_type": "Bronze contender",
        "la_2028_note": "Ruta Meilutyte (31 in 2028): WR holder 100m breaststroke, Olympic gold 2012. "
                        "Danas Rapsys (33 in 2028): multiple Olympic A-finals. Two realistic contenders.",
        "in_2028": True,
    },
    "3x3 Basketball": {
        "funding_sensitivity": 0.04,
        "is_team": True,
        "medal_type": "Bronze/Silver contender",
        "la_2028_note": "Olympic bronze 2024. Core roster avg 27 in 2028 (peak). "
                        "Lithuania basketball culture is structural advantage. "
                        "Probability reflects Bayesian adjustment from 1-game sample.",
        "in_2028": True,
    },
    "Canoe Sprint": {
        "funding_sensitivity": 0.07,
        "is_team": False,
        "medal_type": "Dark horse",
        "la_2028_note": "2016 bronze (K2-200m). No confirmed 2028 contender identified yet.",
        "in_2028": True,
    },
    "Shooting": {
        "funding_sensitivity": 0.05,
        "is_team": False,
        "medal_type": "Dark horse",
        "la_2028_note": "Last medal: Daina Gudzineviciute, Trap Gold 2000. "
                        "No current ISSF top-20 Lithuanian shooter identified.",
        "in_2028": True,
    },
    "Weightlifting": {
        "funding_sensitivity": 0.05,
        "is_team": False,
        "medal_type": "Dark horse",
        "la_2028_note": "Aurimas Didzbalis bronze 2016. Program affected by IWF sanctions era. "
                        "No confirmed 2028 contender.",
        "in_2028": True,
    },
    "Wrestling": {
        "funding_sensitivity": 0.05,
        "is_team": False,
        "medal_type": "Dark horse",
        "la_2028_note": "2 medals (2008, 2012). No current UWW top-global Lithuanian contender.",
        "in_2028": True,
    },
    "Breaking": {
        "funding_sensitivity": 0.0,
        "is_team": False,
        "medal_type": "REMOVED from 2028",
        "la_2028_note": "NICKA won Silver at Paris 2024. Breaking is NOT on the LA 2028 program. "
                        "This medal cannot be replicated at LA 2028.",
        "in_2028": False,
    },
}

# Sports to show in the focused LA 2028 view (exclude low-probability dark horses from default)
PRIMARY_SPORTS = [
    "Athletics", "Rowing", "3x3 Basketball", "Modern Pentathlon", "Swimming",
]
ALL_2028_SPORTS = [s for s, m in SPORT_META.items() if m["in_2028"]]

# ---------------------------------------------------------------------------
# FUNDING EFFECT MODEL
# ---------------------------------------------------------------------------
def compute_medal_probs(
    funding_multiplier: float = 1.0,
    athletes_sent: int = 50,
    selected_sports: list = None,
    focus_mode: bool = False,
) -> dict:
    """
    Compute per-sport medal probabilities for Lithuania at LA 2028.

    Parameters
    ----------
    funding_multiplier : float
        1.0 = current ~20M EUR NSA budget. 2.0 = double.
    athletes_sent : int
        Total delegation size. Affects sports where depth matters.
    selected_sports : list
        Which sports to include. None = all sports in 2028 program.
    focus_mode : bool
        If True, redistribute non-selected sport funding to selected sports
        (concentrated investment increases each sport's probability more).

    Returns
    -------
    dict : {sport_name: {medal_probability, medal_type, notes, ...}}
    """
    probs_data = _load_sport_probs()
    in_2028    = {s: m for s, m in SPORT_META.items() if m["in_2028"]}

    if selected_sports:
        active = {s: m for s, m in in_2028.items() if s in selected_sports}
    else:
        active = in_2028

    # Focus bonus: concentrating budget on fewer sports redistributes funding
    if focus_mode and selected_sports:
        n_total   = len(in_2028)
        n_active  = len(active)
        focus_bonus = n_total / max(n_active, 1)
        eff_funding = funding_multiplier * focus_bonus
    else:
        eff_funding = funding_multiplier

    results = {}
    for sport, meta in active.items():
        sport_data = probs_data.get(sport, {})
        p = sport_data.get("base_prob_2028", 0.1)

        # Funding effect: diminishing returns via sqrt scaling
        funding_delta = (eff_funding - 1.0)
        p = p + meta["funding_sensitivity"] * funding_delta * np.sqrt(max(eff_funding, 0.1))

        # Athlete count effect: more athletes = slightly higher prob for non-team sports
        if not meta["is_team"]:
            ath_ratio = min(athletes_sent / 50.0, 2.0)
            p = p * (0.85 + 0.15 * ath_ratio)

        p = float(np.clip(p, 0.0, 0.95))

        results[sport] = {
            "medal_probability":  p,
            "base_prob_data":     sport_data.get("base_prob_2028", 0.0),
            "historical_win_rate":sport_data.get("historical_win_rate", 0.0),
            "games_with_medals":  sport_data.get("games_with_medals", 0),
            "games_participated": sport_data.get("games_participated", 0),
            "medal_years":        sport_data.get("medal_years", []),
            "medal_type":         meta["medal_type"],
            "notes":              meta["la_2028_note"],
            "source":             sport_data.get("source", ""),
            "is_team":            meta["is_team"],
        }

    return results


def predict_total_medals(
    funding_multiplier: float = 1.0,
    athletes_sent: int = 50,
    selected_sports: list = None,
    focus_mode: bool = False,
    n_simulations: int = 10_000,
    rho: float = 0.15,
) -> dict:
    """
    Correlated Monte Carlo simulation using a Gaussian copula.

    Sports are not fully independent: shared factors (delegation quality,
    travel conditions, funding shocks) induce mild positive correlation.
    Fat-tail shocks capture the observed variance in small-program outcomes
    (Lithuania ranged 1–5 medals across Games — wider than independent Bernoulli implies).

    Parameters
    ----------
    rho : float
        Cross-sport correlation coefficient (0 = independent, 1 = perfectly correlated).
        0.15 is conservative: a "good Lithuania Games" lifts all sports modestly.
    """
    sport_probs = compute_medal_probs(
        funding_multiplier, athletes_sent, selected_sports, focus_mode
    )

    sports   = list(sport_probs.keys())
    n_sports = len(sports)
    probs    = np.array([sport_probs[s]["medal_probability"] for s in sports])

    rng = np.random.default_rng(42)

    # Gaussian copula: correlated standard normals -> correlated uniform -> Bernoulli
    cov = np.full((n_sports, n_sports), rho)
    np.fill_diagonal(cov, 1.0)
    L = np.linalg.cholesky(cov)  # Cholesky factor

    from scipy.stats import norm

    # Fat-tail shock distribution: occasionally everything goes very well or very badly.
    # Calibrated so that Lithuania's observed range (1–5 medals) is plausible.
    SHOCK_VALS = np.array([0.55, 0.80, 1.00, 1.00, 1.20, 1.50])
    SHOCK_PROB = np.array([0.08, 0.12, 0.40, 0.20, 0.12, 0.08])

    total_sim  = np.zeros(n_simulations, dtype=float)
    draws_mat  = np.zeros((n_simulations, n_sports), dtype=float)

    Z = (L @ rng.standard_normal((n_sports, n_simulations))).T  # (n_sim, n_sports)
    U = norm.cdf(Z)  # correlated uniforms

    shocks = rng.choice(SHOCK_VALS, size=n_simulations, p=SHOCK_PROB)

    for i in range(n_simulations):
        p_adj = np.clip(probs * shocks[i], 0.0, 0.95)
        medals = (U[i] < p_adj).astype(float)
        draws_mat[i]  = medals
        total_sim[i]  = medals.sum()

    sport_sims = {s: float(draws_mat[:, i].mean()) for i, s in enumerate(sports)}

    return {
        "expected_total":  float(np.mean(total_sim)),
        "median_total":    float(np.median(total_sim)),
        "p10":             float(np.percentile(total_sim, 10)),
        "p25":             float(np.percentile(total_sim, 25)),
        "p75":             float(np.percentile(total_sim, 75)),
        "p90":             float(np.percentile(total_sim, 90)),
        "std":             float(np.std(total_sim)),
        "zero_medal_prob": float((total_sim == 0).mean()),
        "sim_distribution":total_sim.tolist(),
        "per_sport":       sport_probs,
        "sport_win_rates": sport_sims,
    }


# ---------------------------------------------------------------------------
# PEER BENCHMARKS (similar small European nations for context)
# ---------------------------------------------------------------------------
PEER_COUNTRIES = {
    "Estonia":  {"iso3": "EST", "population": 1_300_000, "gdp_pc": 27000, "paris_2024_medals": 3},
    "Latvia":   {"iso3": "LVA", "population": 1_800_000, "gdp_pc": 21000, "paris_2024_medals": 3},
    "Slovenia": {"iso3": "SVN", "population": 2_100_000, "gdp_pc": 30000, "paris_2024_medals": 2},
    "Croatia":  {"iso3": "HRV", "population": 3_900_000, "gdp_pc": 20000, "paris_2024_medals": 10},
    "Slovakia": {"iso3": "SVK", "population": 5_400_000, "gdp_pc": 22000, "paris_2024_medals": 2},
}


if __name__ == "__main__":
    print("=== Lithuania LA 2028 Baseline Prediction (data-driven) ===")
    result = predict_total_medals(funding_multiplier=1.0, athletes_sent=50)
    print(f"Expected medals: {result['expected_total']:.1f}")
    print(f"Range (p10-p90): {result['p10']:.1f} - {result['p90']:.1f}")
    print(f"Zero-medal probability: {result['zero_medal_prob']:.1%}")
    print()
    print(f"{'Sport':30s}  {'Prob':>5}  {'Hist rate':>9}  {'Medal years'}")
    print("-" * 80)
    for sport, data in result["per_sport"].items():
        yrs = str(data["medal_years"]) if data["medal_years"] else "none"
        print(f"  {sport:28s}  {data['medal_probability']:>4.0%}  "
              f"{data['historical_win_rate']:>8.0%}  {yrs}")
    print()
    print("=== Scenario: Double funding + focus on top 4 sports ===")
    r2 = predict_total_medals(
        funding_multiplier=2.0, athletes_sent=60,
        selected_sports=["Athletics", "Rowing", "Swimming", "3x3 Basketball"],
        focus_mode=True
    )
    print(f"Expected medals: {r2['expected_total']:.1f}  "
          f"(p10={r2['p10']:.1f}, p90={r2['p90']:.1f})")
