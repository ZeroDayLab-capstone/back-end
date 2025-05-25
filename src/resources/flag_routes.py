from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine("sqlite:///./flags.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Flag(Base):
    __tablename__ = "flags"
    id = Column(Integer, primary_key=True, index=True)
    flag = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/resources",
    tags=["flags"],
    responses={500: {"description": "Internal Server Error"}}
)

class FlagSubmit(BaseModel):
    flag: str

@router.post("/submit_flag")
def submit_flag(data: FlagSubmit):
    db = SessionLocal()
    try:
        flag_row = db.query(Flag).filter(Flag.flag == data.flag).first()
        if flag_row:
            return {"result": "정답입니다."}
        else:
            return {"result": "틀렸습니다."}
    finally:
        db.close()