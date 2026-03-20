from fastapi import APIRouter

from app.api.v1.endpoints import auth, dashboard, health, interview, roles

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(interview.router, prefix="/interview", tags=["Interview"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
