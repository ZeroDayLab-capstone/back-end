from sqlalchemy import Column, Integer, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

# 사용자 테이블
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)

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


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False)
    feedback = Column(Text, nullable=False)

    # 로그 테이블 
class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Text, nullable=False)
    action = Column(Text, nullable=False)
    user = Column(Text, nullable=False)