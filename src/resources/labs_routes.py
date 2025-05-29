from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Lab, UserLabProgress
from resources.auth_routes import get_current_user  # JWT 인증 함수
from pydantic import BaseModel

router = APIRouter()

# DB 세션 헬퍼 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 답안 제출용 요청 모델
class SubmitAnswerRequest(BaseModel):
    lab_id: int
    answer: str
    email: str = None  # email도 받을 수 있게 (선택)

# 정답 제출 라우트 (JWT + email 모두 지원)
@router.post("/submit")
def submit_answer(
    req: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 유저 정보 가져오기 (email 있으면 email 우선, 아니면 JWT 토큰)
    if req.email:
        user = db.query(User).filter(User.email == req.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="해당 이메일의 사용자가 없습니다.")
    else:
        user = current_user

    # 2. 진행중 실습 찾기
    prog = db.query(UserLabProgress).filter(
        UserLabProgress.user_id == user.id,
        UserLabProgress.lab_id == req.lab_id
    ).first()
    if not prog:
        raise HTTPException(404, "진행중인 실습이 없습니다.")

    # 3. 정답 체크(실습 테이블 answer 필드 비교, 필요 없으면 이 부분 빼도 됨)
    lab = db.query(Lab).filter(Lab.id == req.lab_id).first()
    if not lab:
        raise HTTPException(404, "해당 실습 문제 없음")

    is_correct = (lab.answer.strip().lower() == req.answer.strip().lower())
    # 4. 완료로 상태 변경
    prog.status = "completed"
    prog.is_correct = is_correct
    db.commit()
    return {"result": "완료", "정답여부": is_correct}
