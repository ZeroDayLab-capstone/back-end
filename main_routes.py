from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Announcement

router = APIRouter()

class MenuItem(BaseModel):
    name: str
    link: str

class AnnouncementOut(BaseModel):
    title: str
    date: str

MENU_ITEMS = [
    {"name": "Home", "link": "/"},
    {"name": "Labs", "link": "/labs"},
    {"name": "Login", "link": "/auth/login"},
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 소개글
@router.get("/intro")
def get_intro():
    return {"content": "This platform provides hands-on security labs to learn web vulnerabilities."}

# 메뉴
@router.get("/menu")
def get_menu():
    return {"menu": MENU_ITEMS}

# 공지사항 (DB 기반)
@router.get("/announcements", response_model=List[AnnouncementOut])
def get_announcements(db: Session = Depends(get_db)):
    announcements = db.query(Announcement).all()
    return announcements
