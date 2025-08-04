from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal
from models import User

router = APIRouter(tags=["id-find"])

# DB 세션

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 요청 스키마
class IDFindRequest(BaseModel):
    username: str
    nationality: str
    job: str

# 응답 스키마
class IDFindResponse(BaseModel):
    message: str
    email_hint: str | None = None

# 이메일 마스킹 함수

def mask_email(email: str) -> str:
    local, domain = email.split("@")
    length = len(local)

    if length == 1:
        masked = "*"
    elif length == 2:
        masked = local[0] + "*"
    elif length == 3:
        masked = local[0] + "*" + local[2]
    elif length == 4:
        masked = local[0] + "**" + local[3]
    else:
        masked = local[:2] + "*" * (length - 4) + local[-2:]

    return f"{masked}@{domain}"

# 아이디(이메일) 찾기 API
@router.post("/auth/find-id", response_model=IDFindResponse)
def find_id(data: IDFindRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.username == data.username,
        User.nationality == data.nationality,
        User.job == data.job
    ).first()

    if not user:
        return {"message": "일치하는 계정을 찾을 수 없습니다."}

    email_hint = mask_email(user.email)
    return {
        "message": "일치하는 계정을 찾았습니다.",
        "email_hint": email_hint
    }
