"""
Builds the unified country x olympic_year training frame.

Output: data/processed/training_frame.csv

Columns:
  country_noc, country_name, year, edition,
  gold, silver, bronze, total_medals,
  gdp_per_capita, population, gni_per_capita,
  hdi,
  eurostat_recreation_pct_gdp,
  wvs_social_trust, wvs_national_pride, wvs_institutional_trust, wvs_civic_participation,
  ess_social_trust, ess_institutional_trust, ess_civic_interest
"""

import os
import glob
import pandas as pd
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW  = os.path.join(ROOT, "data", "raw")
OUT  = os.path.join(ROOT, "data", "processed")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# NOC -> ISO3 mapping (Olympic codes -> World Bank / UN codes)
# ---------------------------------------------------------------------------
NOC_TO_ISO3 = {
    "AFG":"AFG","ALB":"ALB","ALG":"DZA","AND":"AND","ANG":"AGO","ANT":"ATG",
    "ARG":"ARG","ARM":"ARM","ARU":"ABW","ASA":"ASM","AUS":"AUS","AUT":"AUT",
    "AZE":"AZE","BAH":"BHS","BAN":"BGD","BAR":"BRB","BDI":"BDI","BEL":"BEL",
    "BEN":"BEN","BER":"BMU","BHU":"BTN","BIH":"BIH","BIZ":"BLZ","BLR":"BLR",
    "BOL":"BOL","BOT":"BWA","BRA":"BRA","BRN":"BRN","BUL":"BGR","BUR":"BFA",
    "CAF":"CAF","CAM":"KHM","CAN":"CAN","CAY":"CYM","CGO":"COG","CHA":"TCD",
    "CHI":"CHL","CHN":"CHN","CIV":"CIV","CMR":"CMR","COD":"COD","COK":"COK",
    "COL":"COL","COM":"COM","CPV":"CPV","CRC":"CRI","CRO":"HRV","CUB":"CUB",
    "CYP":"CYP","CZE":"CZE","DEN":"DNK","DJI":"DJI","DMA":"DMA","DOM":"DOM",
    "ECU":"ECU","EGY":"EGY","ERI":"ERI","ESA":"SLV","ESP":"ESP","EST":"EST",
    "ETH":"ETH","FIJ":"FJI","FIN":"FIN","FRA":"FRA","FSM":"FSM","GAB":"GAB",
    "GAM":"GMB","GBR":"GBR","GBS":"GNB","GEO":"GEO","GEQ":"GNQ","GER":"DEU",
    "GHA":"GHA","GRE":"GRC","GRN":"GRD","GUA":"GTM","GUI":"GIN","GUM":"GUM",
    "GUY":"GUY","HAI":"HTI","HKG":"HKG","HON":"HND","HUN":"HUN","INA":"IDN",
    "IND":"IND","IRI":"IRN","IRL":"IRL","IRQ":"IRQ","ISL":"ISL","ISR":"ISR",
    "ISV":"VIR","ITA":"ITA","IVB":"VGB","JAM":"JAM","JOR":"JOR","JPN":"JPN",
    "KAZ":"KAZ","KEN":"KEN","KGZ":"KGZ","KIR":"KIR","KOR":"KOR","KOS":"XKX",
    "KSA":"SAU","KUW":"KWT","LAO":"LAO","LAT":"LVA","LBA":"LBY","LBR":"LBR",
    "LCA":"LCA","LES":"LSO","LIB":"LBN","LIE":"LIE","LIT":"LTU","LTU":"LTU","LUX":"LUX",
    "MAD":"MDG","MAR":"MAR","MAS":"MYS","MAW":"MWI","MDA":"MDA","MDV":"MDV",
    "MEX":"MEX","MGL":"MNG","MKD":"MKD","MLI":"MLI","MLT":"MLT","MNE":"MNE",
    "MON":"MCO","MOZ":"MOZ","MRI":"MUS","MTN":"MRT","MYA":"MMR","NAM":"NAM",
    "NCA":"NIC","NED":"NLD","NEP":"NPL","NGR":"NGA","NIG":"NER","NOR":"NOR",
    "NRU":"NRU","NZL":"NZL","OMA":"OMN","PAK":"PAK","PAN":"PAN","PAR":"PRY",
    "PER":"PER","PHI":"PHL","PLE":"PSE","PLW":"PLW","PNG":"PNG","POL":"POL",
    "POR":"PRT","PRK":"PRK","PUR":"PRI","QAT":"QAT","ROC":"TWN","ROT":"---",
    "ROU":"ROU","RSA":"ZAF","RUS":"RUS","RWA":"RWA","SAM":"WSM","SEN":"SEN",
    "SEY":"SYC","SGP":"SGP","SKN":"KNA","SLE":"SLE","SLO":"SVN","SMR":"SMR",
    "SOL":"SLB","SOM":"SOM","SRB":"SRB","SRI":"LKA","SSD":"SSD","STP":"STP",
    "SUD":"SDN","SUI":"CHE","SUR":"SUR","SVK":"SVK","SWE":"SWE","SWZ":"SWZ",
    "SYR":"SYR","TAN":"TZA","TGA":"TON","THA":"THA","TJK":"TJK","TKM":"TKM",
    "TLS":"TLS","TOG":"TGO","TPE":"TWN","TTO":"TTO","TUN":"TUN","TUR":"TUR",
    "TUV":"TUV","UAE":"ARE","UGA":"UGA","UKR":"UKR","URU":"URY","USA":"USA",
    "UZB":"UZB","VAN":"VUT","VEN":"VEN","VIE":"VNM","VIN":"VCT","YEM":"YEM",
    "ZAM":"ZMB","ZIM":"ZWE",
    # Historical / unified teams
    "URS":"RUS","EUN":"RUS","TCH":"CZE","YUG":"SRB","FRG":"DEU","GDR":"DEU",
    "BOH":"CZE","ANZ":"AUS","IOA":"---","EOR":"---","ROC":"RUS",
}

