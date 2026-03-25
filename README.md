# Lithuania LA 2028 Olympic Medal Forecast

Sport-by-sport medal probability model for Lithuania at the Los Angeles 2028 Olympics.

## Live App

[https://lt-olympic-forecast.streamlit.app](https://lt-olympic-forecast.streamlit.app)

## How it works

Base probabilities are computed from **real historical data**:

- **Olympedia** results 1992–2020 (Lithuania's Summer Games medal record per sport)
- **Paris 2024** official IOC results
- Known data correction: Andrius Gudžius, Discus Gold, Rio 2016 (absent from source dataset)
- **Bayesian shrinkage** applied to sports with < 5 Games of data (e.g., 3x3 Basketball)
- **Pipeline factors** applied per sport based on active athlete status heading into 2028

Forward-looking adjustments are documented with sources (World Athletics, FINA, FIBA 3x3, UIPM, ICF, ISSF rankings 2024).

## Key findings (baseline, current funding)

| Sport | 2028 Prob | Historical win rate |
|---|---|---|
| Athletics (Discus) | 82% | 7/9 Games |
| 3x3 Basketball | 34% | 1/1 Games (shrunk) |
| Rowing | 32% | 3/9 Games |
| Modern Pentathlon | 22% | 4/8 Games (Asadauskaite aging) |
| Swimming | 19% | 1/8 Games (2 active contenders) |

**Expected total: 2.2 medals (P10=1, P90=4)**

Note: Breaking is NOT on the LA 2028 program. NICKA's silver (Paris 2024) cannot be replicated.

## Model architecture

- **Sport-level model** (`model/lithuania_2028.py`): Monte Carlo simulation across 9 sports
- **Macro model** (`simulation/simulator.py`): XGBoost + Random Forest ensemble, trained on 137 countries 1960–2024
- Training data: Olympedia + World Bank GDP/population + UNDP HDI + Eurostat + WVS + ESS

## Run locally

```bash
pip install -r requirements.txt
streamlit run simulation/app.py
```

## Reproduce the sport probabilities

```bash
python scripts/compute_ltu_sport_probs.py
```
