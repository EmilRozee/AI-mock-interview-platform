from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.interview_session import InterviewSession
from app.models.user_role import UserRole

TOTAL_CATEGORIES = 4
CONSISTENCY_SESSION_TARGET = 10


def _trend_summary(scores: List[float]) -> tuple[str, float]:
    if len(scores) < 4:
        return "stable", 0.0

    midpoint = len(scores) // 2
    earlier = scores[:midpoint]
    recent = scores[midpoint:]

    if not earlier or not recent:
        return "stable", 0.0

    delta = (sum(recent) / len(recent)) - (sum(earlier) / len(earlier))
    if delta >= 0.5:
        return "improving", round(delta, 2)
    if delta <= -0.5:
        return "declining", round(delta, 2)
    return "stable", round(delta, 2)


def calculate_readiness(db: Session, user_id: int, role_id: int) -> Dict[str, Any]:
    rows = (
        db.query(Answer.score, Answer.category, Answer.session_id, Answer.created_at)
        .join(InterviewSession, InterviewSession.session_id == Answer.session_id)
        .filter(InterviewSession.user_id == user_id, InterviewSession.role_id == role_id)
        .order_by(Answer.created_at.asc())
        .all()
    )

    user_role = db.query(UserRole).filter(UserRole.user_id == user_id, UserRole.role_id == role_id).first()

    if not rows:
        if user_role:
            user_role.readiness_score = 0.0
            db.commit()
            return {
                "readiness_score": 0.0,
                "average_score": 0.0,
                "consistency_sessions": 0,
                "consistency_percent": 0.0,
                "categories_covered": 0,
                "coverage_percent": 0.0,
                "weak_areas": [],
                "last_practiced_date": user_role.last_practiced_at,
                "trend": "stable",
                "trend_delta": 0.0,
            }
        return {
            "readiness_score": 0.0,
            "average_score": 0.0,
            "consistency_sessions": 0,
            "consistency_percent": 0.0,
            "categories_covered": 0,
            "coverage_percent": 0.0,
            "weak_areas": [],
            "last_practiced_date": datetime.utcnow(),
            "trend": "stable",
            "trend_delta": 0.0,
        }

    avg_score = sum(row.score for row in rows) / len(rows)
    avg_component = (avg_score / 10.0) * 100.0

    session_count = len({row.session_id for row in rows})
    consistency_component = min(session_count / CONSISTENCY_SESSION_TARGET, 1.0) * 100.0

    categories = {row.category for row in rows}
    coverage_component = (len(categories) / TOTAL_CATEGORIES) * 100.0

    readiness = round(0.6 * avg_component + 0.2 * consistency_component + 0.2 * coverage_component, 2)

    category_avgs = (
        db.query(Answer.category, func.avg(Answer.score))
        .join(InterviewSession, InterviewSession.session_id == Answer.session_id)
        .filter(InterviewSession.user_id == user_id, InterviewSession.role_id == role_id)
        .group_by(Answer.category)
        .all()
    )
    weak_areas = [category for category, score in category_avgs if score < 6.0]

    last_practiced = max(row.created_at for row in rows)
    trend, trend_delta = _trend_summary([row.score for row in rows])

    if user_role:
        user_role.readiness_score = readiness
        user_role.last_practiced_at = last_practiced
        db.commit()

    return {
        "readiness_score": readiness,
        "average_score": round(avg_score, 2),
        "consistency_sessions": session_count,
        "consistency_percent": round(consistency_component, 2),
        "categories_covered": len(categories),
        "coverage_percent": round(coverage_component, 2),
        "weak_areas": weak_areas,
        "last_practiced_date": last_practiced,
        "trend": trend,
        "trend_delta": trend_delta,
    }
