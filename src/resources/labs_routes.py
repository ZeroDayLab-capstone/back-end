from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal
from models import Lab, UserLabProgress

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
    user_id: int
    lab_id: int

class URLResponse(BaseModel):
    url: str

class SubmitAnswerRequest(BaseModel):
    user_id: int
    lab_id: int
    answer: str

class ResultResponse(BaseModel):
    status: str

# 실습 시작: in-progress 기록 생성
@router.post(
    "/environment",
    response_model=URLResponse,
    summary="실습 환경 접속 및 진행 시작",
    description="실습을 시작하면 진행 상태를 'in-progress'로 기록합니다.",
    status_code=status.HTTP_200_OK
)
def start_lab(data: EnvironmentRequest, db: Session = Depends(get_db)):
    url = "http://lab.localhost:8001"
    prog = db.query(UserLabProgress).filter(
        UserLabProgress.user_id == data.user_id,
        UserLabProgress.lab_id == data.lab_id
    ).first()
    if not prog:
        prog = UserLabProgress(
            user_id=data.user_id,
            lab_id=data.lab_id,
            status="in-progress",
            is_correct=False
        )
        db.add(prog)
        db.commit()
    return {"url": url}

# 문제 제출: 진행/완료 상태 업데이트
@router.post(
    "/submit",
    response_model=ResultResponse,
    summary="실습 문제 답안 제출",
    description="답안 검증 후 진행 상태를 업데이트합니다.",
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "실습을 찾을 수 없습니다"}}
)
def submit_answer(data: SubmitAnswerRequest, db: Session = Depends(get_db)):
    lab = db.query(Lab).filter(Lab.id == data.lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    prog = db.query(UserLabProgress).filter(
        UserLabProgress.user_id == data.user_id,
        UserLabProgress.lab_id == data.lab_id
    ).first()

    correct = data.answer.strip().lower() == lab.answer.strip().lower()
    status_str = "completed" if correct else "in-progress"

    if not prog:
        prog = UserLabProgress(
            user_id=data.user_id,
            lab_id=data.lab_id,
            status=status_str,
            is_correct=correct
        )
        db.add(prog)
    else:
        prog.status = status_str
        prog.is_correct = correct

    db.commit()
    return {"status": status_str}
