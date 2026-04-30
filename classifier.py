from __future__ import annotations

import json
import os
from typing import Any

from anthropic import Anthropic

from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

FAST_MODEL = "claude-haiku-4-5-20251001"
DEEP_MODEL = "claude-sonnet-4-6"
CONFIDENCE_THRESHOLD = 70


def _client() -> Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Missing ANTHROPIC_API_KEY environment variable.")
    return Anthropic(api_key=api_key)


def _normalize_output(raw: dict[str, Any]) -> dict[str, Any]:
    category = str(raw.get("category", "Other")).strip() or "Other"
    explanation = str(raw.get("explanation", "")).strip() or "No explanation provided."

    try:
        confidence = int(raw.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 0
    confidence = max(0, min(100, confidence))

    fraud_flag = raw.get("fraud_flag", False)
    if isinstance(fraud_flag, str):
        fraud_flag = fraud_flag.strip().lower() == "true"
    else:
        fraud_flag = bool(fraud_flag)

    return {
        "category": category,
        "explanation": explanation,
        "confidence": confidence,
        "fraud_flag": fraud_flag,
    }


def _run_model(row: dict[str, Any], model: str) -> dict[str, Any]:
    prompt = USER_PROMPT_TEMPLATE.format(
        date=row.get("Date", ""),
        description=row.get("Description", ""),
        amount=row.get("Amount", ""),
    )

    response = _client().messages.create(
        model=model,
        max_tokens=400,
        temperature=0,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    text = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    ).strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model returned non-JSON response: {text}") from exc

    result = _normalize_output(parsed)
    result["model_used"] = model
    return result


def classify_transaction(row: dict[str, Any]) -> dict[str, Any]:
    first_pass = _run_model(row, FAST_MODEL)
    if first_pass["confidence"] >= CONFIDENCE_THRESHOLD:
        return first_pass
    return _run_model(row, DEEP_MODEL)
