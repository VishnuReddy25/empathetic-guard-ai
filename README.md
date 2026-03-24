# 💙 Empathetic-Guard AI

A fully local, responsible AI emotional-support chatbot.  
**Zero cloud APIs. Zero subscriptions. Everything runs on your machine.**

---

## 🏗️ Architecture

```
User (Streamlit UI)
      ↓ POST /api/chat
FastAPI Backend
  ├── Emotion Detection  (HuggingFace DistilRoBERTa)
  ├── Risk Assessment    (Detoxify + keyword list)
  ├── LLM Response       (Ollama → llama3, local)
  └── SQLite DB          (SQLAlchemy, zero setup)
```

---

## 📁 Project Structure

```
empathetic-guard-ai/
├── backend/
│   ├── app.py                  # FastAPI entry point
│   ├── routes/
│   │   └── chat.py             # POST /api/chat, GET /api/history
│   ├── services/
│   │   ├── emotion_service.py  # HuggingFace emotion detection
│   │   ├── risk_service.py     # Detoxify + keyword risk scoring
│   │   └── llm_service.py      # Ollama LLM calls + prompt engineering
│   └── db/
│       └── database.py         # SQLAlchemy models + SQLite config
├── frontend/
│   └── app.py                  # Streamlit chat UI
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Setup (Step-by-Step)

### Step 1 — Install Python dependencies

```bash
# From the project root
pip install -r requirements.txt
```

> **Note:** First run downloads ~500 MB of HuggingFace models. Subsequent runs are instant.

---

### Step 2 — Install & start Ollama

**Install Ollama:**

| OS      | Command |
|---------|---------|
| Linux   | `curl -fsSL https://ollama.com/install.sh \| sh` |
| macOS   | Download from [ollama.com](https://ollama.com) |
| Windows | Download installer from [ollama.com](https://ollama.com) |

**Pull llama3 model (~4 GB):**

```bash
ollama pull llama3
```

**Start Ollama (keep this terminal open):**

```bash
ollama run llama3
```

---

### Step 3 — Configure environment (optional)

```bash
cp .env.example .env
# Edit .env if your Ollama runs on a different port
```

---

### Step 4 — Start the backend

```bash
# From the project root (one level above the backend/ folder)
uvicorn backend.app:app --reload --port 8000
```

The API will be live at: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

---

### Step 5 — Start the frontend

Open a **new terminal**:

```bash
streamlit run frontend/app.py
```

Browser opens automatically at: `http://localhost:8501`

---

## 🔌 API Reference

### `POST /api/chat`

```json
// Request
{
  "user_id": 1,
  "message": "I'm feeling really overwhelmed today"
}

// Response
{
  "response": "That sounds really tough...",
  "emotion": "sadness",
  "emotion_score": 0.91,
  "risk": "LOW"
}
```

### `GET /api/history/{user_id}?limit=20`

Returns last N conversations for a user.

---

## 🛡️ Ethical AI Features

| Feature | Implementation |
|---------|---------------|
| Emotion detection | 7-class DistilRoBERTa (joy, sadness, anger, fear, surprise, disgust, neutral) |
| Crisis keyword detection | 10 explicit crisis phrases → immediate HIGH risk |
| Toxicity scoring | Detoxify model (toxicity + severe_toxicity) |
| Crisis override | HIGH risk → fixed safe response, LLM **not called** |
| Memory | Last 5 turns injected into prompt for context |
| Local-only | No data leaves your machine |
| Disclaimer | Prominently displayed in UI sidebar |

---

## 🗄️ Database

Uses **SQLite** — no installation needed. A file `empathetic_guard.db` is created automatically on first run.

Tables: `users`, `conversations`, `emotion_logs`, `risk_logs`

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| `ConnectionError` to Ollama | Run `ollama run llama3` and keep terminal open |
| Slow first response | Models loading into memory — wait ~30 seconds |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| Port 8000 in use | Use `--port 8001` and update `API_URL` in `frontend/app.py` |

---

## ⚠️ Disclaimer

This chatbot is **not a substitute** for professional mental health care.  
If you or someone you know is in crisis, please contact:

- **iCall (India):** 9152987821  
- **Vandrevala Foundation:** 1860-2662-345 *(24/7)*  
- **International:** [findahelpline.com](https://findahelpline.com)
