from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import List, Dict
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Lab, UserLabProgress
from passlib.context import CryptContext

router = APIRouter(
    prefix="/mypage",
    tags=["mypage"],
    responses={404: {"description": "Not found"}},
)

class LabItem(BaseModel):
    id: int
    title: str

class ProfileUpdateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    gender: str | None = None
    nationality: str | None = None
    job: str | None = None

class MessageResponse(BaseModel):
    message: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)        

# 현재 진행 중인 실습 조회
@router.get(
    "/ongoing-labs/{user_id}", 
    response_model=Dict[str, List[LabItem]],
    summary="사용자의 진행 중인 실습 목록 조회",
    description="특정 사용자의 현재 진행 중인('in-progress' 상태) 실습 목록을 반환합니다.",
    response_description="진행 중인 실습의 ID와 제목 목록",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "사용자를 찾을 수 없습니다"},
    }
)
def get_ongoing_labs(user_id: int, db: Session = Depends(get_db)):
    progresses = db.query(UserLabProgress).filter(
        UserLabProgress.user_id == user_id,
        UserLabProgress.status == "in-progress"
    ).all()

    labs = [LabItem(id=p.lab.id, title=p.lab.title) for p in progresses]
    return {"labs": labs}

# 완료된 실습 조회
@router.get(
    "/completed-labs/{user_id}", 
    response_model=Dict[str, List[LabItem]],
    summary="사용자의 완료된 실습 목록 조회",
    description="특정 사용자의 완료된('completed' 상태) 실습 목록을 반환합니다.",
    response_description="완료된 실습의 ID와 제목 목록",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "사용자를 찾을 수 없습니다"},
    }
)
def get_completed_labs(user_id: int, db: Session = Depends(get_db)):
    progresses = db.query(UserLabProgress).filter(
        UserLabProgress.user_id == user_id,
        UserLabProgress.status == "completed"
    ).all()

    labs = [LabItem(id=p.lab.id, title=p.lab.title) for p in progresses]
    return {"labs": labs}

# 프로필 수정
@router.put(
    "/profile/{user_id}", 
    response_model=MessageResponse,
    summary="사용자 프로필 정보 수정",
    description="사용자의 프로필 정보(사용자 이름, 이메일, 비밀번호)를 업데이트합니다.",
    response_description="프로필 수정 결과 메시지",
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
    user.password = hash_password(data.password)  # 참고: 실제로는 비밀번호 해싱 처리 필요
    user.gender = data.gender
    user.nationality = data.nationality
    user.job = data.job

    db.commit()
    return {"message": "Profile updated successfully"}