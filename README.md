# ClearCharge

AI-powered transaction classifier for beginners. Upload bank transactions and get:
- spending category
- plain-English explanation
- confidence score (0-100)
- fraud flag

Low-confidence rows and flagged rows are routed into a human **Review Queue**.

## Quickstart (Under 10 Minutes)

### 1) Install dependencies
```bash
python -m pip install -r requirements.txt
```

### 2) Set your Anthropic API key

**macOS/Linux (bash/zsh)**
```bash
export ANTHROPIC_API_KEY="your_key_here"
```

**Windows PowerShell**
```powershell
$env:ANTHROPIC_API_KEY="your_key_here"
```

**Windows cmd**
```cmd
set ANTHROPIC_API_KEY=your_key_here
```

### 3) Run the app (PATH-safe)
```bash
python -m streamlit run app.py
```

### 4) Test quickly
Upload `sample_transactions.csv`.

## CSV Format

Your CSV must include exactly these headers:
- `Date`
- `Description`
- `Amount`

Example:
```csv
Date,Description,Amount
2026-04-01,Tesco Superstore #1184,-42.37
2026-04-10,UNKNOWN MERCHANT 03:00AM,-999.00
```

## How Model Routing Works

1. First pass uses `claude-haiku-4-5-20251001`
2. If confidence is below 70, ClearCharge re-runs with `claude-sonnet-4-6`
3. Final output includes category, explanation, confidence, fraud flag, and model used

## Troubleshooting

### `streamlit: command not found`
Use:
```bash
python -m streamlit run app.py
```

### Missing API key
If the app says `Missing ANTHROPIC_API_KEY`, set the env var in the same terminal where you run Streamlit.

### CSV errors
If classification does not start:
- check headers are exactly `Date`, `Description`, `Amount`
- ensure `Amount` is numeric-style text (e.g. `-42.37`)

### Model returned non-JSON response
The classifier already handles markdown-wrapped JSON responses from Claude. If this still appears, retry once and confirm your API key is valid.