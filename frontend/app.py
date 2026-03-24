"""
Empathetic-Guard AI — Streamlit Frontend
Run with: streamlit run frontend/app.py
"""

import streamlit as st
import requests
import json

# ── Config ────────────────────────────────────────────────────────────────────
API_URL   = "http://localhost:8000/api"
PAGE_TITLE = "Empathetic-Guard AI 💙"

# Emotion → emoji mapping for display
EMOTION_EMOJI = {
    "joy":      "😊",
    "sadness":  "😢",
    "anger":    "😠",
    "fear":     "😨",
    "surprise": "😲",
    "disgust":  "😤",
    "neutral":  "😐",
}

RISK_COLOR = {
    "HIGH": "🔴",
    "LOW":  "🟢",
}

# ── Page setup ─────────────────────────────────────────────────────────────────
st.set_page_config(page_title=PAGE_TITLE, page_icon="💙", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #f0f4f8; }
    .user-bubble {
        background: #4a90d9; color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 10px 16px; margin: 6px 0;
        max-width: 75%; float: right; clear: both;
        font-size: 15px;
    }
    .ai-bubble {
        background: #ffffff; color: #1a1a2e;
        border-radius: 18px 18px 18px 4px;
        padding: 10px 16px; margin: 6px 0;
        max-width: 75%; float: left; clear: both;
        font-size: 15px; border: 1px solid #dce3ed;
    }
    .meta-tag {
        font-size: 11px; color: #888;
        float: left; clear: both;
        margin: 0 0 8px 4px;
    }
    .crisis-banner {
        background: #ffe4e4; border-left: 4px solid #e74c3c;
        border-radius: 8px; padding: 12px; margin: 8px 0;
        font-size: 14px;
    }
    .clearfix { clear: both; display: block; height: 4px; }
</style>
""", unsafe_allow_html=True)

st.title(PAGE_TITLE)
st.caption("A safe, empathetic space. All processing happens locally on your machine. 🔒")

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []   # list of {role, content, emotion, risk}

if "user_id" not in st.session_state:
    st.session_state.user_id = 1     # default demo user


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.user_id = st.number_input(
        "User ID", min_value=1, max_value=9999,
        value=st.session_state.user_id, step=1
    )
    st.divider()

    st.subheader("📖 Disclaimer")
    st.info(
        "This chatbot is **not a substitute** for professional mental health care. "
        "If you are in crisis, please contact a qualified professional or helpline."
    )

    st.subheader("🆘 Crisis Lines (India)")
    st.markdown("""
- **iCall:** 9152987821
- **Vandrevala Foundation:** 1860-2662-345 *(24/7)*
- **NIMHANS:** 080-46110007
    """)

    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

    # Check backend health
    st.divider()
    try:
        r = requests.get(f"{API_URL.replace('/api', '')}/health", timeout=3)
        if r.status_code == 200:
            st.success("✅ Backend connected")
        else:
            st.error("⚠️ Backend error")
    except Exception:
        st.error("❌ Backend offline — run `uvicorn backend.app:app --reload`")


# ── Chat display ──────────────────────────────────────────────────────────────
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">🧑 {msg["content"]}</div><div class="clearfix"></div>', unsafe_allow_html=True)
        else:
            emoji = EMOTION_EMOJI.get(msg.get("emotion", "neutral"), "🤖")
            risk  = msg.get("risk", "LOW")
            risk_icon = RISK_COLOR.get(risk, "🟢")

            # Crisis banner
            if risk == "HIGH":
                st.markdown(
                    f'<div class="crisis-banner">🆘 <b>High-risk signal detected.</b> '
                    f'Please reach out to a helpline.</div>',
                    unsafe_allow_html=True
                )

            st.markdown(f'<div class="ai-bubble">💙 {msg["content"]}</div><div class="clearfix"></div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="meta-tag">{emoji} {msg.get("emotion","—")} &nbsp;|&nbsp; {risk_icon} {risk}</div>'
                f'<div class="clearfix"></div>',
                unsafe_allow_html=True
            )


# ── Input area ────────────────────────────────────────────────────────────────
st.divider()

col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        label="Your message",
        placeholder="How are you feeling today?",
        label_visibility="collapsed",
        key="input_box"
    )
with col2:
    send = st.button("Send 💬", use_container_width=True)


# ── Send message ──────────────────────────────────────────────────────────────
if send and user_input.strip():
    user_message = user_input.strip()

    # Append user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    with st.spinner("Thinking..."):
        try:
            resp = requests.post(
                f"{API_URL}/chat",
                json={"user_id": st.session_state.user_id, "message": user_message},
                timeout=90
            )
            data = resp.json()

            st.session_state.messages.append({
                "role": "assistant",
                "content":  data.get("response", "Sorry, I couldn't generate a response."),
                "emotion":  data.get("emotion", "neutral"),
                "risk":     data.get("risk", "LOW"),
            })

        except requests.exceptions.ConnectionError:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "⚠️ Cannot reach the backend. Is it running?",
                "emotion": "neutral",
                "risk": "LOW",
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ An error occurred: {e}",
                "emotion": "neutral",
                "risk": "LOW",
            })

    st.rerun()
