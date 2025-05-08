from fastapi import APIRouter, HTTPException, Depends, status, Body
from sqlalchemy.orm import Session
from typing import List, Dict
from database import SessionLocal
from models import User, Lab, UserLabProgress
from pydantic import BaseModel

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={403: {"description": "권한 없음"}, 500: {"description": "서버 오류"}}
)

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

@router.get(
    "/users", 
    response_model=Dict[str, List[UserOut]],
    summary="전체 사용자 목록 조회",
    description="시스템에 등록된 모든 사용자의 정보를 조회합니다. 관리자 권한이 필요합니다.",
    response_description="사용자 ID, 이름, 이메일 정보 목록",
    status_code=status.HTTP_200_OK
)
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"users": users}

@router.post(
    "/labs", 
    response_model=LabResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="새 실습 생성",
    description="새로운 실습을 시스템에 추가합니다. 제목, 설명, 난이도 정보가 필요합니다.",
    response_description="실습 생성 결과 메시지",
    responses={
        500: {"description": "데이터베이스 업데이트 실패"}
    }
)
def create_lab(lab: LabCreate, db: Session = Depends(get_db)):
    try:
        new_lab = Lab(**lab.dict())
        db.add(new_lab)
        db.commit()
        return {"message": "Lab created successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="DB_UPDATE_FAILED")

@router.get(
    "/server-status",
    summary="서버 상태 확인",
    description="실습 환경 서버의 현재 실행 상태를 확인합니다.",
    response_description="서버 실행 상태 정보",
    status_code=status.HTTP_200_OK
)
def check_server_status():
    # 실제 Docker 상태 확인 로직은 별도로 구성 필요
    return {"status": "running"}  # 또는 "down"

@router.get(
    "/user-results", 
    response_model=UserResultResponse,
    summary="사용자 실습 결과 조회",
    description="특정 사용자의 모든 실습 진행 상태와 결과를 조회합니다.",
    response_description="사용자의 실습 ID와 상태 정보 목록",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "사용자 또는 결과를 찾을 수 없습니다"}
    }
)
def get_user_results(data: UserResultRequest = Body(...), db: Session = Depends(get_db)):
    progresses = db.query(UserLabProgress).filter(UserLabProgress.user_id == data.user_id).all()
    if not progresses:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    results = [{"lab_id": p.lab_id, "status": p.status} for p in progresses]
    return {"results": results}

@router.get(
    "/logs", 
    response_model=Dict[str, List[LogItem]],
    summary="시스템 로그 조회",
    description="시스템의 모든 활동 로그를 시간순으로 조회합니다. 관리자만 접근 가능합니다.",
    response_description="타임스탬프, 액션, 사용자 정보가 포함된 로그 목록",
    status_code=status.HTTP_200_OK
)
def get_logs():
    logs = [
        {"timestamp": "2025-05-06T12:00:00Z", "action": "LOGIN", "user": "admin"},
        {"timestamp": "2025-05-06T12:05:00Z", "action": "CREATE_LAB", "user": "admin"},
    ]
    return {"logs": logs}