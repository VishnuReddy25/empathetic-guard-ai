"""
Chat Router — POST /chat
Orchestrates: emotion detection → risk assessment → LLM response → DB storage
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from backend.db.database import get_db, Conversation, EmotionLog, RiskLog, User
from backend.services.emotion_service import detect_emotion
from backend.services.risk_service import assess_risk
from backend.services.llm_service import generate_response

router = APIRouter()


# ── Request / Response schemas ────────────────────────────────────────────────

class ChatRequest(BaseModel):
    user_id: int
    message: str


class ChatResponse(BaseModel):
    response: str
    emotion: str
    emotion_score: float
    risk: str


# ── Helper: fetch last N conversations for memory context ─────────────────────

def get_conversation_history(db: Session, user_id: int, limit: int = 5) -> list[dict]:
    rows = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.timestamp.desc())
        .limit(limit)
        .all()
    )
    # Return in chronological order (oldest first)
    return [{"message": r.message, "response": r.response} for r in reversed(rows)]


# ── POST /chat ─────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint.
    1. Validate input
    2. Detect emotion
    3. Assess risk
    4. Fetch conversation history (memory)
    5. Generate LLM response (or crisis override)
    6. Persist everything to DB
    7. Return response
    """
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Auto-create user if not found (convenience for demo)
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        user = User(id=req.user_id, name=f"User{req.user_id}", email=f"user{req.user_id}@demo.local")
        db.add(user)
        db.commit()

    # ── Step 1: Emotion detection ─────────────────────────────────────────────
    emotion_result = detect_emotion(message)
    emotion_label  = emotion_result["emotion"]
    emotion_score  = emotion_result["score"]

    # ── Step 2: Risk assessment ───────────────────────────────────────────────
    risk_result = assess_risk(message)
    risk_level  = risk_result["risk_level"]

    # ── Step 3: Conversation history (memory) ─────────────────────────────────
    history = get_conversation_history(db, req.user_id)

    # ── Step 4: Generate response ─────────────────────────────────────────────
    ai_response = generate_response(message, emotion_label, risk_level, history)

    # ── Step 5: Persist to database ───────────────────────────────────────────
    db.add(Conversation(
        user_id=req.user_id,
        message=message,
        response=ai_response,
        emotion=emotion_label,
        risk=risk_level,
        timestamp=datetime.utcnow()
    ))
    db.add(EmotionLog(
        user_id=req.user_id,
        emotion=emotion_label,
        score=emotion_score,
        timestamp=datetime.utcnow()
    ))
    db.add(RiskLog(
        user_id=req.user_id,
        risk_level=risk_level,
        message=message,
        timestamp=datetime.utcnow()
    ))
    db.commit()

    return ChatResponse(
        response=ai_response,
        emotion=emotion_label,
        emotion_score=emotion_score,
        risk=risk_level
    )


# ── GET /history/{user_id} ────────────────────────────────────────────────────

@router.get("/history/{user_id}")
def get_history(user_id: int, limit: int = 20, db: Session = Depends(get_db)):
    """Return recent conversation history for a user."""
    rows = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "message": r.message,
            "response": r.response,
            "emotion": r.emotion,
            "risk": r.risk,
            "timestamp": r.timestamp.isoformat()
        }
        for r in reversed(rows)
    ]
