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

# 프로필 조회 응답 모델
class ProfileResponse(BaseModel):
    username: str
    email: EmailStr
    gender: str | None = None
    nationality: str | None = None
    job: str | None = None

# 진행 중 실습 목록 조회
@router.get(
    "/ongoing-labs/{email}",
    response_model=Dict[str, List[ProgressItem]],
    summary="사용자의 진행 중인 실습 목록 조회",
    description="사용자의 진행 상태가 'in-progress'인 lab_id 목록을 반환합니다.",
    status_code=status.HTTP_200_OK
)
def get_ongoing_labs(email: str, db: Session = Depends(get_db)):  # email로 수정
    user = db.query(User).filter(User.email == email).first()  # 이메일로 사용자 찾기
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    records = db.query(UserLabProgress).filter(
        UserLabProgress.user_id == user.id,  # user_id로 실습 목록 조회
        UserLabProgress.status == "in-progress"
    ).all()
    return {"labs": [{"lab_id": r.lab_id} for r in records]}

# 완료된 실습 목록 조회
@router.get(
    "/completed-labs/{email}",
    response_model=Dict[str, List[ProgressItem]],
    summary="사용자의 완료된 실습 목록 조회",
    description="사용자의 진행 상태가 'completed'인 lab_id 목록을 반환합니다.",
    status_code=status.HTTP_200_OK
)
def get_completed_labs(email: str, db: Session = Depends(get_db)):  # email로 수정
    user = db.query(User).filter(User.email == email).first()  # 이메일로 사용자 찾기
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    records = db.query(UserLabProgress).filter(
        UserLabProgress.user_id == user.id,  # user_id로 실습 목록 조회
        UserLabProgress.status == "completed"
    ).all()
    return {"labs": [{"lab_id": r.lab_id} for r in records]}

# 프로필 수정 엔드포인트 추가
@router.put(
    "/profile/{email}",
    response_model=MessageResponse,
    summary="사용자 프로필 수정",
    description="특정 사용자의 프로필을 수정합니다.",
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "사용자를 찾을 수 없습니다"}}
)
def update_profile(email: str, data: ProfileUpdateRequest, db: Session = Depends(get_db)):  # email로 수정
    user = db.query(User).filter(User.email == email).first()  # 이메일로 사용자 찾기
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 수정할 필드 업데이트
    try:
        user.username = data.username
        user.email = data.email
        user.password = hash_password(data.password)  # 비밀번호 해시 처리
        user.gender = data.gender
        user.nationality = data.nationality
        user.job = data.job
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating user: {str(e)}")

    db.commit()
    return {"message": "Profile updated successfully"}

# 프로필 조회 엔드포인트
@router.get(
    "/profile/{email}",
    response_model=ProfileResponse,
    summary="사용자 프로필 조회",
    description="특정 사용자의 프로필 정보를 반환합니다.",
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "사용자를 찾을 수 없습니다"}}
)
def get_profile(email: str, db: Session = Depends(get_db)):  # email로 수정
    user = db.query(User).filter(User.email == email).first()  # 이메일로 사용자 찾기
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ProfileResponse(
        username=user.username,
        email=user.email,
        gender=user.gender,
        nationality=user.nationality,
        job=user.job
    )
