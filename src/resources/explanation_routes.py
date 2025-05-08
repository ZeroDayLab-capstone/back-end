from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal
from models import Explanation

router = APIRouter(
    prefix="/resources",
    tags=["explanation"],
    responses={500: {"description": "Internal Server Error"}}
)

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

@router.post(
    "/explanation", 
    response_model=ExplanationResponse,
    summary="보안 주제 설명 조회",
    description="요청된 보안 주제에 대한 상세 설명을 제공합니다.",
    response_description="주제에 대한 설명 내용",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "요청한 주제에 대한 설명을 찾을 수 없습니다"},
        422: {"description": "유효하지 않은 요청 형식"}
    }
)
def provide_explanation(request: ExplanationRequest, db: Session = Depends(get_db)):
    explanation = db.query(Explanation).filter(Explanation.topic == request.topic).first()
    if not explanation:
        raise HTTPException(status_code=404, detail="Explanation not found")
    return {"content": explanation.content}