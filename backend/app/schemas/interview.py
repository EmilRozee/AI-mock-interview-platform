from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StartSessionRequest(BaseModel):
    role_id: int


class StartSessionResponse(BaseModel):
    session_id: int
    role_id: int
    question: str
    category: str


class SubmitAnswerRequest(BaseModel):
    question: str
    answer: str = Field(min_length=1)
    category: str


class EvaluationResponse(BaseModel):
    score: float
    strengths: List[str]
    weaknesses: List[str]
    missing_points: List[str]
    ideal_answer: str
    category: str
    raw: Optional[Dict[str, Any]] = None


class NextQuestionResponse(BaseModel):
    question: str
    category: str
