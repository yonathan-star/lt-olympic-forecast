# Manual Downloads Required

These datasets require registration or manual steps. Place files in the indicated folders.

---

## 1. World Values Survey — Wave 7
**Folder:** `data/raw/wvs/`
**Steps:**
1. Go to: https://www.worldvaluessurvey.org/WVSDocumentationWV7.jsp
2. Register (free, instant)
3. Download: **"WVS Cross-National Wave 7 csv v6.0.zip"**
4. Extract and place `WVS_Cross-National_Wave_7_csv_v6_0.csv` in `data/raw/wvs/`

**What it contains:** National pride, trust, civic participation, values — ~80 countries.

---

## 2. European Social Survey (ESS) — Rounds 1–11
**Folder:** `data/raw/ess/`
**Steps:**
1. Go to: https://ess.sikt.no/en/
2. Register (free)
3. Download the **integrated cumulative file** (ESS Rounds 1–11, all countries, CSV)
4. Place in `data/raw/ess/`

**What it contains:** Sport participation rates, national identity, institutional trust — EU countries.

---

## 3. SPLISS 2.0 Policy Data
**Folder:** `data/raw/spliss/`
**Steps:**
1. Download the report PDF: https://ussa-my.com/assets/SPLISS_report.pdf
2. The data tables (country scores by pillar) need to be manually extracted
3. Save as `data/raw/spliss/spliss_country_scores.csv` with columns:
   `country, pillar_1_funding, pillar_2_governance, pillar_3_participation, pillar_4_talent, pillar_5_athletic_career, pillar_6_training_facilities, pillar_7_coaching, pillar_8_competition, pillar_9_research`

**What it contains:** Elite sport policy scores for 15 nations (including benchmarks for Lithuania comparison).

---

## 4. UNDP HDI (if auto-download failed)
**Folder:** `data/raw/undp/`
**Steps:**
1. Go to: https://hdr.undp.org/data-center/documentation-and-downloads
2. Download "Human Development Index and components" → Excel/CSV
3. Download "HDI Trends" table (gives all years 1990–present)
4. Place both files in `data/raw/undp/`

---

## Status Checklist

- [ ] WVS Wave 7 CSV downloaded
- [ ] ESS cumulative file downloaded
- [ ] SPLISS scores extracted to CSV
- [ ] UNDP HDI files downloaded (or auto-download script ran successfully)
- [ ] Kaggle token set up (`~/.kaggle/kaggle.json`)
- [ ] Kaggle download script ran (`python scripts/download_kaggle.py`)
- [ ] World Bank script ran (`python scripts/download_world_bank.py`)
- [ ] Eurostat script ran (`python scripts/download_eurostat.py`)
