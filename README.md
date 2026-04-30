# ClearCharge

AI-powered bank statement explainer built for the **Financial Intelligence** track at Cursor × AI Hackathon London 2026.

---

## What it does

Most bank statements are full of cryptic merchant codes. ClearCharge takes a CSV of transactions and does three things:

**1. Classifies every transaction**
Each row gets a plain-English category (Groceries, Transport, Dining, etc.) and a confidence score. The agent uses two Claude models — Haiku for fast, clear-cut transactions and Sonnet for anything that needs deeper reasoning — routing automatically based on confidence.

**2. Explains cryptic merchant names**
`SQ *BFST CLB 28374` becomes *"Square payment to a breakfast café"*. `AMZN MKTP US*MN6XJ` becomes *"Amazon Marketplace purchase"*. Every transaction gets a one-sentence plain-English explanation.

**3. Flags uncertain and suspicious transactions for human review**
Any transaction with confidence below 70% or a fraud signal goes into a dedicated Review Queue. The agent surfaces what it does not know — it does not hide uncertainty behind a confident-sounding label. A £999 charge to an unknown merchant at 3am shows up as: fraud flag `True`, confidence `22%`, escalated for human review.

---

## Human-in-the-loop design

The Review Queue is not optional UX — it is the core design principle. ClearCharge is built on the premise that a wrong categorisation becomes a wrong financial decision downstream. The agent is calibrated to be conservative: when it is not sure, it says so and asks a human to look. Confidence thresholds are explicit and adjustable.

---

## Tech

- **Claude Haiku** — first-pass classification for clear transactions (fast, low-cost)
- **Claude Sonnet** — deep reasoning for uncertain or flagged items
- **Streamlit** — browser UI, no frontend code required
- **Python** — classifier, prompt logic, model routing

---

## Sample data

`sample_transactions.csv` includes 22 transactions: recognisable UK merchants, cryptic merchant codes, and one obviously suspicious row (£999, unknown merchant, 3am) to demonstrate fraud detection.
