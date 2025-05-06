from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite DB 경로
DATABASE_URL = "sqlite:///./websec.db"

# DB 연결 설정
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # SQLite 전용 옵션
)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 모델 생성
Base = declarative_base()
