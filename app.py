from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from classifier import classify_transaction

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="ClearCharge", page_icon="💳", layout="wide")

st.title("💳 ClearCharge")
st.caption("AI-powered bank statement explainer · flags uncertain transactions for human review")

with st.expander("Getting Started", expanded=True):
    st.markdown(
        "1. Set `ANTHROPIC_API_KEY`\n"
        "2. Upload CSV with `Date`, `Description`, `Amount`\n"
        "3. Click **Classify transactions**\n"
        "4. Review `confidence < 70` or `fraud_flag = True` rows"
    )
    st.caption(
        "Routing note: transactions are analyzed with Claude Haiku first and "
        "automatically escalated to Claude Sonnet when confidence is low."
    )

# ── File upload ───────────────────────────────────────────────────────────────
uploaded = st.file_uploader("Upload your bank CSV (Date, Description, Amount)", type=["csv"])
if uploaded is None:
    st.info("👆 Upload a CSV to get started — or use **sample_transactions.csv** to test.")
    st.stop()

df = pd.read_csv(uploaded)
required_columns = {"Date", "Description", "Amount"}
missing_columns = sorted(required_columns - set(df.columns))
if missing_columns:
    st.error("❌ Missing required columns: " + ", ".join(missing_columns))
    st.caption("Expected headers: Date, Description, Amount")
    st.stop()

st.success(f"✅ Loaded {len(df)} transactions from **{uploaded.name}**")

if not os.getenv("ANTHROPIC_API_KEY"):
    st.error("Missing `ANTHROPIC_API_KEY`.")
    st.code("export ANTHROPIC_API_KEY='your_key_here'  # macOS/Linux")
    st.code("$env:ANTHROPIC_API_KEY='your_key_here'    # PowerShell")
    st.code("set ANTHROPIC_API_KEY=your_key_here       # Windows cmd")
    st.stop()

# ── Run classifier ────────────────────────────────────────────────────────────
if st.button("🔍 Classify transactions", type="primary"):
    records = []
    progress = st.progress(0, text="Analysing transactions…")
    total = len(df.index)

    for i, row in enumerate(df.to_dict(orient="records"), start=1):
        try:
            result = classify_transaction(row)
        except ValueError as exc:
            st.error(f"Classification failed at row {i}: {exc}")
            st.caption("Retry after confirming API key and CSV formatting.")
            st.stop()
        records.append({**row, **result})
        progress.progress(i / total if total else 1.0,
                          text=f"Analysing {i} of {total}…")

    progress.empty()
    result_df = pd.DataFrame(records)

    # ── Summary metrics ───────────────────────────────────────────────────────
    total_count   = len(result_df)
    flagged_count = int(
        ((result_df["fraud_flag"]) | (result_df["confidence"] < 70)).sum()
    )
    avg_conf = int(result_df["confidence"].mean())
    fraud_count = int(result_df["fraud_flag"].sum())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Transactions", total_count)
    col2.metric("Avg Confidence", f"{avg_conf}%")
    col3.metric("Need Review", flagged_count,
                delta=f"{flagged_count} flagged" if flagged_count else None,
                delta_color="inverse")
    col4.metric("Fraud Signals", fraud_count,
                delta=f"{fraud_count} detected" if fraud_count else None,
                delta_color="inverse")

    st.divider()

    # ── Colour-coded results table ────────────────────────────────────────────
    def row_colour(row):
        if row["fraud_flag"]:
            colour = "background-color: #ffd6d6"   # red
        elif row["confidence"] < 70:
            colour = "background-color: #fff3cd"   # amber
        else:
            colour = "background-color: #d4edda"   # green
        return [colour] * len(row)

    display_cols = ["Date", "Description", "Amount",
                    "category", "confidence", "fraud_flag", "model_used"]
    styled = (
        result_df[display_cols]
        .style.apply(row_colour, axis=1)
        .format({"confidence": "{}%"})
    )

    st.subheader("📊 All Transactions")
    st.caption("🟢 High confidence  🟡 Uncertain (< 70%)  🔴 Fraud signal")
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.divider()

    # ── Human Review Queue ────────────────────────────────────────────────────
    st.subheader("🚨 Human Review Queue")
    review_df = result_df[
        (result_df["fraud_flag"]) | (result_df["confidence"] < 70)
    ].reset_index(drop=True)

    if review_df.empty:
        st.success("✅ All transactions cleared — no human review needed.")
    else:
        st.warning(
            f"**{len(review_df)} transaction{'s' if len(review_df) > 1 else ''} "
            f"need your review.** The agent is not confident enough to act alone."
        )

        for _, row in review_df.iterrows():
            fraud_label = "🔴 FRAUD SIGNAL" if row["fraud_flag"] else "🟡 UNCERTAIN"
            header = (
                f"{fraud_label} · {row['Date']} · "
                f"{row['Description']} · £{abs(float(row['Amount'])):.2f}"
            )
            with st.expander(header):
                c1, c2, c3 = st.columns(3)
                c1.metric("Category", row["category"])
                c2.metric("Confidence", f"{row['confidence']}%")
                c3.metric("Fraud flag", "⚠️ Yes" if row["fraud_flag"] else "No")

                st.markdown(f"**What the agent thinks:** {row['explanation']}")

                model_label = (
                    "⚡ Claude Haiku (fast)"
                    if "haiku" in str(row.get("model_used", "")).lower()
                    else "🧠 Claude Sonnet (deep reasoning)"
                )
                st.caption(f"Analysed by {model_label} · Escalated due to low confidence or fraud signal")
