"""
Trains the Olympic medal prediction model (v2 — improved accuracy).

Key improvements over v1:
  - XGBoost replaces Random Forest (better on tabular data)
  - medal_trend feature: 2-cycle momentum delta
  - gdp_growth_rate: captures rising/falling economies
  - athletes_sent_trend: change in delegation size
  - host_multiplier: calibrated from historical data (~1.5x) instead of binary flag
  - prev_total_medals is now supplemented by a 3-cycle rolling mean (smoother baseline)
  - Deduplication of duplicate year rows (Tokyo dataset issue)

Outputs:
  model/medal_classifier.pkl
  model/gold_regressor.pkl
  model/silver_regressor.pkl
  model/bronze_regressor.pkl
  model/total_medals_regressor.pkl
  model/feature_names.json
  model/model_metrics.json
  model/host_multiplier.json
"""

import os, json
import numpy as np
import pandas as pd
import joblib
import warnings
warnings.filterwarnings("ignore")

from xgboost import XGBRegressor, XGBClassifier
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.model_selection import LeaveOneGroupOut, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error

ROOT   = os.path.join(os.path.dirname(__file__), "..")
DATA   = os.path.join(ROOT, "data", "processed", "training_frame.csv")
OUTDIR = os.path.dirname(__file__)

# ---------------------------------------------------------------------------
# 1. LOAD & DEDUPLICATE
# ---------------------------------------------------------------------------
print("Loading data...")
df = pd.read_csv(DATA)

# Remove duplicate edition rows (Tokyo 2020 dataset had same country appearing twice
# because the source dataset included both Tokyo and Paris under year 2020)
df = df.drop_duplicates(subset=["iso3", "year", "noc"], keep="first")
print(f"  Rows after deduplication: {len(df)}")

# ---------------------------------------------------------------------------
# 2. HOST EFFECT — calibrate multiplier from historical data
# ---------------------------------------------------------------------------
HOST_MAP = {
    1960:"ITA",1964:"JPN",1968:"MEX",1972:"DEU",1976:"CAN",
    1980:"RUS",1984:"USA",1988:"KOR",1992:"ESP",1996:"USA",
    2000:"AUS",2004:"GRC",2008:"CHN",2012:"GBR",2016:"BRA",
    2020:"JPN",2024:"FRA",
}
df["host"] = df.apply(lambda r: 1 if HOST_MAP.get(r["year"],"") == r["iso3"] else 0, axis=1)

# Size-stratified host multiplier: small programs get bigger relative boosts
df_sorted = df.sort_values(["iso3","year"])
df_sorted["_prev"] = df_sorted.groupby("iso3")["total_medals"].shift(1)
host_rows = df_sorted[(df_sorted["host"]==1) & (df_sorted["_prev"] > 0)].copy()
host_rows["_mult"] = (host_rows["total_medals"] / host_rows["_prev"]).clip(upper=6.0)

small  = float(host_rows[host_rows["_prev"] <= 15]["_mult"].median())
medium = float(host_rows[(host_rows["_prev"] > 15) & (host_rows["_prev"] <= 45)]["_mult"].median())
large  = float(host_rows[host_rows["_prev"] > 45]["_mult"].median())
# Fallback if any bucket is empty
if np.isnan(small):  small  = 2.5
if np.isnan(medium): medium = 1.5
if np.isnan(large):  large  = 1.3

print(f"  Host multipliers — small:{small:.2f}x  medium:{medium:.2f}x  large:{large:.2f}x")

with open(os.path.join(OUTDIR, "host_multiplier.json"), "w") as f:
    json.dump({"small": small, "medium": medium, "large": large,
               "small_thresh": 15, "large_thresh": 45}, f)

# ---------------------------------------------------------------------------
# 3. FEATURE ENGINEERING
# ---------------------------------------------------------------------------
print("Engineering features...")
df = df.sort_values(["iso3","year"])

# Log transforms
df["log_population"]     = np.log1p(df["population"])
df["log_gdp_per_capita"] = np.log1p(df["gdp_per_capita"])

# Lagged medals
df["prev_total_medals"]  = df.groupby("iso3")["total_medals"].shift(1)
df["prev_gold"]          = df.groupby("iso3")["gold"].shift(1)
df["prev2_total_medals"] = df.groupby("iso3")["total_medals"].shift(2)

# 3rd lag
df["prev3_total_medals"] = df.groupby("iso3")["total_medals"].shift(3)

