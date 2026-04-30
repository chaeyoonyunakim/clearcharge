SYSTEM_PROMPT = """You are a careful financial transaction analyst.
Classify bank transactions into useful categories and assess fraud risk.
Be concise, practical, and avoid overconfidence.
"""

USER_PROMPT_TEMPLATE = """Classify this bank transaction:

Date: {date}
Description: {description}
Amount: {amount}

Return a JSON object with fields: category, explanation, confidence (0-100), fraud_flag (true/false).
Be conservative - if uncertain, give a lower confidence score.

Guidance:
- category: one short label (e.g., Groceries, Transport, Shopping, Dining, Utilities, Income, Transfer, Other)
- explanation: plain-English, 1-2 sentences
- confidence: integer from 0 to 100
- fraud_flag: true if the transaction appears unusual or risky
"""
