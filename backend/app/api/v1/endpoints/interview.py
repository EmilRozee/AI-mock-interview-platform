import json
import random

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.answer import Answer
from app.models.interview_session import InterviewSession
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.interview import (
    EvaluationResponse,
    NextQuestionResponse,
    StartSessionRequest,
    StartSessionResponse,
    SubmitAnswerRequest,
)
from app.services.ai_service import evaluate_answer, generate_question
from app.services.readiness_service import calculate_readiness

router = APIRouter()
QUESTION_CATEGORIES = ["HR", "Technical", "Situational", "Project"]


@router.post("/sessions/start", response_model=StartSessionResponse)
def start_session(
    payload: StartSessionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    role_link = db.query(UserRole).filter(UserRole.user_id == user.id, UserRole.role_id == payload.role_id).first()
    if not role_link:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role is not selected in your profile",
        )

    role = db.query(Role).filter(Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    session = InterviewSession(user_id=user.id, role_id=payload.role_id)
    db.add(session)
    db.commit()
    db.refresh(session)

    category = random.choice(QUESTION_CATEGORIES)
    question = generate_question(role.role_name, category)

    return StartSessionResponse(session_id=session.session_id, role_id=payload.role_id, question=question, category=category)


@router.post("/sessions/{session_id}/answer", response_model=EvaluationResponse)
def submit_answer(
    session_id: int,
    payload: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    evaluation = evaluate_answer(payload.question, payload.answer, payload.category)

    answer = Answer(
        session_id=session_id,
        question=payload.question,
        answer=payload.answer,
        score=float(evaluation.get("score", 0)),
        category=str(evaluation.get("category", payload.category)),
        feedback=json.dumps(evaluation),
    )
    db.add(answer)
    db.commit()

    calculate_readiness(db, user.id, session.role_id)

    return EvaluationResponse(
        score=float(evaluation.get("score", 0)),
        strengths=list(evaluation.get("strengths", [])),
        weaknesses=list(evaluation.get("weaknesses", [])),
        missing_points=list(evaluation.get("missing_points", [])),
        ideal_answer=str(evaluation.get("ideal_answer", "")),
        category=str(evaluation.get("category", payload.category)),
        raw=evaluation,
    )


@router.post("/sessions/{session_id}/next-question", response_model=NextQuestionResponse)
def next_question(
    session_id: int,
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    role = db.query(Role).filter(Role.id == session.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    selected_category = category if category in QUESTION_CATEGORIES else random.choice(QUESTION_CATEGORIES)
    question = generate_question(role.role_name, selected_category)
    return NextQuestionResponse(question=question, category=selected_category)
