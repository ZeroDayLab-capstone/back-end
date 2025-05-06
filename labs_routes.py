from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# 요청 모델
class SubmitAnswerRequest(BaseModel):
    lab_id: int
    answer: str

# 응답 모델
class URLResponse(BaseModel):
    url: str

class ResultResponse(BaseModel):
    result: str

class HintResponse(BaseModel):
    hint: str

class FeedbackResponse(BaseModel):
    feedback: str

# 더미 데이터
VALID_LABS = {
    1: {"answer": "admin", "hint": "Try SQL injection", "feedback": "This was a classic SQLi vulnerability."},
    2: {"answer": "cookie", "hint": "Check the cookies", "feedback": "This lab was about session handling."}
}

# 실습 환경 제공
@router.get("/environment", response_model=URLResponse)
def get_lab_environment():
    # 실제 환경이라면 Docker 컨테이너 상태 확인
    url = "http://lab.localhost:8001"  # 예시
    if not url:
        raise HTTPException(status_code=503, detail="Lab environment unavailable.")
    return {"url": url}

# 문제 제출
@router.post("/submit", response_model=ResultResponse)
def submit_answer(data: SubmitAnswerRequest):
    lab = VALID_LABS.get(data.lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found.")

    if not data.answer:
        raise HTTPException(status_code=400, detail="Answer is required.")

    if data.answer.strip().lower() == lab["answer"]:
        return {"result": "Correct!"}
    else:
        return {"result": "Incorrect. Try again."}

# 결과 확인
@router.get("/results", response_model=ResultResponse)
def get_results():
    # 실제라면 사용자별로 DB에서 가져옴
    return {"result": "Lab 1: Correct, Lab 2: In Progress"}

# 힌트 제공
@router.get("/hint", response_model=HintResponse)
def get_hint():
    return {"hint": "생각보다 쿠키가 힌트일지도?"}

# 피드백 제공
@router.get("/feedback", response_model=FeedbackResponse)
def get_feedback():
    return {"feedback": "이 실습은 인증 우회에 대한 이해를 평가합니다."}