# ---------------------------------------------------------------------------
# 1. OLYMPIC MEDAL TALLIES
# ---------------------------------------------------------------------------
print("Loading Olympic medal tallies...")

# Historical 1896-2022
hist = pd.read_csv(os.path.join(RAW, "kaggle/olympics_historical/Olympic_Games_Medal_Tally.csv"))
hist = hist.rename(columns={"country_noc": "noc", "country": "country_name"})
hist = hist[["edition", "year", "noc", "country_name", "gold", "silver", "bronze", "total"]]
hist = hist[hist["edition"].str.contains("Summer")]  # Summer only

# NOTE: the tokyo_2020 Kaggle folder is actually Paris 2024 data (identical files).
# Real Tokyo 2020 results are already in the Olympedia historical dataset above.
# Do NOT add tok here.

# Paris 2024
par = pd.read_csv(os.path.join(RAW, "kaggle/paris_2024/medals_total.csv"))
par = par.rename(columns={
    "country_code": "noc", "country": "country_name",
    "Gold Medal": "gold", "Silver Medal": "silver",
    "Bronze Medal": "bronze", "Total": "total"
})
par["year"] = 2024
par["edition"] = "2024 Summer Olympics"
par = par[["edition", "year", "noc", "country_name", "gold", "silver", "bronze", "total"]]

medals = pd.concat([hist, par], ignore_index=True)
medals["iso3"] = medals["noc"].map(NOC_TO_ISO3)
print(f"  {len(medals):,} rows, {medals['year'].nunique()} Olympic editions")

# ---------------------------------------------------------------------------
# 2. WORLD BANK — GDP, POPULATION, GNI
# ---------------------------------------------------------------------------
print("Loading World Bank data...")

def load_wb(filename, value_col):
    df = pd.read_csv(os.path.join(RAW, "world_bank", filename))
    df = df.rename(columns={"value": value_col})
    df["year"] = df["year"].astype(int)
    return df[["country_iso3", "year", value_col]].dropna(subset=[value_col])

gdp = load_wb("gdp_per_capita.csv", "gdp_per_capita")
pop = load_wb("population.csv", "population")
gni = load_wb("gni_per_capita.csv", "gni_per_capita")

wb = gdp.merge(pop, on=["country_iso3", "year"], how="outer")
wb = wb.merge(gni, on=["country_iso3", "year"], how="outer")
print(f"  {len(wb):,} country-year rows")

