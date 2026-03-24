"""
Emotion Detection Service
Uses: j-hartmann/emotion-english-distilroberta-base
Returns emotion label + confidence score.
Model is loaded once at startup (lazy singleton).
"""

from transformers import pipeline
from functools import lru_cache

# Labels from this model:
# anger, disgust, fear, joy, neutral, sadness, surprise
EMOTION_LABELS = ["anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]


@lru_cache(maxsize=1)
def _load_pipeline():
    """Load the model once and cache it in memory."""
    print("[EmotionService] Loading emotion model (first call only)...")
    return pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=1
    )


def detect_emotion(text: str) -> dict:
    """
    Detect the dominant emotion in a text string.

    Returns:
        {
            "emotion": "sadness",
            "score": 0.92
        }
    """
    try:
        clf = _load_pipeline()
        result = clf(text)[0]  # top_k=1 returns a list with one item
        top = result[0]        # dict with 'label' and 'score'
        return {
            "emotion": top["label"].lower(),
            "score": round(top["score"], 4)
        }
    except Exception as e:
        print(f"[EmotionService] Error: {e}")
        return {"emotion": "neutral", "score": 0.0}
