from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import SessionLocal
from models import User
from utils.email_sender import send_reset_code_email
from passlib.context import CryptContext
import random

router = APIRouter(tags=["password-reset"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
reset_codes = {}

# 요청 모델
class ResetCodeRequest(BaseModel):
    email: EmailStr

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str

# DB 세션
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 비밀번호 해싱
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# 1. 인증코드 발송
@router.post("/send-reset-code", summary="인증코드 발송", description="사용자의 이메일로 인증코드를 발송합니다.")
def send_reset_code(data: ResetCodeRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="등록된 사용자(아이디)가 없습니다.")

    code = str(random.randint(100000, 999999))
    reset_codes[data.email] = code

    success = send_reset_code_email(data.email, code)
    if success:
        return {"message": "인증코드가 해당 아이디(이메일)로 발송되었습니다."}
    else:
        raise HTTPException(status_code=500, detail="이메일 발송 실패")

# 2. 인증코드 확인
@router.post("/verify-reset-code", summary="인증코드 확인", description="사용자가 입력한 인증코드를 검증합니다.")
def verify_code(data: VerifyCodeRequest):
    saved_code = reset_codes.get(data.email)
    if saved_code != data.code:
        raise HTTPException(status_code=400, detail="인증코드가 일치하지 않습니다.")
    return {"message": "인증 성공"}

# 3. 비밀번호 재설정
@router.post("/reset-password", summary="비밀번호 재설정", description="인증된 사용자에게 새 비밀번호를 설정합니다.")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    if data.email not in reset_codes:
        raise HTTPException(status_code=403, detail="인증되지 않은 사용자입니다.")

    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    user.password = hash_password(data.new_password)
    db.commit()
    reset_codes.pop(data.email)

    return {"message": "비밀번호가 성공적으로 재설정되었습니다."}