# ---------------------------------------------------------------------------
# 3. UNDP HDI
# ---------------------------------------------------------------------------
print("Loading UNDP HDI...")

hdi_raw = pd.read_excel(
    os.path.join(RAW, "undp/hdi_trends.xlsx"),
    header=None, skiprows=4
)
# Row 0 is the year header, actual data starts after
# Columns: HDI rank, Country, 1990, nan, 2000, nan, 2010, nan, 2015, nan, 2019, nan, 2020, nan, 2021, nan, 2022...
year_cols = [1990, 2000, 2010, 2015, 2019, 2020, 2021, 2022]
col_indices = [0, 1, 2, 4, 6, 8, 10, 12, 14, 16]  # rank, country, then every other col

hdi_sub = hdi_raw.iloc[:, col_indices].copy()
hdi_sub.columns = ["hdi_rank", "country"] + year_cols
hdi_sub = hdi_sub.dropna(subset=["country"])
hdi_sub = hdi_sub[hdi_sub["country"].astype(str).str.strip() != ""]
hdi_sub = hdi_sub[~hdi_sub["country"].astype(str).str.isupper()]  # drop section headers

# Melt to long format
hdi_long = hdi_sub.melt(
    id_vars=["country"], value_vars=year_cols,
    var_name="year", value_name="hdi"
).dropna(subset=["hdi"])
hdi_long["year"] = hdi_long["year"].astype(int)
hdi_long["hdi"] = pd.to_numeric(hdi_long["hdi"], errors="coerce")
hdi_long = hdi_long.dropna(subset=["hdi"])

# Country name -> ISO3 via fuzzy match using country_name from World Bank
wb_names = gdp[["country_iso3"]].drop_duplicates()
# Simple manual map for key mismatches
HDI_NAME_MAP = {
    "Korea (Republic of)": "KOR", "Iran (Islamic Republic of)": "IRN",
    "Bolivia (Plurinational State of)": "BOL", "Congo (Democratic Republic of the)": "COD",
    "Tanzania (United Republic of)": "TZA", "Venezuela (Bolivarian Republic of)": "VEN",
    "Viet Nam": "VNM", "Syrian Arab Republic": "SYR", "Lao People's Democratic Republic": "LAO",
    "Micronesia (Federated States of)": "FSM", "Moldova (Republic of)": "MDA",
    "Palestine, State of": "PSE", "Hong Kong, China (SAR)": "HKG",
    "Czechia": "CZE", "Eswatini (Kingdom of)": "SWZ",
    "Cabo Verde": "CPV", "Turkiye": "TUR",
}
hdi_long["iso3"] = hdi_long["country"].map(HDI_NAME_MAP)

# For unmapped, use pycountry-style match via wb country names
wb_name_iso = (
    gdp.drop_duplicates("country_iso3")
    .set_index("country_iso3")
    .reset_index()
)
# Build reverse lookup from wb names
from difflib import get_close_matches
wb_name_dict = {}
for _, row in wb_name_iso.iterrows():
    wb_name_dict[row.get("country_name", "").lower() if "country_name" in row else ""] = row["country_iso3"]

# Load wb country names properly
gdp_names = pd.read_csv(os.path.join(RAW, "world_bank/gdp_per_capita.csv"))
wb_lookup = gdp_names.drop_duplicates("country_iso3")[["country_iso3","country_name"]]
wb_name_to_iso = dict(zip(wb_lookup["country_name"].str.lower(), wb_lookup["country_iso3"]))

def name_to_iso3(name):
    if pd.isna(name):
        return None
    key = str(name).lower()
    if key in wb_name_to_iso:
        return wb_name_to_iso[key]
    matches = get_close_matches(key, wb_name_to_iso.keys(), n=1, cutoff=0.85)
    return wb_name_to_iso[matches[0]] if matches else None

mask = hdi_long["iso3"].isna()
hdi_long.loc[mask, "iso3"] = hdi_long.loc[mask, "country"].apply(name_to_iso3)

hdi_long = hdi_long.dropna(subset=["iso3"])
print(f"  {len(hdi_long):,} HDI country-year rows")

# ---------------------------------------------------------------------------
# 4. EUROSTAT — Recreation/Sport expenditure % of GDP
# ---------------------------------------------------------------------------
print("Loading Eurostat data...")

