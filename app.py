import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="CO2-to-Methanol Catalyst Screening – Data-Driven Dashboard",
    layout="wide",
)

st.title("CO2-to-Methanol Catalyst Screening – Data-Driven Dashboard")

st.caption(
    "Developed by Dr. Masomeh Taghipour  |  Masomehtaghipour59@gmail.com"
)

st.markdown(
    """
    This dashboard provides an **interactive view of a model-generated screening table**
    for CO2-to-methanol catalysts, built on a literature dataset of 1,339 experimental
    records from 57 published studies.

    - The 459 base–support combinations shown here are **model predictions** at fixed
      reference conditions (250 °C, 30 bar, H₂/CO₂ = 3) — not all of them are
      experimentally tested systems.
    - Only **68 of 459** combinations (≈15%) correspond to a base–support pair that
      actually appears in the underlying literature data. The rest are
      **extrapolations** of a linear regression model and should be treated as
      hypotheses for experimental follow-up, not confirmed results.
    - Use the **"Tested only"** filter below to restrict the table to
      experimentally grounded combinations.
    """
)

st.warning(
    "⚠️ Most rows in this table are model-derived predictions, not direct "
    "experimental measurements. Check the **Is_Tested** column before treating "
    "a candidate as validated.",
    icon="⚠️",
)

# ---------- 1. Load base dataset ----------
@st.cache_data
def load_base_data():
    # IMPORTANT: for Streamlit Cloud, use the CSV inside the repo
    df = pd.read_csv("SmartCatalog_final_ML_ready.csv")
    return df

base_df = load_base_data()

# ---------- 1a. Data overview (no upload) ----------
st.subheader("1. Data overview")

# In this version we only use the internal SmartCatalog dataset (no file upload).
merged_df = base_df.copy()

if "Is_Tested" not in merged_df.columns:
    st.error(
        "Column 'Is_Tested' not found in SmartCatalog_final_ML_ready.csv. "
        "Please regenerate the dataset to include the tested-vs-extrapolated flag."
    )
    merged_df["Is_Tested"] = np.nan

n_tested = int(merged_df["Is_Tested"].sum()) if merged_df["Is_Tested"].notna().any() else 0
st.write(
    f"Final data shape for scoring: {merged_df.shape}  "
    f"({n_tested} experimentally tested combinations, "
    f"{merged_df.shape[0] - n_tested} model extrapolations)"
)
st.dataframe(merged_df.head())

# ---------- 1b. Filters (Base, Support, Stable, Selected, Ratios, Tested) ----------
st.sidebar.header("Filters")

# unique values for categorical filters
bases = ["(All)"] + sorted(merged_df["Base"].dropna().unique().tolist())
supports = ["(All)"] + sorted(merged_df["Support"].dropna().unique().tolist())

base_filter = st.sidebar.selectbox("Filter by Base", bases)
support_filter = st.sidebar.selectbox("Filter by Support", supports)

# binary filters for stability / selection
stable_filter = st.sidebar.selectbox(
    "Stable?",
    ["(All)", "Only stable (Is_Stable=1)", "Only unstable (Is_Stable=0)"],
)
selected_filter = st.sidebar.selectbox(
    "Selected?",
    ["(All)", "Only selected (Is_Selected=1)", "Only not selected (Is_Selected=0)"],
)

# provenance filter: experimentally tested vs. model extrapolation
tested_filter = st.sidebar.selectbox(
    "Provenance",
    [
        "(All — tested + extrapolated)",
        "Tested only (experimentally observed)",
        "Extrapolated only (model prediction, untested)",
    ],
)

# numeric filters for ratios
st.sidebar.markdown("---")
st.sidebar.markdown("**Ratio filters**")

h2co2_min = float(merged_df["Best_H2CO2_ratio"].min())
h2co2_max = float(merged_df["Best_H2CO2_ratio"].max())
best_h2co2_range = st.sidebar.slider(
    "Best_H2CO2_ratio range",
    min_value=h2co2_min,
    max_value=h2co2_max,
    value=(h2co2_min, h2co2_max),
    step=0.1,
)

delta_min = float(merged_df["Delta_yield_ratio"].min())
delta_max = float(merged_df["Delta_yield_ratio"].max())
delta_range = st.sidebar.slider(
    "Delta_yield_ratio range",
    min_value=delta_min,
    max_value=delta_max,
    value=(delta_min, delta_max),
    step=0.01,
)

filtered_df = merged_df.copy()

# apply categorical filters
if base_filter != "(All)":
    filtered_df = filtered_df[filtered_df["Base"] == base_filter]

if support_filter != "(All)":
    filtered_df = filtered_df[filtered_df["Support"] == support_filter]

