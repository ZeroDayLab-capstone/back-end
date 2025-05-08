from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from typing import List, Dict
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Announcement

router = APIRouter(
    tags=["main"],
    responses={500: {"description": "Internal Server Error"}},
)

class MenuItem(BaseModel):
    name: str
    link: str

class AnnouncementOut(BaseModel):
    title: str
    date: str

class IntroResponse(BaseModel):
    content: str

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
@router.get(
    "/intro",
    response_model=IntroResponse,
    summary="플랫폼 소개글 조회",
    description="플랫폼의 기본적인 소개 정보를 제공합니다.",
    response_description="소개글 내용",
    status_code=status.HTTP_200_OK
)
def get_intro():
    return {"content": "This platform provides hands-on security labs to learn web vulnerabilities."}

# 메뉴
@router.get(
    "/menu",
    response_model=Dict[str, List[MenuItem]],
    summary="메뉴 항목 목록 조회",
    description="웹 애플리케이션의 메인 메뉴 항목 목록을 반환합니다.",
    response_description="메뉴 이름과 링크 목록",
    status_code=status.HTTP_200_OK
)
def get_menu():
    return {"menu": MENU_ITEMS}

# 공지사항 (DB 기반)
@router.get(
    "/announcements", 
    response_model=List[AnnouncementOut],
    summary="공지사항 목록 조회",
    description="시스템에 등록된 모든 공지사항을 데이터베이스에서 조회하여 반환합니다.",
    response_description="공지사항 제목과 날짜 목록",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "공지사항이 없습니다"}
    }
)
def get_announcements(db: Session = Depends(get_db)):
    announcements = db.query(Announcement).all()
    return announcements