euro = pd.read_csv(os.path.join(RAW, "eurostat/gov_expenditure_cofog_gf08.csv"))
euro = euro.rename(columns={"country_code": "eurostat_code", "year": "year",
                             "recreation_pct_gdp": "eurostat_recreation_pct_gdp"})
euro["year"] = euro["year"].astype(int)
euro = euro.dropna(subset=["eurostat_recreation_pct_gdp"])

# Eurostat 2-letter -> ISO3
EU_CODE_MAP = {
    "AT":"AUT","BE":"BEL","BG":"BGR","CY":"CYP","CZ":"CZE","DE":"DEU",
    "DK":"DNK","EE":"EST","EL":"GRC","ES":"ESP","FI":"FIN","FR":"FRA",
    "HR":"HRV","HU":"HUN","IE":"IRL","IT":"ITA","LT":"LTU","LU":"LUX",
    "LV":"LVA","MT":"MLT","NL":"NLD","PL":"POL","PT":"PRT","RO":"ROU",
    "SE":"SWE","SI":"SVN","SK":"SVK","IS":"ISL","LI":"LIE","NO":"NOR",
    "CH":"CHE","UK":"GBR","RS":"SRB","TR":"TUR","ME":"MNE","MK":"MKD",
    "AL":"ALB","BA":"BIH","XK":"XKX","UA":"UKR","MD":"MDA","AM":"ARM",
    "AZ":"AZE","GE":"GEO","BY":"BLR",
}
euro["iso3"] = euro["eurostat_code"].map(EU_CODE_MAP)
euro = euro.dropna(subset=["iso3"])
print(f"  {len(euro):,} Eurostat rows")

# ---------------------------------------------------------------------------
# 5. WVS WAVE 7 — Social capital variables
# ---------------------------------------------------------------------------
print("Loading WVS Wave 7...")

wvs = pd.read_csv(os.path.join(RAW, "wvs/WVS_Cross-National_Wave_7_csv_v6_0.csv"),
                  low_memory=False)

# Key variables (WVS Wave 7 codebook):
# Q57  = Most people can be trusted (1=yes, 2=no)
# Q71  = Confidence in government
# Q72  = Confidence in political parties
# Q131 = National pride (1=very proud ... 4=not proud)
# Q209 = Active membership sport/recreation org (0=no, 1=yes)
wvs_vars = {
    "B_COUNTRY_ALPHA": "country_alpha",
    "A_YEAR": "year",
    "Q57": "wvs_interpersonal_trust",    # most people can be trusted
    "Q71": "wvs_confidence_govt",        # confidence in government
    "Q72": "wvs_confidence_parties",     # confidence in political parties
    "Q131": "wvs_national_pride",        # national pride
    "Q209": "wvs_sport_org_membership",  # active in sport/rec org
}

available = {k: v for k, v in wvs_vars.items() if k in wvs.columns}
wvs_sub = wvs[list(available.keys())].rename(columns=available)

# Recode: replace negative values (missing codes -1, -2, -3, -4, -5) with NaN
for col in wvs_sub.columns[2:]:
    wvs_sub[col] = pd.to_numeric(wvs_sub[col], errors="coerce")
    wvs_sub.loc[wvs_sub[col] < 0, col] = np.nan

# Invert pride scale (1=very proud -> 4=not proud) so higher = more proud
if "wvs_national_pride" in wvs_sub.columns:
    wvs_sub["wvs_national_pride"] = 5 - wvs_sub["wvs_national_pride"]

# Aggregate to country level (mean across all respondents)
wvs_agg = wvs_sub.groupby("country_alpha").mean(numeric_only=True).reset_index()
wvs_agg = wvs_agg.rename(columns={"country_alpha": "wvs_country"})
wvs_agg["survey_year"] = wvs_agg["year"].round().astype(int)
wvs_agg = wvs_agg.drop(columns=["year"])

