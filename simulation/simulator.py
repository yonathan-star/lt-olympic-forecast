"""
Simulation engine v2 — ensemble (XGBoost + RF) with calibrated host multiplier.
"""

import os, json
import numpy as np
import pandas as pd
import joblib

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "model")
DATA_DIR  = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

def load_models():
    regressors = {
        t: joblib.load(os.path.join(MODEL_DIR, f"{t}_regressor.pkl"))
        for t in ["gold", "silver", "bronze", "total_medals"]
    }
    with open(os.path.join(MODEL_DIR, "feature_names.json")) as f:
        features = json.load(f)
    with open(os.path.join(MODEL_DIR, "host_multiplier.json")) as f:
        host_cfg = json.load(f)
    return regressors, features, host_cfg

def get_host_multiplier(host_cfg: dict, prev_medals: float) -> float:
    """Return size-stratified host multiplier."""
    if prev_medals <= host_cfg.get("small_thresh", 15):
        return host_cfg["small"]
    elif prev_medals <= host_cfg.get("large_thresh", 45):
        return host_cfg["medium"]
    else:
        return host_cfg["large"]

def load_reference_data():
    return pd.read_csv(os.path.join(DATA_DIR, "training_frame_enriched.csv"))

def get_country_baseline(df: pd.DataFrame, iso3: str) -> dict:
    rows = df[df["iso3"] == iso3].sort_values("year", ascending=False)
    if rows.empty:
        med = df[df["year"] == df["year"].max()]
        return {
            "gdp_per_capita": float(med["gdp_per_capita"].median()),
            "log_gdp_per_capita": float(np.log1p(med["gdp_per_capita"].median())),
            "log_population": float(med["log_population"].median()),
            "gdp_growth_rate": 0.03,
            "hdi": float(med["hdi"].median()),
            "eurostat_recreation_pct_gdp": np.nan,
            "wvs_national_pride": np.nan,
            "wvs_interpersonal_trust": np.nan,
            "ess_social_trust": np.nan,
            "ess_trust_parliament": np.nan,
            "host": 0, "upcoming_host": 0,
            "prev_total_medals": 0, "prev_gold": 0,
            "medal_trend": 0, "rolling_mean_medals": 0,
            "athletes_sent": 20, "athletes_sent_trend": 0,
            "years_experience": 20,
        }

    r  = rows.iloc[0]
    r2 = rows.iloc[1] if len(rows) > 1 else r

    return {
        "gdp_per_capita":              float(r.get("gdp_per_capita", 0) or 0),
        "log_gdp_per_capita":          float(np.log1p(r.get("gdp_per_capita", 0) or 0)),
        "log_population":              float(r.get("log_population", 10) or 10),
        "gdp_growth_rate":             float(r.get("gdp_growth_rate", 0.03) or 0.03),
        "hdi":                         float(r.get("hdi", 0.7) or 0.7),
        "eurostat_recreation_pct_gdp": float(r.get("eurostat_recreation_pct_gdp", np.nan) or np.nan),
        "wvs_national_pride":          float(r.get("wvs_national_pride", np.nan) or np.nan),
        "wvs_interpersonal_trust":     float(r.get("wvs_interpersonal_trust", np.nan) or np.nan),
        "ess_social_trust":            float(r.get("ess_social_trust", np.nan) or np.nan),
        "ess_trust_parliament":        float(r.get("ess_trust_parliament", np.nan) or np.nan),
        "host":                        0,
        "upcoming_host":               0,
        "prev_total_medals":           float(r.get("total_medals", 0) or 0),
        "prev_gold":                   float(r.get("gold", 0) or 0),
        "medal_trend":                 float(r.get("total_medals", 0) - r2.get("total_medals", 0)),
        "rolling_mean_medals":         float(r.get("rolling_mean_medals", r.get("total_medals", 0)) or 0),
        "athletes_sent":               float(r.get("athletes_sent", 30) or 30),
        "athletes_sent_trend":         float(r.get("athletes_sent_trend", 0) or 0),
        "years_experience":            float(r.get("years_experience", 30) or 30),
    }

def _ensemble_predict(reg_dict: dict, X_imp: np.ndarray) -> np.ndarray:
    """Weighted average of XGB and RF tree predictions."""
    xgb_pred = reg_dict["xgb"].named_steps["model"].predict(
        reg_dict["xgb"].named_steps["imputer"].transform(
            pd.DataFrame(X_imp, columns=["f"] * X_imp.shape[1])
        ) if False else X_imp
    )
    rf_trees = reg_dict["rf"].named_steps["model"].estimators_
    rf_preds = np.array([t.predict(X_imp)[0] for t in rf_trees])

    w_xgb = reg_dict["w_xgb"]
    w_rf  = reg_dict["w_rf"]
    # XGB gives single point; RF gives distribution
    # Blend: shift the RF distribution toward XGB mean
    xgb_val = float(xgb_pred[0] if hasattr(xgb_pred, "__len__") else xgb_pred)
    combined = w_xgb * xgb_val + w_rf * rf_preds
    return combined

