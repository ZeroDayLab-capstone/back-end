from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Dict
from fastapi import APIRouter

router = APIRouter()
@router.get("/intro")
def get_intro():
    return {"content": "This platform provides hands-on security labs to learn web vulnerabilities."}

class LabItem(BaseModel):
    id: int
    title: str

class ProfileUpdateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class MessageResponse(BaseModel):
    message: str

# 더미 데이터 
ONGOING_LABS = [
    {"id": 1, "title": "XSS 실습"},
    {"id": 2, "title": "SQL Injection 실습"},
]

COMPLETED_LABS = [
    {"id": 3, "title": "CSRF 실습"},
]

DUMMY_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "1234"
}


@router.get("/ongoing-labs", response_model=Dict[str, List[LabItem]])
def get_ongoing_labs() -> dict:
    return {"labs": ONGOING_LABS}


@router.get("/completed-labs", response_model=Dict[str, List[LabItem]])
def get_completed_labs() -> dict:
    return {"labs": COMPLETED_LABS}


@router.put("/profile", response_model=MessageResponse)
def update_profile(data: ProfileUpdateRequest) -> dict:
    print(" 기존 유저 정보:", DUMMY_USER)
    print(" 받은 요청 데이터:", data.dict())


    if not data.username or not data.password:
        raise HTTPException(status_code=400, detail="Username and password are required.")

    DUMMY_USER["username"] = data.username
    DUMMY_USER["email"] = data.email
    DUMMY_USER["password"] = data.password

    return {"message": "Profile updated successfully"}