# Map WVS country alpha -> ISO3
WVS_ALPHA_TO_ISO3 = {
    "AND":"AND","ARG":"ARG","ARM":"ARM","AUS":"AUS","AZE":"AZE","BGD":"BGD",
    "BOL":"BOL","BRA":"BRA","BGR":"BGR","CAN":"CAN","CHL":"CHL","CHN":"CHN",
    "COL":"COL","CYP":"CYP","ECU":"ECU","EGY":"EGY","ETH":"ETH","DEU":"DEU",
    "GRC":"GRC","GTM":"GTM","HKG":"HKG","IDN":"IDN","IRN":"IRN","IRQ":"IRQ",
    "KAZ":"KAZ","KEN":"KEN","KGZ":"KGZ","LBN":"LBN","LBY":"LBY","MYS":"MYS",
    "MEX":"MEX","MAR":"MAR","MMR":"MMR","NZL":"NZL","NIC":"NIC","NGA":"NGA",
    "PAK":"PAK","PHL":"PHL","PER":"PER","PRI":"PRI","ROM":"ROU","RUS":"RUS",
    "SRB":"SRB","SLE":"SLE","SVN":"SVN","KOR":"KOR","ESP":"ESP","SWE":"SWE",
    "TWN":"TWN","TJK":"TJK","TZA":"TZA","THA":"THA","TUN":"TUN","TUR":"TUR",
    "UKR":"UKR","USA":"USA","URY":"URY","VNM":"VNM","ZWE":"ZWE",
    "GBR":"GBR","NLD":"NLD","POL":"POL","PRT":"PRT","ROU":"ROU","SVK":"SVK",
    "AUT":"AUT","BEL":"BEL","CZE":"CZE","DNK":"DNK","EST":"EST","FIN":"FIN",
    "FRA":"FRA","HUN":"HUN","IRL":"IRL","ITA":"ITA","LTU":"LTU","LUX":"LUX",
    "LVA":"LVA","MLT":"MLT","HRV":"HRV","MNE":"MNE","MKD":"MKD","ALB":"ALB",
    "BIH":"BIH","ISL":"ISL","NOR":"NOR","CHE":"CHE","JPN":"JPN","IND":"IND",
    "ZAF":"ZAF","SAU":"SAU","QAT":"QAT","ARE":"ARE","JOR":"JOR",
}
wvs_agg["iso3"] = wvs_agg["wvs_country"].map(WVS_ALPHA_TO_ISO3)
wvs_agg = wvs_agg.dropna(subset=["iso3"])
print(f"  {len(wvs_agg)} countries with WVS data")

# ---------------------------------------------------------------------------
# 6. ESS — Social trust and institutional trust
# ---------------------------------------------------------------------------
print("Loading ESS data...")

ess_file = glob.glob(os.path.join(RAW, "ess/*.csv"))[0]
ess = pd.read_csv(ess_file, low_memory=False)

ess_vars = {
    "cntry": "ess_country",
    "essround": "essround",
    "ppltrst": "ess_social_trust",          # most people can be trusted (0-10)
    "trstprl": "ess_trust_parliament",       # trust in parliament (0-10)
    "trstlgl": "ess_trust_legal",            # trust in legal system (0-10)
    "nwspol": "ess_news_politics",           # attention to politics (mins/day)
    "prtprt": "ess_sport_participation",     # participated in sport (yes/no)
}
available_ess = {k: v for k, v in ess_vars.items() if k in ess.columns}
ess_sub = ess[list(available_ess.keys())].rename(columns=available_ess)

# Replace refusal/don't know codes (77,88,99) with NaN
for col in ess_sub.columns[2:]:
    ess_sub[col] = pd.to_numeric(ess_sub[col], errors="coerce")
    ess_sub.loc[ess_sub[col] > 70, col] = np.nan

# ESS round -> approximate year
ESS_ROUND_YEAR = {1:2002, 2:2004, 3:2006, 4:2008, 5:2010, 6:2012, 7:2014, 8:2016, 9:2018, 10:2020, 11:2023}
ess_sub["survey_year"] = ess_sub["essround"].map(ESS_ROUND_YEAR)

# Aggregate to country x round level
ess_agg = ess_sub.groupby(["ess_country", "essround", "survey_year"]).mean(numeric_only=True).reset_index()

