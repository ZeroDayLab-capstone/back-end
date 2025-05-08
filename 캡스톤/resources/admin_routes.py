from fastapi import APIRouter, HTTPException, Depends, status, Body
from sqlalchemy.orm import Session
from typing import List, Dict
from database import SessionLocal
from models import User, Lab, UserLabProgress
from pydantic import BaseModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======= Pydantic Schemas =======

class UserOut(BaseModel):
    id: int
    username: str
    email: str

class LabCreate(BaseModel):
    title: str
    description: str
    difficulty: str

class LabResponse(BaseModel):
    message: str

class ResultItem(BaseModel):
    lab_id: int
    status: str

class UserResultRequest(BaseModel):
    user_id: int

class UserResultResponse(BaseModel):
    results: List[ResultItem]

class LogItem(BaseModel):
    timestamp: str
    action: str
    user: str

# ======= Admin API =======

@router.get("/users", response_model=Dict[str, List[UserOut]])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"users": users}


@router.post("/labs", response_model=LabResponse, status_code=status.HTTP_201_CREATED)
def create_lab(lab: LabCreate, db: Session = Depends(get_db)):
    try:
        new_lab = Lab(**lab.dict())
        db.add(new_lab)
        db.commit()
        return {"message": "Lab created successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="DB_UPDATE_FAILED")


@router.get("/server-status")
def check_server_status():
    # 실제 Docker 상태 확인 로직은 별도로 구성 필요
    return {"status": "running"}  # 또는 "down"


@router.get("/user-results", response_model=UserResultResponse)
def get_user_results(data: UserResultRequest = Body(...), db: Session = Depends(get_db)):
    progresses = db.query(UserLabProgress).filter(UserLabProgress.user_id == data.user_id).all()
    if not progresses:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    results = [{"lab_id": p.lab_id, "status": p.status} for p in progresses]
    return {"results": results}


@router.get("/logs", response_model=Dict[str, List[LogItem]])
def get_logs():
    logs = [
        {"timestamp": "2025-05-06T12:00:00Z", "action": "LOGIN", "user": "admin"},
        {"timestamp": "2025-05-06T12:05:00Z", "action": "CREATE_LAB", "user": "admin"},
    ]
    return {"logs": logs}
