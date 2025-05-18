from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import List, Dict
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, UserLabProgress
from passlib.context import CryptContext

router = APIRouter(
    prefix="/mypage",
    tags=["mypage"],
    responses={404: {"description": "Not found"}},
)

# 비밀번호 해시 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# DB 세션
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 진행 상태 반환 모델
class ProgressItem(BaseModel):
    lab_id: int

# 프로필 수정 요청 모델
class ProfileUpdateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    gender: str | None = None
    nationality: str | None = None
    job: str | None = None

# 공통 응답 모델
class MessageResponse(BaseModel):
    message: str

# 진행 중 실습 목록 조회
@router.get(
    "/ongoing-labs/{user_id}",
    response_model=Dict[str, List[ProgressItem]],
    summary="사용자의 진행 중인 실습 목록 조회",
    description="사용자의 진행 상태가 'in-progress'인 lab_id 목록을 반환합니다.",
    status_code=status.HTTP_200_OK
)
def get_ongoing_labs(user_id: int, db: Session = Depends(get_db)):
    records = db.query(UserLabProgress).filter(
        UserLabProgress.user_id == user_id,
        UserLabProgress.status == "in-progress"
    ).all()
    return {"labs": [{"lab_id": r.lab_id} for r in records]}

# 완료된 실습 목록 조회
@router.get(
    "/completed-labs/{user_id}",
    response_model=Dict[str, List[ProgressItem]],
    summary="사용자의 완료된 실습 목록 조회",
    description="사용자의 진행 상태가 'completed'인 lab_id 목록을 반환합니다.",
    status_code=status.HTTP_200_OK
)
def get_completed_labs(user_id: int, db: Session = Depends(get_db)):
    records = db.query(UserLabProgress).filter(
        UserLabProgress.user_id == user_id,
        UserLabProgress.status == "completed"
    ).all()
    return {"labs": [{"lab_id": r.lab_id} for r in records]}

# 프로필 수정
@router.put(
    "/profile/{user_id}",
    response_model=MessageResponse,
    summary="사용자 프로필 정보 수정",
    description="사용자의 프로필 정보(사용자 이름, 이메일, 비밀번호, 성별, 국적, 직업)를 업데이트합니다.",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "사용자를 찾을 수 없습니다"},
        400: {"description": "잘못된 요청 형식"}
    }
)
def update_profile(user_id: int, data: ProfileUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = data.username
    user.email = data.email
    user.password = hash_password(data.password)
    user.gender = data.gender
    user.nationality = data.nationality
    user.job = data.job

    db.commit()
    return {"message": "Profile updated successfully"}
