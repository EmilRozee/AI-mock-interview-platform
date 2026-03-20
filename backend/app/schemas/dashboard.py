from datetime import datetime
from typing import List

from pydantic import BaseModel


class RoleProgress(BaseModel):
    role_id: int
    role_name: str
    readiness_score: float
    average_score: float
    consistency_sessions: int
    consistency_percent: float
    categories_covered: int
    coverage_percent: float
    weak_areas: List[str]
    last_practiced_date: datetime
    trend: str
    trend_delta: float


class DashboardResponse(BaseModel):
    roles: List[RoleProgress]


class ReadinessHistoryPoint(BaseModel):
    date: str
    average_score: float


class CategoryTrend(BaseModel):
    category: str
    average_score: float


class RoleHistoryResponse(BaseModel):
    role_id: int
    role_name: str
    history: List[ReadinessHistoryPoint]
    category_trends: List[CategoryTrend]
