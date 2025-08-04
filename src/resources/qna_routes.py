from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database import SessionLocal
from models import User
from resources.auth_routes import get_current_user
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# FastAPI 라우터
router = APIRouter(prefix="/qna/posts", tags=["qna"])

# ======================== DB 모델 ========================

class QnAPost(Base):
    __tablename__ = "qna_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    author = relationship("User")
    comments = relationship("QnAComment", back_populates="post")

class QnAComment(Base):
    __tablename__ = "qna_comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("qna_posts.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    author = relationship("User")
    post = relationship("QnAPost", back_populates="comments")

# ======================== Pydantic Schemas ========================

class PostCreate(BaseModel):
    title: str
    content: str

class PostOut(BaseModel):
    id: int
    title: str
    author: str
    created_at: str
    class Config:
        from_attributes = True

class PostDetail(PostOut):
    content: str
    comments: List[dict]

class CommentCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    message: str

# ======================== Dependency ========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================== 게시글 API ========================

@router.get(
    "/",
    response_model=dict,
    summary="게시글 목록 조회",
    description="전체 Q&A 게시글 목록을 반환합니다."
)
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(QnAPost).all()
    return {"posts": [
        PostOut(id=p.id, title=p.title, author=p.author.username, created_at=p.created_at.isoformat())
        for p in posts
    ]}

@router.post(
    "/",
    response_model=PostOut,
    status_code=201,
    summary="게시글 작성",
    description="새로운 Q&A 게시글을 작성합니다. (로그인 필요)"
)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_post = QnAPost(**post.dict(), author_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return PostOut(id=db_post.id, title=db_post.title, author=current_user.username, created_at=db_post.created_at.isoformat())

@router.get(
    "/{post_id}",
    response_model=PostDetail,
    summary="게시글 상세 조회",
    description="특정 게시글의 상세 내용을 댓글과 함께 반환합니다."
)
def get_post_detail(post_id: int, db: Session = Depends(get_db)):
    post = db.query(QnAPost).filter(QnAPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    comments = [{
        "id": c.id,
        "content": c.content,
        "author": c.author.username,
        "created_at": c.created_at.isoformat()
    } for c in post.comments]
    return PostDetail(id=post.id, title=post.title, author=post.author.username,
                      created_at=post.created_at.isoformat(), content=post.content, comments=comments)

@router.put(
    "/{post_id}",
    response_model=MessageResponse,
    summary="게시글 수정",
    description="특정 게시글을 수정합니다. (작성자만 가능)"
)
def update_post(post_id: int, data: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(QnAPost).filter(QnAPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="PERMISSION_DENIED")
    post.title = data.title
    post.content = data.content
    db.commit()
    return {"message": "Post updated"}

@router.delete(
    "/{post_id}",
    response_model=MessageResponse,
    summary="게시글 삭제",
    description="특정 게시글을 삭제합니다. (작성자만 가능)"
)
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(QnAPost).filter(QnAPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="PERMISSION_DENIED")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}

# ======================== 댓글 API ========================

@router.post(
    "/{post_id}/comments",
    response_model=dict,
    status_code=201,
    summary="댓글 작성",
    description="특정 게시글에 댓글을 작성합니다. (로그인 필요)"
)
def add_comment(post_id: int, comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(QnAPost).filter(QnAPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    new_comment = QnAComment(content=comment.content, author_id=current_user.id, post_id=post_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return {
        "id": new_comment.id,
        "content": new_comment.content,
        "author": current_user.username,
        "created_at": new_comment.created_at.isoformat()
    }

@router.put(
    "/comments/{comment_id}",
    response_model=MessageResponse,
    summary="댓글 수정",
    description="특정 댓글을 수정합니다. (작성자만 가능)"
)
def update_comment(comment_id: int, comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cmt = db.query(QnAComment).filter(QnAComment.id == comment_id).first()
    if not cmt:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    if cmt.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="PERMISSION_DENIED")
    cmt.content = comment.content
    db.commit()
    return {"message": "Comment updated"}

@router.delete(
    "/comments/{comment_id}",
    response_model=MessageResponse,
    summary="댓글 삭제",
    description="특정 댓글을 삭제합니다. (작성자만 가능)"
)
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cmt = db.query(QnAComment).filter(QnAComment.id == comment_id).first()
    if not cmt:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    if cmt.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="PERMISSION_DENIED")
    db.delete(cmt)
    db.commit()
    return {"message": "Comment deleted"}