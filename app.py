from __future__ import annotations

import pandas as pd
import streamlit as st

from classifier import classify_transaction

st.set_page_config(page_title="ClearCharge", layout="wide")
st.title("ClearCharge - Transaction Classifier")
st.write(
    "Upload a CSV with columns Date, Description, Amount to classify transactions and review risky items."
)

uploaded = st.file_uploader("Upload transaction CSV", type=["csv"])
if uploaded is None:
    st.info("Tip: upload sample_transactions.csv to test quickly.")
    st.stop()

df = pd.read_csv(uploaded)
required_columns = {"Date", "Description", "Amount"}
if not required_columns.issubset(df.columns):
    st.error("CSV must contain Date, Description, Amount columns.")
    st.stop()

if st.button("Classify transactions", type="primary"):
    records = []
    progress = st.progress(0)
    total = len(df.index)

    for i, row in enumerate(df.to_dict(orient="records"), start=1):
        records.append({**row, **classify_transaction(row)})
        progress.progress(i / total if total else 1.0)

    result_df = pd.DataFrame(records)
    st.subheader("Results")
    st.dataframe(result_df, use_container_width=True)

    st.subheader("Review Queue")
    review_df = result_df[(result_df["fraud_flag"]) | (result_df["confidence"] < 70)]
    if review_df.empty:
        st.success("No transactions require review.")
    else:
        st.warning("Flagged transactions require review.")
        st.dataframe(review_df, use_container_width=True)