# Momentum: 2-cycle trend (positive = rising program)
df["medal_trend"]        = df["prev_total_medals"] - df["prev2_total_medals"]

# 3-cycle rolling mean (smoothed baseline)
df["rolling_mean_medals"] = (
    df.groupby("iso3")["total_medals"]
    .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
)

# Log of previous medals (handles scale better)
df["log_prev_total"] = np.log1p(df["prev_total_medals"])

# GDP growth rate (captures surging economies / investment capacity)
df["gdp_growth_rate"] = df.groupby("iso3")["gdp_per_capita"].pct_change()
df["gdp_growth_rate"] = df["gdp_growth_rate"].clip(-0.5, 1.0)  # winsorise

# Athletes sent — compute from bio file and Paris 2024 athletes file
bio = pd.read_csv(os.path.join(ROOT, "data/raw/kaggle/olympics_historical/Olympic_Athlete_Event_Results.csv"))
games = pd.read_csv(os.path.join(ROOT, "data/raw/kaggle/olympics_historical/Olympics_Games.csv"))
games_summer = games[games["edition"].str.contains("Summer")][["edition_id", "year"]]
ath_country = (
    bio.groupby(["edition_id", "country_noc"])["athlete_id"]
    .nunique().reset_index()
    .rename(columns={"athlete_id": "athletes_sent", "country_noc": "noc"})
    .merge(games_summer, on="edition_id", how="left")
)
df = df.merge(ath_country[["noc", "year", "athletes_sent"]], on=["noc", "year"], how="left")

# Paris 2024
ath_2024 = pd.read_csv(os.path.join(ROOT, "data/raw/kaggle/paris_2024/athletes.csv"))
if "country_code" in ath_2024.columns:
    cnt_2024 = ath_2024.groupby("country_code").size().reset_index(name="athletes_2024")
    cnt_2024 = cnt_2024.rename(columns={"country_code": "noc"})
    for _, row in cnt_2024.iterrows():
        mask = (df["year"] == 2024) & (df["noc"] == row["noc"]) & df["athletes_sent"].isna()
        df.loc[mask, "athletes_sent"] = row["athletes_2024"]

df["athletes_sent"] = df.groupby("year")["athletes_sent"].transform(
    lambda x: x.fillna(x.median())
)

# Athletes sent trend
df["athletes_sent_prev"]  = df.groupby("iso3")["athletes_sent"].shift(1)
df["athletes_sent_trend"] = df["athletes_sent"] - df["athletes_sent_prev"]

# Efficiency: medals per athlete — must be after athletes_sent is populated
df["medals_per_athlete"] = (
    df["prev_total_medals"] / df["athletes_sent"].replace(0, np.nan)
).clip(upper=2.0)

# Years since first Olympics (experience / program maturity)
df["first_year"] = df.groupby("iso3")["year"].transform("min")
df["years_experience"] = df["year"] - df["first_year"]

# Host flag (will be post-multiplied, but kept as feature too)
# Upcoming host (T+1 = this edition is 4 years before hosting — countries invest more)
next_hosts = {v - 4: v for v in HOST_MAP.keys()}
df["upcoming_host"] = df.apply(
    lambda r: 1 if next_hosts.get(r["year"],"") != "" and HOST_MAP.get(next_hosts.get(r["year"],0),"") == r["iso3"] else 0,
    axis=1
)

# ---------------------------------------------------------------------------
# 4. FEATURE LIST
# ---------------------------------------------------------------------------
FEATURES = [
    "log_gdp_per_capita",
    "log_population",
    "gdp_growth_rate",
    "hdi",
    "eurostat_recreation_pct_gdp",
    "wvs_national_pride",
    "wvs_interpersonal_trust",
    "ess_social_trust",
    "ess_trust_parliament",
    "host",
    "upcoming_host",
    "prev_total_medals",
    "log_prev_total",
    "prev_gold",
    "prev2_total_medals",
    "prev3_total_medals",
    "medal_trend",
    "rolling_mean_medals",
    "medals_per_athlete",
    "athletes_sent",
    "athletes_sent_trend",
    "years_experience",
]

TARGETS = ["gold", "silver", "bronze", "total_medals"]

model_df = df.dropna(subset=["prev_total_medals", "log_gdp_per_capita"]).copy()
print(f"  Training rows: {len(model_df)}")

X      = model_df[FEATURES]
groups = model_df["year"]

