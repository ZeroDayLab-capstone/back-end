from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal
from models import Lab, UserLabProgress, Feedback
from typing import List

router = APIRouter(
    prefix="/labs",
    tags=["labs"],
    responses={500: {"description": "Internal Server Error"}}
)

# 요청/응답 모델
class SubmitAnswerRequest(BaseModel):
    user_id: int
    lab_id: int
    answer: str

class URLResponse(BaseModel):
    url: str

class ResultResponse(BaseModel):
    result: str
    explanation_topic: str | None = None

class HintResponse(BaseModel):
    hint: str

class FeedbackResponse(BaseModel):
    feedback: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 실습 환경 제공
@router.get(
    "/environment", 
    response_model=URLResponse,
    summary="실습 환경 접속 URL 조회",
    description="실습을 수행할 수 있는 환경의 URL을 제공합니다.",
    response_description="실습 환경 접속 URL",
    status_code=status.HTTP_200_OK
)
def get_lab_environment():
    url = "http://lab.localhost:8001"  # 예시 URL
    return {"url": url}

# 문제 제출 및 진행도 기록
@router.post(
    "/submit", 
    response_model=ResultResponse,
    summary="실습 문제 답안 제출",
    description="사용자가 제출한 답안을 검증하고 정답 여부를 반환합니다. 사용자의 진행 상태도 함께 기록됩니다.",
    response_description="답안 검증 결과",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "해당 실습을 찾을 수 없습니다"},
    }
)
def submit_answer(data: SubmitAnswerRequest, db: Session = Depends(get_db)):
    lab = db.query(Lab).filter(Lab.id == data.lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found.")

    progress = db.query(UserLabProgress).filter(
        UserLabProgress.user_id == data.user_id,
        UserLabProgress.lab_id == data.lab_id
    ).first()

    is_correct = data.answer.strip().lower() == lab.answer.strip().lower()

    if not progress:
        progress = UserLabProgress(
            user_id=data.user_id,
            lab_id=data.lab_id,
            status="completed" if is_correct else "in-progress",
            is_correct=is_correct
        )
        db.add(progress)
    else:
        progress.status = "completed" if is_correct else "in-progress"
        progress.is_correct = is_correct

    db.commit()

    if is_correct:
        return {
            "result": "Correct!",
            "explanation_topic": lab.title  # 해설 topic은 lab.title과 연결
        }
    else:
        return {
            "result": "Incorrect. Try again.",
            "explanation_topic": None
        }

# 힌트 제공
@router.get(
    "/hint/{lab_id}", 
    response_model=HintResponse,
    summary="실습 힌트 조회",
    description="특정 실습에 대한 힌트를 제공합니다.",
    response_description="실습 힌트 내용",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "힌트를 찾을 수 없습니다"},
    }
)
def get_hint(lab_id: int, db: Session = Depends(get_db)):
    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab or not lab.hint:
        raise HTTPException(status_code=404, detail="Hint not available.")
    return {"hint": lab.hint}

# 피드백 제공
@router.get(
    "/feedback/{lab_id}", 
    response_model=FeedbackResponse,
    summary="실습 피드백 조회",
    description="특정 실습에 대한 피드백 정보를 제공합니다.",
    response_description="실습 피드백 내용",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "피드백을 찾을 수 없습니다"},
    }
)
def get_feedback(lab_id: int, db: Session = Depends(get_db)):
    feedback = db.query(Feedback).filter(Feedback.lab_id == lab_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found.")
    return {"feedback": feedback.feedback}

# 결과 요약
@router.get(
    "/results/{user_id}", 
    response_model=List[ResultResponse],
    summary="사용자의 실습 결과 요약",
    description="특정 사용자의 모든 실습 결과와 진행 상태를 요약하여 반환합니다.",
    response_description="모든 실습에 대한 결과 요약 목록",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "사용자를 찾을 수 없습니다"},
    }
)
def get_results(user_id: int, db: Session = Depends(get_db)):
    progresses = db.query(UserLabProgress).filter(UserLabProgress.user_id == user_id).all()
    results = []
    for p in progresses:
        result_text = f"Lab {p.lab_id}: {'Correct' if p.is_correct else 'In Progress'}"
        results.append({"result": result_text})
    return results