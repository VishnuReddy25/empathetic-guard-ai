"""
Empathetic-Guard AI — FastAPI Backend
Run with: uvicorn backend.app:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db.database import init_db
from backend.routes.chat import router as chat_router

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Empathetic-Guard AI",
    description="Responsible AI emotional support chatbot with emotion detection & risk assessment.",
    version="1.0.0"
)

# Allow Streamlit frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Create DB tables on first run."""
    init_db()
    print("✅ Database initialised (SQLite).")


# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(chat_router, prefix="/api", tags=["chat"])


@app.get("/", tags=["health"])
def root():
    return {
        "status": "ok",
        "service": "Empathetic-Guard AI",
        "docs": "/docs"
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}
