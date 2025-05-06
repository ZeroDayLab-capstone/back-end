from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from fastapi import APIRouter


router = APIRouter()

# 📦 요청/응답 모델 정의
class ExplanationRequest(BaseModel):
    user_id: int
    question_id: int
    answer: str

class ExplanationResponse(BaseModel):
    explanation: str


# ✅ 해설 제공 API
@router.post("/explantion", response_model=ExplanationResponse)
def provide_Explanation(request: ExplanationRequest) -> ExplanationResponse:
    """
    문제에 대한 해설 제공 (임시 로직)
    """
    explantion_msg =f"해설제공"
    return {"ㅌxplanation": explantion_msg}

