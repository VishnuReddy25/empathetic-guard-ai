"""
LLM Service — calls local Ollama (llama3) via its REST API.
No LangChain dependency needed; plain requests is simpler and more reliable.
"""

import os
import requests

OLLAMA_BASE = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# ── System prompt template ────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a compassionate and responsible mental health support assistant.
Always respond with empathy, validation, and care.
Never give harmful advice.
If the user shows distress, suggest healthy coping strategies.
Keep responses concise (2-4 sentences) unless more detail is needed.
Do NOT repeat the user's words back to them verbatim.

User emotion: {emotion}
Risk level: {risk}
"""

# ── Crisis override response ──────────────────────────────────────────────────
CRISIS_RESPONSE = (
    "I'm really sorry you're feeling this way. You are not alone. 💙\n\n"
    "Please consider reaching out to someone you trust or a mental health helpline. "
    "In India you can call **iCall: 9152987821** or **Vandrevala Foundation: 1860-2662-345** (24/7). "
    "You deserve support — help is available right now."
)


def build_prompt(
    message: str,
    emotion: str,
    risk: str,
    history: list[dict]
) -> str:
    """
    Construct the full prompt with conversation history context.

    history: list of {"message": ..., "response": ...} dicts (last 5 turns)
    """
    system = SYSTEM_PROMPT.format(emotion=emotion, risk=risk)

    # Build context from prior turns
    context_lines = []
    for turn in history:
        context_lines.append(f"User: {turn['message']}")
        context_lines.append(f"Assistant: {turn['response']}")

    context_block = "\n".join(context_lines)
    if context_block:
        context_block = f"\n\n--- Previous conversation ---\n{context_block}\n--- End ---\n"

    full_prompt = (
        f"{system}"
        f"{context_block}\n"
        f"User: {message}\n"
        f"Assistant:"
    )
    return full_prompt


def generate_response(
    message: str,
    emotion: str,
    risk_level: str,
    history: list[dict]
) -> str:
    """
    Generate an empathetic response.

    If risk_level is HIGH, return the crisis response immediately
    without calling the LLM.
    """
    # ── Crisis override — do NOT call LLM ────────────────────────────────────
    if risk_level == "HIGH":
        return CRISIS_RESPONSE

    # ── Normal path — call Ollama ─────────────────────────────────────────────
    prompt = build_prompt(message, emotion, risk_level, history)

    try:
        resp = requests.post(
            f"{OLLAMA_BASE}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 256   # keep responses concise
                }
            },
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "I'm here for you. Can you tell me more about how you're feeling?").strip()

    except requests.exceptions.ConnectionError:
        return (
            "⚠️ I couldn't connect to the local AI model. "
            "Please make sure Ollama is running: `ollama run llama3`"
        )
    except Exception as e:
        print(f"[LLMService] Error: {e}")
        return "I'm here to listen. Could you share a bit more about what's on your mind?"
