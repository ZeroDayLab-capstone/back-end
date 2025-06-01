from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import SessionLocal
from models import Lab, UserLabProgress, User

router = APIRouter(
    prefix="/labs",
    tags=["labs"],
    responses={500: {"description": "Internal Server Error"}}
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 요청/응답 모델
class EnvironmentRequest(BaseModel):
    email: EmailStr
    lab_id: int

class SimpleResponse(BaseModel):
    status: str

class SubmitAnswerRequest(BaseModel):
    email: EmailStr
    lab_id: int
    is_correct: bool   # 프론트에서 판단해서 전달
    status: str        # "completed" or "in-progress"

# 실습 시작: in-progress 기록만 생성 (url X)
@router.post(
    "/environment",
    response_model=SimpleResponse,
    summary="실습 환경 시작(진행 상태만 기록)",
    description="이메일과 실습 ID만 받아 진행 상태를 'in-progress'로 기록. URL 반환 없음.",
    status_code=status.HTTP_200_OK
)
def start_lab(data: EnvironmentRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    prog = db.query(UserLabProgress).filter(
        UserLabProgress.user_id == user.id,
        UserLabProgress.lab_id == data.lab_id
    ).first()
    if not prog:
        prog = UserLabProgress(
            user_id=user.id,
            lab_id=data.lab_id,
            status="in-progress",
            is_correct=False
        )
        db.add(prog)
        db.commit()
    else:
        if prog.status != "in-progress":
            prog.status = "in-progress"
            prog.is_correct = False
            db.commit()
    return {"status": "in-progress"}

# 문제 제출: 결과만 기록 (프론트에서 정오/상태 판단)
@router.post(
    "/submit",
    response_model=SimpleResponse,
    summary="실습 문제 답안 제출",
    description="프론트에서 판단된 답안 결과를 저장합니다. status만 반환.",
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "실습을 찾을 수 없습니다"}}
)
def submit_answer(data: SubmitAnswerRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    prog = db.query(UserLabProgress).filter(
        UserLabProgress.user_id == user.id,
        UserLabProgress.lab_id == data.lab_id
    ).first()
    if not prog:
        prog = UserLabProgress(
            user_id=user.id,
            lab_id=data.lab_id,
            status=data.status,
            is_correct=data.is_correct
        )
        db.add(prog)
    else:
        prog.status = data.status
        prog.is_correct = data.is_correct
    db.commit()
    return {"status": data.status}
