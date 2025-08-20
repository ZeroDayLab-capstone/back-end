from sqlalchemy import Column, Integer, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# 사용자 테이블
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)
    gender = Column(Text, nullable=True)
    nationality = Column(Text, nullable=True)
    job = Column(Text, nullable=True)
    profile_photo = Column(Text, nullable=False, default="A")  # "A" or "B"

    progress = relationship("UserLabProgress", back_populates="user")

# 실습 문제 테이블
class Lab(Base):
    __tablename__ = "labs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    difficulty = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    hint = Column(Text)
    flag = Column(Text)

    progress = relationship("UserLabProgress", back_populates="lab")

# 실습 진행도 테이블
class UserLabProgress(Base):
    __tablename__ = "user_lab_progress"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    lab_id = Column(Integer, ForeignKey("labs.id"), primary_key=True)
    status = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)

    user = relationship("User", back_populates="progress")
    lab = relationship("Lab", back_populates="progress")

# 해설 테이블
class Explanation(Base):
    __tablename__ = "explanation"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(Text, nullable=False, unique=True)
    content = Column(Text, nullable=False)

# 공지사항 테이블
class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    date = Column(Text, nullable=False)


# 로그 테이블 
class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Text, nullable=False)
    action = Column(Text, nullable=False)
    user = Column(Text, nullable=False)

# Q&A 게시판 테이블
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