# ---------------------------------------------------------------------------
# 5. MODEL — XGBoost + RF Ensemble
# ---------------------------------------------------------------------------
def make_xgb_pipeline(target_mean=None):
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", XGBRegressor(
            n_estimators=700,
            max_depth=4,
            learning_rate=0.03,
            subsample=0.75,
            colsample_bytree=0.75,
            min_child_weight=4,
            reg_alpha=0.2,
            reg_lambda=2.0,
            gamma=0.1,
            random_state=42,
            n_jobs=-1,
            verbosity=0,
        )),
    ])

def make_rf_pipeline():
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestRegressor(
            n_estimators=300, max_depth=10, min_samples_leaf=2,
            random_state=42, n_jobs=-1
        )),
    ])

# ---------------------------------------------------------------------------
# 6. TRAIN + CROSS-VALIDATE
# ---------------------------------------------------------------------------
logo     = LeaveOneGroupOut()
regressors = {}
metrics    = {}

medal_df = model_df[model_df["total_medals"] > 0].copy()
Xm       = medal_df[FEATURES]
groups_m = medal_df["year"]

from sklearn.metrics import mean_absolute_error as sk_mae

for target in TARGETS:
    print(f"\nTraining: {target}...")
    y_raw = medal_df[target]
    y_log = np.log1p(y_raw)  # log-transform: reduces influence of large programs

    xgb = make_xgb_pipeline()
    rf  = make_rf_pipeline()

    # CV with back-transformation to get MAE in original medal units
    def logo_cv_mae(pipe, y_tr):
        maes = []
        for tr, te in logo.split(Xm, y_tr, groups_m):
            p = Pipeline(pipe.steps)
            p.fit(Xm.iloc[tr], y_tr.iloc[tr])
            pred_log = p.predict(Xm.iloc[te])
            pred_raw = np.maximum(0, np.expm1(pred_log))
            maes.append(sk_mae(y_raw.iloc[te], pred_raw))
        return np.array(maes)

    mae_xgb = logo_cv_mae(xgb, y_log)
    mae_rf  = logo_cv_mae(rf,  y_log)
    print(f"  XGB  MAE={mae_xgb.mean():.3f} (log-trained, back-transformed)")
    print(f"  RF   MAE={mae_rf.mean():.3f}")

    # Fit both on full log-transformed target
    xgb.fit(Xm, y_log)
    rf.fit(Xm, y_log)

    w_xgb   = 1 / max(mae_xgb.mean(), 0.01)
    w_rf    = 1 / max(mae_rf.mean(),  0.01)
    total_w = w_xgb + w_rf

    regressors[target] = {"xgb": xgb, "rf": rf,
                           "w_xgb": w_xgb/total_w, "w_rf": w_rf/total_w,
                           "log_transformed": True}

    best_mae = min(mae_xgb.mean(), mae_rf.mean())
    metrics[target] = {
        "xgb_cv_mae": float(mae_xgb.mean()), "rf_cv_mae": float(mae_rf.mean()),
        "best_mae": float(best_mae), "w_xgb": float(w_xgb/total_w), "w_rf": float(w_rf/total_w),
    }

# ---------------------------------------------------------------------------
# 7. FEATURE IMPORTANCE
# ---------------------------------------------------------------------------
print("\n--- XGBoost feature importances (total_medals) ---")
xgb_model = regressors["total_medals"]["xgb"].named_steps["model"]
imps = pd.Series(xgb_model.feature_importances_, index=FEATURES).sort_values(ascending=False)
for feat, imp in imps.items():
    print(f"  {feat:35s} {imp:.4f}")

# ---------------------------------------------------------------------------
# 8. SAVE
# ---------------------------------------------------------------------------
for target, reg_dict in regressors.items():
    joblib.dump(reg_dict, os.path.join(OUTDIR, f"{target}_regressor.pkl"))

with open(os.path.join(OUTDIR, "feature_names.json"), "w") as f:
    json.dump(FEATURES, f, indent=2)

with open(os.path.join(OUTDIR, "model_metrics.json"), "w") as f:
    json.dump(metrics, f, indent=2)

# Save enriched frame
enriched_path = os.path.join(ROOT, "data/processed/training_frame_enriched.csv")
df.to_csv(enriched_path, index=False)

print("\n=== FINAL METRICS ===")
for t, m in metrics.items():
    print(f"  {t:15s}  best MAE={m['best_mae']:.3f}  (XGB w={m['w_xgb']:.2f}, RF w={m['w_rf']:.2f})")
print("\nAll models saved.")
