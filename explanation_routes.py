from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal
from models import Explanation


router = APIRouter()

class ExplanationRequest(BaseModel):
    topic: str

class ExplanationResponse(BaseModel):
    content: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from models import Explanation  # Guide = explanation 테이블로 연결됨

@router.post("/explanation", response_model=ExplanationResponse)
def provide_explanation(request: ExplanationRequest, db: Session = Depends(get_db)):
    explanation = db.query(Explanation).filter(Explanation.topic == request.topic).first()
    if not explanation:
        raise HTTPException(status_code=404, detail="Explanation not found")
    return {"content": explanation.content}

