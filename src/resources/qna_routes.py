from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import timezone
from database import SessionLocal
from models import User, QnAPost, QnAComment
from resources.auth_routes import get_current_user

# ✅ 프론트 요구 경로에 맞춤
router = APIRouter(prefix="/qna/qna/posts", tags=["qna"])

# ---------- Schemas ----------
class PostCreate(BaseModel):
    title: str
    content: str

class CommentCreate(BaseModel):
    content: str

class PostListItem(BaseModel):
    id: int
    title: str
    author: str
    created_at: str
    comment_count: int = 0
    accepted: bool = False

    class Config:
        from_attributes = True

class CommentOut(BaseModel):
    id: int
    content: str
    author: str
    created_at: str

class PostDetail(BaseModel):
    id: int
    title: str
    author: str
    created_at: str
    content: str
    comments: List[CommentOut]

class MessageResponse(BaseModel):
    message: str

# ---------- DB Dependency ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Helpers ----------
def _utc_iso(dt) -> str:
    # created_at이 naive이면 UTC로 가정하고 Z 붙임
    if dt is None:
        return ""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

def _author_name_from_post(post: QnAPost) -> str:
    # 관계가 있으면 user.username, 없으면 문자열 필드로 폴백
    try:
        if getattr(post, "author", None) and getattr(post.author, "username", None):
            return post.author.username
    except Exception:
        pass
    # 모델에 author_name 같은 문자열 필드가 있다면 폴백
    if hasattr(post, "author_name") and post.author_name:
        return post.author_name
    # 마지막 폴백
    return "anonymous"

def _author_name_from_comment(c: QnAComment) -> str:
    try:
        if getattr(c, "author", None) and getattr(c.author, "username", None):
            return c.author.username
    except Exception:
        pass
    if hasattr(c, "author_name") and c.author_name:
        return c.author_name
    return "anonymous"

# ---------- Posts ----------
@router.get("/", response_model=List[PostListItem], summary="게시글 목록")
def list_posts(db: Session = Depends(get_db)):
    # comment_count를 N+1 없이 구하기
    counts = dict(
        db.query(QnAComment.post_id, func.count(QnAComment.id))
          .group_by(QnAComment.post_id)
          .all()
    )
    posts = db.query(QnAPost).order_by(QnAPost.id.desc()).all()
    items: List[PostListItem] = []
    for p in posts:
        items.append(PostListItem(
            id=p.id,
            title=p.title,
            author=_author_name_from_post(p),
            created_at=_utc_iso(p.created_at),
            comment_count=int(counts.get(p.id, 0)),
            accepted=bool(getattr(p, "accepted", False)),
        ))
    return items

@router.post("/", response_model=PostListItem, status_code=status.HTTP_201_CREATED, summary="게시글 작성")
def create_post(data: PostCreate,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    post = QnAPost(title=data.title, content=data.content, author_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return PostListItem(
        id=post.id,
        title=post.title,
        author=_author_name_from_post(post) or current_user.username,
        created_at=_utc_iso(post.created_at),
        comment_count=0,
        accepted=bool(getattr(post, "accepted", False)),
    )

@router.get("/{post_id}", response_model=PostDetail, summary="게시글 상세")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post: Optional[QnAPost] = db.query(QnAPost).filter(QnAPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="NOT_FOUND")

    # 댓글 한번에 읽고 변환
    comments = db.query(QnAComment).filter(QnAComment.post_id == post_id)\
                   .order_by(QnAComment.id.asc()).all()
    comments_out = [
        CommentOut(
            id=c.id,
            content=c.content,
            author=_author_name_from_comment(c),
            created_at=_utc_iso(c.created_at),
        ) for c in comments
    ]

    return PostDetail(
        id=post.id,
        title=post.title,
        author=_author_name_from_post(post),
        created_at=_utc_iso(post.created_at),
        content=post.content,
        comments=comments_out,
    )

@router.put("/{post_id}", response_model=MessageResponse, summary="게시글 수정")
def update_post(post_id: int,
                data: PostCreate,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    post = db.query(QnAPost).filter(QnAPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    if post.author_id != current_user.id and not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="PERMISSION_DENIED")
    post.title = data.title
    post.content = data.content
    db.commit()
    return {"message": "ok"}

@router.delete("/{post_id}", response_model=MessageResponse, summary="게시글 삭제")
def delete_post(post_id: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    post = db.query(QnAPost).filter(QnAPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    if post.author_id != current_user.id and not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="PERMISSION_DENIED")
    db.delete(post)
    db.commit()
    return {"message": "ok"}

# ---------- Comments ----------
@router.post("/{post_id}/comments", status_code=status.HTTP_201_CREATED, response_model=dict, summary="댓글 작성")
def add_comment(post_id: int,
                payload: CommentCreate,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    post = db.query(QnAPost).filter(QnAPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    cmt = QnAComment(content=payload.content, author_id=current_user.id, post_id=post_id)
    db.add(cmt)
    db.commit()
    db.refresh(cmt)
    return {"id": cmt.id}

@router.put("/comments/{comment_id}", response_model=MessageResponse, summary="댓글 수정")
def update_comment(comment_id: int,
                   payload: CommentCreate,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    cmt = db.query(QnAComment).filter(QnAComment.id == comment_id).first()
    if not cmt:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    if cmt.author_id != current_user.id and not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="PERMISSION_DENIED")
    cmt.content = payload.content
    db.commit()
    return {"message": "ok"}

@router.delete("/comments/{comment_id}", response_model=MessageResponse, summary="댓글 삭제")
def delete_comment(comment_id: int,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    cmt = db.query(QnAComment).filter(QnAComment.id == comment_id).first()
    if not cmt:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    if cmt.author_id != current_user.id and not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="PERMISSION_DENIED")
    db.delete(cmt)
    db.commit()
    return {"message": "ok"}