if stable_filter == "Only stable (Is_Stable=1)":
    filtered_df = filtered_df[filtered_df["Is_Stable"] == 1]
elif stable_filter == "Only unstable (Is_Stable=0)":
    filtered_df = filtered_df[filtered_df["Is_Stable"] == 0]

if selected_filter == "Only selected (Is_Selected=1)":
    filtered_df = filtered_df[filtered_df["Is_Selected"] == 1]
elif selected_filter == "Only not selected (Is_Selected=0)":
    filtered_df = filtered_df[filtered_df["Is_Selected"] == 0]

if tested_filter == "Tested only (experimentally observed)":
    filtered_df = filtered_df[filtered_df["Is_Tested"] == True]
elif tested_filter == "Extrapolated only (model prediction, untested)":
    filtered_df = filtered_df[filtered_df["Is_Tested"] == False]

# apply numeric filters
filtered_df = filtered_df[
    (filtered_df["Best_H2CO2_ratio"] >= best_h2co2_range[0]) &
    (filtered_df["Best_H2CO2_ratio"] <= best_h2co2_range[1]) &
    (filtered_df["Delta_yield_ratio"] >= delta_range[0]) &
    (filtered_df["Delta_yield_ratio"] <= delta_range[1])
]

st.write("Filtered data shape:", filtered_df.shape)
st.dataframe(filtered_df.head())

# ---------- 2. Weights and score calculation ----------
st.subheader("2. Weights and score calculation")

col1, col2, col3 = st.columns(3)

with col1:
    w_yield = st.slider("Weight: Best_MeOH_yield_ratio", 0.0, 2.0, 1.0, 0.1)
with col2:
    w_stable = st.slider("Weight: Is_Stable (bonus if 1)", 0.0, 2.0, 0.5, 0.1)
with col3:
    w_selected = st.slider("Weight: Is_Selected (bonus if 1)", 0.0, 2.0, 0.5, 0.1)

def normalize(series):
    return (series - series.min()) / (series.max() - series.min() + 1e-9)

required_cols = [
    "Base", "Support",
    "Best_H2CO2_ratio", "Best_MeOH_yield_ratio",
    "Is_Stable", "Is_Selected", "Is_Tested"
]

missing = [c for c in required_cols if c not in filtered_df.columns]
if missing:
    st.error(f"Missing required columns in data: {missing}")
    filtered_df["score"] = np.nan
elif filtered_df.empty:
    st.warning("No rows match the current filters. Adjust filters to see results.")
    filtered_df["score"] = np.nan
else:
    filtered_df["yield_norm"] = normalize(filtered_df["Best_MeOH_yield_ratio"])

    filtered_df["Is_Stable_num"] = filtered_df["Is_Stable"].astype(float)
    filtered_df["Is_Selected_num"] = filtered_df["Is_Selected"].astype(float)

    filtered_df["score"] = (
        w_yield * filtered_df["yield_norm"] +
        w_stable * filtered_df["Is_Stable_num"] +
        w_selected * filtered_df["Is_Selected_num"]
    )

st.dataframe(
    filtered_df[[
        "Base", "Support",
        "Best_H2CO2_ratio", "Best_MeOH_yield_ratio",
        "Is_Stable", "Is_Selected", "Is_Tested", "score"
    ]].head()
)

# ---------- 3. Plot, ranking, and export ----------
st.subheader("3. Plot, ranking, and export")

if "score" in filtered_df.columns and filtered_df["score"].notna().any():
    ranked_df = filtered_df.sort_values("score", ascending=False)

    top_n = st.slider("How many top candidates to show?", 5, 100, 10, 1)
    st.write("Top candidates:")
    top_df = ranked_df[[
        "Base", "Support",
        "Best_H2CO2_ratio", "Best_MeOH_yield_ratio",
        "Is_Stable", "Is_Selected", "Is_Tested", "score"
    ]].head(top_n)
    st.dataframe(top_df)

    n_top_tested = int(top_df["Is_Tested"].sum())
    st.caption(
        f"Of the {len(top_df)} candidates shown above, "
        f"{n_top_tested} are experimentally tested and "
        f"{len(top_df) - n_top_tested} are model extrapolations."
    )

    st.write("Scatter plot: Best_H2CO2_ratio vs Best_MeOH_yield_ratio (color = score)")
    plot_df = ranked_df.copy()
    st.scatter_chart(
        plot_df,
        x="Best_H2CO2_ratio",
        y="Best_MeOH_yield_ratio",
        color="score",
    )

    csv_bytes = top_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download top candidates as CSV",
        data=csv_bytes,
        file_name="top_candidates_filtered_scored.csv",
        mime="text/csv",
    )
else:
    st.warning("No valid score, cannot show plot and ranking.")
