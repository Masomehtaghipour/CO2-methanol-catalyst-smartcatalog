# Smart Catalyst Tool — CO₂-to-Methanol Catalyst Screening

A data-driven engine and interactive Streamlit dashboard for screening and ranking heterogeneous catalysts for CO₂-to-methanol hydrogenation, built on a curated literature dataset of 1,339 experimental records from 57 published studies.

**Live demo:** https://co2-methanol-catalyst-smartcatalog-wpflpqvc5j8jozjqsks9ka.streamlit.app/

## What this is

This repository contains:

1. **A literature dataset** (`MAIN_DATA_smart_tiered_cleaned.csv`) — 1,339 experimental data points compiled from 57 peer-reviewed papers (2015–2023) on CO₂ hydrogenation to methanol, covering 31 base metals and 45 supports under varying temperature, pressure, and H₂/CO₂ conditions.
2. **A screening model** — a linear regression trained on operating conditions (T, P, H₂/CO₂) plus one-hot encoded catalyst identity (Base, Support), used to rank a 17 base × 27 support full-factorial design space (459 combinations) at fixed reference conditions.
3. **An interactive Streamlit dashboard** (`app.py`) — lets users filter, inspect, and rank precomputed candidates by stability and yield score, with adjustable weighting and CSV export.

## Repository contents

| File | Description |
|---|---|
| `app.py` | Streamlit dashboard — loads the precomputed candidate table, applies user filters and a weighted scoring formula, and renders rankings/plots. |
| `requirements.txt` | Python dependencies. |
| `MAIN_DATA_smart_tiered_cleaned.csv` | Source literature dataset (1,339 records, 57 articles). |
| `SmartCatalog_final_ML_ready.csv` | 459-combination screening table consumed by `app.py`. |
| `SmartCatalog_TempScan_*.csv` | Yield predictions at 220/250/280 °C for the full grid; top/stable candidate subsets. |
| `SmartCatalog_PressureScan_full_master.csv` | Yield predictions at 30/50/70 bar. |
| `SmartCatalog_RatioScan_full_master.csv` | Yield predictions at H₂/CO₂ = 2/3/4. |
| `Summary_BestBasePerSupport_*.csv` | Best base metal for each support at 250 °C, 30 bar, H₂/CO₂ = 3. |
| `Experimental_plan_round1.csv` | Proposed candidate shortlist template for experimental validation (results columns currently empty). |

## How to run locally

```bash
git clone https://github.com/Masomehtaghipour/Smart-catalyst-tool.git
cd Smart-catalyst-tool
pip install -r requirements.txt
streamlit run app.py
```

## Methodology summary

- **Data cleaning:** records with complete Base, Support, T, P, H₂/CO₂, and yield fields were retained (761 of 1,339 rows) for regression.
- **Model:** ordinary least squares on one-hot encoded Base/Support plus the three operating variables.
- **Screening grid:** each base metal and support is assigned its average reported loading (wt%) from the literature data, and the model is evaluated across all 459 base × support pairs at fixed reference conditions — most of which were never experimentally tested. These are model extrapolations, not experimental results.

## Limitations

This section is included deliberately, based on independent verification against the raw data. Please read it before citing model predictions as experimental fact.

- **Cross-validated model fit is moderate, not high.** A single train/test split can yield R² as high as 0.84, but 5-fold cross-validation gives a mean R² of **≈0.41 (± 0.24)** — the model explains less than half of yield variance on average, and performance is sensitive to how the data is split.
- **Top-ranked candidates are often extrapolations.** The single highest-ranked system in the 459-combination grid (Ag/ZnAl₂O₄, predicted ≈7.7% yield) has no matching experimental record — Ag was only tested on ZrO₂ in the source literature, where it achieved 0.2–1.4% yield. Predictions for untested combinations should be treated as hypotheses for experimental follow-up, not validated results.
- **Apparent "patterns" can come from a single source.** Some high-yield clusters in the raw data (e.g., the 60–88% yield group at 250 °C / 41 bar on mesoporous supports) come entirely from one published study, not from independent replication across multiple papers.
- **Provenance metadata is sparse.** Article/year/DOI fields are populated for only ~4% of the 1,339 rows (the rest can be recovered by forward-filling within article blocks, but this should be verified before reuse).
- **Some auxiliary screening files in earlier exports contain processing artifacts** (e.g., a constant predicted value across all 459 rows in one CSV variant, and raw terminal output pasted into a few `.xlsx` files instead of structured tables). Use `SmartCatalog_final_ML_ready.csv` and the `P2_SmartCatalog_Screened_*` file as the validated screening outputs.

## Citation

If you use this dataset or code, please cite:

- Software (this version): https://doi.org/10.5281/zenodo.20181400
- Concept DOI (all versions): https://doi.org/10.5281/zenodo.20181399

```bibtex
@software{taghipour_smart_catalyst_tool,
  author       = {Taghipour, Masomeh and Ashrafzadeh, Ali},
  title        = {Smart Catalyst Tool: CO2-to-Methanol Catalyst Screening Engine},
  year         = {2026},
  publisher    = {Zenodo},
  version      = {v1.0.0},
  doi          = {10.5281/zenodo.20181400},
  url          = {https://doi.org/10.5281/zenodo.20181400}
}
```

## Roadmap

- [ ] Replace single train/test split reporting with cross-validated metrics throughout
- [ ] Non-linear models (random forest / gradient boosting) to capture base–support interaction effects
- [ ] Flag extrapolated (untested) vs. experimentally grounded predictions in the dashboard
- [ ] Fill in `Experimental_plan_round1.csv` with real validation runs
- [ ] Re-export the corrupted auxiliary screening files

## Author contributions and AI-assistance disclosure

Dataset compilation, modeling, and the Streamlit application were developed by the project authors. AI-assisted tools were used for code review, documentation drafting, and independent verification of reported metrics against the underlying data (see Limitations above).

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), matching the license registered on the [Zenodo record](https://doi.org/10.5281/zenodo.20181400).






[Open Streamlit dashboard](https://co2-methanol-catalyst-smartcatalog-wpflpqvc5j8jozjqsks9ka.streamlit.app/)
