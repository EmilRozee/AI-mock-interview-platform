from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.answer import Answer
from app.models.interview_session import InterviewSession
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.dashboard import CategoryTrend, DashboardResponse, ReadinessHistoryPoint, RoleHistoryResponse, RoleProgress
from app.services.readiness_service import calculate_readiness

router = APIRouter()


@router.get("/me", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    links = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    items = []

    for link in links:
        role = db.query(Role).filter(Role.id == link.role_id).first()
        readiness_data = calculate_readiness(db, user.id, link.role_id)
        if role:
            items.append(
                RoleProgress(
                    role_id=role.id,
                    role_name=role.role_name,
                    readiness_score=readiness_data["readiness_score"],
                    average_score=readiness_data["average_score"],
                    consistency_sessions=readiness_data["consistency_sessions"],
                    consistency_percent=readiness_data["consistency_percent"],
                    categories_covered=readiness_data["categories_covered"],
                    coverage_percent=readiness_data["coverage_percent"],
                    weak_areas=readiness_data["weak_areas"],
                    last_practiced_date=readiness_data["last_practiced_date"],
                    trend=readiness_data["trend"],
                    trend_delta=readiness_data["trend_delta"],
                )
            )

    return DashboardResponse(roles=items)


@router.get("/role-history/{role_id}", response_model=RoleHistoryResponse)
def get_role_history(
    role_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    link = db.query(UserRole).filter(UserRole.user_id == user.id, UserRole.role_id == role_id).first()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found in your profile")

    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    timeline_rows = (
        db.query(func.date(Answer.created_at).label("day"), func.avg(Answer.score).label("avg_score"))
        .join(InterviewSession, InterviewSession.session_id == Answer.session_id)
        .filter(InterviewSession.user_id == user.id, InterviewSession.role_id == role_id)
        .group_by(func.date(Answer.created_at))
        .order_by(func.date(Answer.created_at).asc())
        .all()
    )

    category_rows = (
        db.query(Answer.category, func.avg(Answer.score).label("avg_score"))
        .join(InterviewSession, InterviewSession.session_id == Answer.session_id)
        .filter(InterviewSession.user_id == user.id, InterviewSession.role_id == role_id)
        .group_by(Answer.category)
        .order_by(Answer.category.asc())
        .all()
    )

    history = [
        ReadinessHistoryPoint(
            date=row.day,
            average_score=round(float(row.avg_score), 2),
        )
        for row in timeline_rows
    ]
    category_trends = [
        CategoryTrend(
            category=row.category,
            average_score=round(float(row.avg_score), 2),
        )
        for row in category_rows
    ]

    return RoleHistoryResponse(
        role_id=role.id,
        role_name=role.role_name,
        history=history,
        category_trends=category_trends,
    )