def build_feature_vector(baseline: dict, sim_params: dict, features: list) -> pd.DataFrame:
    vec = dict(baseline)

    funding_mult = sim_params.get("funding_multiplier", 1.0)
    vec["log_gdp_per_capita"] = float(np.log1p(
        baseline["gdp_per_capita"] * (1 + (funding_mult - 1) * 0.15)
    ))
    vec["gdp_growth_rate"] = baseline["gdp_growth_rate"] + (funding_mult - 1) * 0.02

    if "athletes_sent" in sim_params:
        prev_ath = baseline["athletes_sent"]
        vec["athletes_sent"] = float(sim_params["athletes_sent"])
        vec["athletes_sent_trend"] = float(sim_params["athletes_sent"]) - prev_ath

    if "hdi_delta" in sim_params:
        vec["hdi"] = min(1.0, baseline["hdi"] + sim_params["hdi_delta"])

    vec["host"]         = 1 if sim_params.get("is_host", False) else 0
    vec["upcoming_host"] = 1 if sim_params.get("is_upcoming_host", False) else 0

    if "prev_total_medals_override" in sim_params:
        vec["prev_total_medals"]    = sim_params["prev_total_medals_override"]
        vec["rolling_mean_medals"]  = sim_params["prev_total_medals_override"]
        vec["prev_gold"]            = sim_params.get("prev_gold_override", vec["prev_gold"])

    return pd.DataFrame([{f: vec.get(f, np.nan) for f in features}])

def simulate(iso3: str, sim_params: dict, _cache: dict = {}) -> dict:
    if "regressors" not in _cache:
        _cache["regressors"], _cache["features"], _cache["host_cfg"] = load_models()
        _cache["df"] = load_reference_data()

    regressors = _cache["regressors"]
    features   = _cache["features"]
    host_cfg   = _cache["host_cfg"]
    df         = _cache["df"]

    baseline = get_country_baseline(df, iso3)
    X        = build_feature_vector(baseline, sim_params, features)

    focus_bonus = 1.0 + sim_params.get("sport_focus_bonus", 0.0) * 1.5
    is_host     = sim_params.get("is_host", False)
    host_mult   = get_host_multiplier(host_cfg, baseline["prev_total_medals"]) if is_host else 1.0

    results = {}
    for target, reg_dict in regressors.items():
        imp     = reg_dict["rf"].named_steps["imputer"]
        X_imp   = imp.transform(X)

        tree_preds = _ensemble_predict(reg_dict, X_imp)
        # Back-transform from log space
        tree_preds = np.maximum(0, np.expm1(tree_preds))
        tree_preds = tree_preds * focus_bonus * host_mult

        results[target] = {
            "mean":   float(np.mean(tree_preds)),
            "median": float(np.median(tree_preds)),
            "p10":    float(np.percentile(tree_preds, 10)),
            "p25":    float(np.percentile(tree_preds, 25)),
            "p75":    float(np.percentile(tree_preds, 75)),
            "p90":    float(np.percentile(tree_preds, 90)),
            "std":    float(np.std(tree_preds)),
        }

    medal_prob = min(1.0, results["total_medals"]["mean"] / max(results["total_medals"]["std"], 1))
    medal_prob = min(1.0, medal_prob)

    return {
        "iso3": iso3,
        "medal_probability": medal_prob,
        "predictions": results,
        "baseline": baseline,
        "sim_params": sim_params,
    }

def compare_scenarios(iso3: str, scenarios: list) -> pd.DataFrame:
    rows = []
    for s in scenarios:
        label = s.pop("label", "Scenario")
        result = simulate(iso3, s)
        rows.append({
            "scenario":  label,
            "gold":      round(result["predictions"]["gold"]["mean"], 1),
            "silver":    round(result["predictions"]["silver"]["mean"], 1),
            "bronze":    round(result["predictions"]["bronze"]["mean"], 1),
            "total":     round(result["predictions"]["total_medals"]["mean"], 1),
            "gold_p10":  round(result["predictions"]["gold"]["p10"], 1),
            "gold_p90":  round(result["predictions"]["gold"]["p90"], 1),
            "total_p10": round(result["predictions"]["total_medals"]["p10"], 1),
            "total_p90": round(result["predictions"]["total_medals"]["p90"], 1),
            "medal_prob":round(result["medal_probability"], 3),
        })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    print("Lithuania baseline simulation...")
    r = simulate("LTU", {"funding_multiplier": 1.0, "athletes_sent": 40,
                          "hdi_delta": 0.0, "is_host": False, "sport_focus_bonus": 0.0})
    print(f"Medal probability: {r['medal_probability']:.1%}")
    for t, v in r["predictions"].items():
        print(f"  {t:15s}: {v['mean']:.1f}  (p10={v['p10']:.1f}, p90={v['p90']:.1f})")
