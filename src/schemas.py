from pydantic import BaseModel, EmailStr
from typing import Optional

# 사용자
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# 실습 문제
class LabCreate(BaseModel):
    title: str
    description: Optional[str]
    difficulty: str

class LabItem(BaseModel):
    id: int
    title: str

# 실습 피드백/제출 관련
class SubmitAnswerRequest(BaseModel):
    lab_id: int
    answer: str

class ResultResponse(BaseModel):
    result: str

class URLResponse(BaseModel):
    url: str

class HintResponse(BaseModel):
    hint: str

class FeedbackResponse(BaseModel):
    feedback: str

#  진행도 갱신용은 모델 없이 내부에서 처리 가능

#  해설
class ExplanationCreate(BaseModel):
    topic: str
    content: str

class ExplanationRequest(BaseModel):
    topic: str

class ExplanationResponse(BaseModel):
    content: str

#  공지사항
class AnnouncementOut(BaseModel):
    title: str
    date: str

#  마이페이지
class ProfileUpdateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class MessageResponse(BaseModel):
    message: str

#  인증
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    token: str