from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Dict
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Lab, UserLabProgress

router = APIRouter()

class LabItem(BaseModel):
    id: int
    title: str

class ProfileUpdateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class MessageResponse(BaseModel):
    message: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 현재 진행 중인 실습 조회
@router.get("/ongoing-labs/{user_id}", response_model=Dict[str, List[LabItem]])
def get_ongoing_labs(user_id: int, db: Session = Depends(get_db)):
    progresses = db.query(UserLabProgress).filter(
        UserLabProgress.user_id == user_id,
        UserLabProgress.status == "in-progress"
    ).all()

    labs = [LabItem(id=p.lab.id, title=p.lab.title) for p in progresses]
    return {"labs": labs}

# 완료된 실습 조회
@router.get("/completed-labs/{user_id}", response_model=Dict[str, List[LabItem]])
def get_completed_labs(user_id: int, db: Session = Depends(get_db)):
    progresses = db.query(UserLabProgress).filter(
        UserLabProgress.user_id == user_id,
        UserLabProgress.status == "completed"
    ).all()

    labs = [LabItem(id=p.lab.id, title=p.lab.title) for p in progresses]
    return {"labs": labs}

# 프로필 수정
@router.put("/profile/{user_id}", response_model=MessageResponse)
def update_profile(user_id: int, data: ProfileUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = data.username
    user.email = data.email
    user.password = data.password

    db.commit()
    return {"message": "Profile updated successfully"}