# ESS 2-letter country code -> ISO3
ESS_CNTRY_TO_ISO3 = {
    "AT":"AUT","BE":"BEL","BG":"BGR","CH":"CHE","CY":"CYP","CZ":"CZE",
    "DE":"DEU","DK":"DNK","EE":"EST","ES":"ESP","FI":"FIN","FR":"FRA",
    "GB":"GBR","GR":"GRC","HR":"HRV","HU":"HUN","IE":"IRL","IL":"ISR",
    "IS":"ISL","IT":"ITA","LT":"LTU","LU":"LUX","LV":"LVA","ME":"MNE",
    "MK":"MKD","MT":"MLT","NL":"NLD","NO":"NOR","PL":"POL","PT":"PRT",
    "RU":"RUS","SE":"SWE","SI":"SVN","SK":"SVK","TR":"TUR","UA":"UKR",
    "RS":"SRB","AL":"ALB","XK":"XKX","KZ":"KAZ","RO":"ROU",
}
ess_agg["iso3"] = ess_agg["ess_country"].map(ESS_CNTRY_TO_ISO3)
ess_agg = ess_agg.dropna(subset=["iso3"])
print(f"  {ess_agg['iso3'].nunique()} countries, {ess_agg['essround'].nunique()} rounds in ESS")

# ---------------------------------------------------------------------------
# 7. MERGE EVERYTHING
# ---------------------------------------------------------------------------
print("Merging all datasets...")

df = medals.copy()

# 7a. World Bank — match on iso3 + year (exact)
df = df.merge(wb.rename(columns={"country_iso3": "iso3"}),
              on=["iso3", "year"], how="left")

# 7b. HDI — match on iso3 + nearest available year
hdi_pivot = hdi_long.pivot_table(index="iso3", columns="year", values="hdi")
HDI_YEARS = sorted(hdi_long["year"].unique())

def get_hdi(iso3, year):
    if iso3 not in hdi_pivot.index:
        return np.nan
    row = hdi_pivot.loc[iso3]
    # Find closest year with data
    available = [(abs(y - year), y) for y in HDI_YEARS if not pd.isna(row.get(y, np.nan))]
    if not available:
        return np.nan
    return row[min(available)[1]]

df["hdi"] = [get_hdi(iso, yr) for iso, yr in zip(df["iso3"], df["year"])]

# 7c. Eurostat — match on iso3 + year (exact, EU countries only)
euro_merge = euro[["iso3", "year", "eurostat_recreation_pct_gdp"]]
df = df.merge(euro_merge, on=["iso3", "year"], how="left")

# 7d. WVS — match on iso3 (single wave, treat as country-level feature)
wvs_cols = [c for c in wvs_agg.columns if c.startswith("wvs_")]
wvs_merge = wvs_agg[["iso3"] + wvs_cols].drop_duplicates("iso3")
df = df.merge(wvs_merge, on="iso3", how="left")

# 7e. ESS — match on iso3 + nearest ESS survey year
def get_ess_row(iso3, year):
    sub = ess_agg[ess_agg["iso3"] == iso3].copy()
    if sub.empty:
        return pd.Series(dtype=float)
    sub["dist"] = abs(sub["survey_year"] - year)
    return sub.sort_values("dist").iloc[0]

ess_feature_cols = [c for c in ess_agg.columns if c.startswith("ess_") and c != "ess_country"]
ess_rows = df.apply(lambda r: get_ess_row(r["iso3"], r["year"]), axis=1)
for col in ess_feature_cols:
    if col in ess_rows.columns:
        df[col] = ess_rows[col].values

# ---------------------------------------------------------------------------
# 8. CLEAN UP AND SAVE
# ---------------------------------------------------------------------------
df = df.rename(columns={"total": "total_medals"})

# Drop rows with no useful economic data at all
df = df.dropna(subset=["gdp_per_capita", "population"], how="all")

# Sort
df = df.sort_values(["year", "total_medals"], ascending=[True, False])

out_path = os.path.join(OUT, "training_frame.csv")
df.to_csv(out_path, index=False)

print(f"\nDone! Saved -> {out_path}")
print(f"Shape: {df.shape}")
print(f"Years: {sorted(df['year'].unique())}")
print(f"Countries: {df['iso3'].nunique()}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nSample (Lithuania):")
lit = df[df["iso3"] == "LTU"]
if not lit.empty:
    print(lit[["year","gold","silver","bronze","total_medals","gdp_per_capita","population","hdi"]].to_string())
else:
    print("  Lithuania not found in medal data (no medals in Summer Olympics)")
