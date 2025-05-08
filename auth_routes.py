# auth_routes.py (수정)
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from pydantic import BaseModel, EmailStr

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class MessageResponse(BaseModel):
    message: str

class TokenResponse(BaseModel):
    token: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=MessageResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=409, detail="Email already registered.")
    
    new_user = User(email=data.email, password=data.password, username=data.username)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

# 로그인
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"token": access_token}