from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from typing import List

app = FastAPI()
router = APIRouter()

# ✅ 데이터 모델
class MenuItem(BaseModel):
    name: str
    link: str

class Announcement(BaseModel):
    title: str
    date: str

# 임시 데이터
MENU_ITEMS = [
    {"name": "Home", "link": "/"},
    {"name": "Labs", "link": "/labs"},
    {"name": "Login", "link": "/auth/login"},
]

ANNOUNCEMENTS = [
    {"title": "Welcome to the Platform!", "date": "2025-03-25"},
    {"title": "New Security Labs Added", "date": "2025-03-24"},
]

# API 엔드포인트
@router.get("/intro")
def get_intro():
    return {"content": "This platform provides hands-on security labs to learn web vulnerabilities."}

@router.get("/menu")
def get_menu():
    return {"menu": MENU_ITEMS}

@router.get("/announcements")
def get_announcements():
    return {"announcements": ANNOUNCEMENTS}

# ✅ 라우터 등록
app.include_router(router, prefix="/main")
