from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal
from models import Lab, UserLabProgress, Feedback


router = APIRouter()

# 요청/응답 모델
class SubmitAnswerRequest(BaseModel):
    user_id: int
    lab_id: int
    answer: str

class URLResponse(BaseModel):
    url: str

class ResultResponse(BaseModel):
    result: str

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
@router.get("/environment", response_model=URLResponse)
def get_lab_environment():
    url = "http://lab.localhost:8001"  # 예시 URL
    return {"url": url}

# 문제 제출 및 진행도 기록
@router.post("/submit", response_model=ResultResponse)
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
    return {"result": "Correct!" if is_correct else "Incorrect. Try again."}

# 힌트 제공
@router.get("/hint/{lab_id}", response_model=HintResponse)
def get_hint(lab_id: int, db: Session = Depends(get_db)):
    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab or not lab.hint:
        raise HTTPException(status_code=404, detail="Hint not available.")
    return {"hint": lab.hint}

# 피드백 제공
@router.get("/feedback/{lab_id}", response_model=FeedbackResponse)
def get_feedback(lab_id: int, db: Session = Depends(get_db)):
    feedback = db.query(Feedback).filter(Feedback.lab_id == lab_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found.")
    return {"feedback": feedback.feedback}

# 결과 요약
@router.get("/results/{user_id}", response_model=list[ResultResponse])
def get_results(user_id: int, db: Session = Depends(get_db)):
    progresses = db.query(UserLabProgress).filter(UserLabProgress.user_id == user_id).all()
    results = []
    for p in progresses:
        result_text = f"Lab {p.lab_id}: {'Correct' if p.is_correct else 'In Progress'}"
        results.append({"result": result_text})
    return results
