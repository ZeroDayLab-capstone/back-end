from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

router = APIRouter(
    prefix="",
    tags=["authentication"],
    responses={401: {"description": "인증 실패"}, 500: {"description": "서버 오류"}}
)

# .env 로드
load_dotenv()

# 비밀번호 해시용
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정 (환경 변수에서 불러오기)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# 요청/응답 모델
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: str
    gender: str | None = None
    nationality: str | None = None
    job: str | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class MessageResponse(BaseModel):
    message: str

class TokenResponse(BaseModel):
    token: str

# DB 종속성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 유틸 함수
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 회원가입
@router.post(
    "/register", 
    response_model=MessageResponse,
    summary="사용자 회원가입",
    description="새로운 사용자를 등록합니다. 이메일, 비밀번호, 사용자명이 필요합니다.",
    response_description="회원가입 성공 메시지",
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "이미 등록된 이메일입니다"},
        422: {"description": "유효하지 않은 요청 데이터"}
    }
)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=409, detail="Email already registered.")

    hashed_pw = hash_password(data.password)
    new_user = User(email=data.email, password=hashed_pw, username=data.username,
    gender=data.gender, nationality=data.nationality, job=data.job)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

# 로그인
@router.post(
    "/login", 
    response_model=TokenResponse,
    summary="사용자 로그인",
    description="이메일과 비밀번호를 검증하고 접근 토큰을 발급합니다.",
    response_description="접근 토큰(JWT)",
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "이메일 또는 비밀번호가 올바르지 않습니다"},
        422: {"description": "유효하지 않은 요청 데이터"}
    }
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"token": access_token}

# JWT 토큰 인증 처리
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.get("/me",)
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "gender": current_user.gender,
        "nationality": current_user.nationality,
        "job": current_user.job
    }