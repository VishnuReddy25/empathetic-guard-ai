"""
Risk Detection Service
Uses Detoxify for toxicity scoring + custom keyword list for crisis signals.
Returns risk_level: "HIGH" or "LOW"
"""

from detoxify import Detoxify
from functools import lru_cache

# ── Crisis keywords (override to HIGH regardless of toxicity score) ──────────
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die",
    "don't want to live", "take my own life", "self harm",
    "hurt myself", "no reason to live", "better off dead"
]

# Thresholds for Detoxify scores
TOXICITY_THRESHOLD       = 0.7
SEVERE_TOXICITY_THRESHOLD = 0.5


@lru_cache(maxsize=1)
def _load_detoxify():
    """Load Detoxify model once."""
    print("[RiskService] Loading detoxify model (first call only)...")
    return Detoxify("original")


def assess_risk(text: str) -> dict:
    """
    Assess whether the message is high-risk.

    Checks:
      1. Crisis keyword presence (immediate HIGH)
      2. Detoxify toxicity / severe_toxicity scores

    Returns:
        {
            "risk_level": "HIGH" | "LOW",
            "toxicity": 0.12,
            "severe_toxicity": 0.01,
            "keyword_match": False
        }
    """
    text_lower = text.lower()

    # 1. Keyword check — most sensitive signal
    keyword_hit = any(kw in text_lower for kw in CRISIS_KEYWORDS)
    if keyword_hit:
        return {
            "risk_level": "HIGH",
            "toxicity": None,
            "severe_toxicity": None,
            "keyword_match": True
        }

    # 2. Detoxify scoring
    try:
        model   = _load_detoxify()
        scores  = model.predict(text)
        tox     = float(scores["toxicity"])
        sev_tox = float(scores["severe_toxicity"])

        risk_level = (
            "HIGH"
            if tox >= TOXICITY_THRESHOLD or sev_tox >= SEVERE_TOXICITY_THRESHOLD
            else "LOW"
        )

        return {
            "risk_level": risk_level,
            "toxicity": round(tox, 4),
            "severe_toxicity": round(sev_tox, 4),
            "keyword_match": False
        }
    except Exception as e:
        print(f"[RiskService] Error: {e}")
        return {
            "risk_level": "LOW",
            "toxicity": None,
            "severe_toxicity": None,
            "keyword_match": False
        }
