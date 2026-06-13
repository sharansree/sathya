from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.auth import get_current_user
from app.services.rag import ask_sathya
from app.db.client import get_db
import json

router = APIRouter(prefix="/questions", tags=["questions"])
limiter = Limiter(key_func=get_remote_address)

class AskRequest(BaseModel):
    question: str

@router.post("/ask")
@limiter.limit("20/minute")
def ask(request: Request, body: AskRequest, current_user: dict = Depends(get_current_user)):
    question = body.question.strip()
    question = ' '.join(question.split())
    if len(question) < 5:
        raise HTTPException(status_code=400, detail="Question is too short")
    if len(question) > 1000:
        raise HTTPException(status_code=400, detail="Question must be under 1000 characters")
    response = ask_sathya(question, current_user["sub"])
    return response

@router.get("/history")
def get_history(current_user: dict = Depends(get_current_user)):
    db = get_db()
    result = db.table("questions")\
        .select("id, question, answer, sources, created_at")\
        .eq("user_id", current_user["sub"])\
        .order("created_at", desc=True)\
        .limit(50)\
        .execute()
    questions = []
    for q in result.data:
        questions.append({
            "id": q["id"],
            "question": q["question"],
            "answer": q["answer"],
            "sources": json.loads(q["sources"]) if isinstance(q["sources"], str) else q["sources"],
            "created_at": q["created_at"]
        })
    return {"questions": questions}

@router.delete("/{question_id}")
def delete_question(question_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    result = db.table("questions")\
        .select("id")\
        .eq("id", question_id)\
        .eq("user_id", current_user["sub"])\
        .execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Question not found")
    db.table("questions").delete().eq("id", question_id).execute()
    return {"message": "Deleted"}