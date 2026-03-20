from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.role import RoleRead, RoleSelectionRequest, RoleSelectionResponse

router = APIRouter()


@router.get("/", response_model=list[RoleRead])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).order_by(Role.role_name.asc()).all()


@router.get("/selected", response_model=list[RoleRead])
def selected_roles(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    roles = (
        db.query(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user.id)
        .order_by(Role.role_name.asc())
        .all()
    )
    return roles


@router.post("/select", response_model=RoleSelectionResponse)
def select_roles(
    payload: RoleSelectionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    roles = db.query(Role).filter(Role.id.in_(payload.role_ids)).all()
    if len(roles) != len(set(payload.role_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more roles are invalid")

    selected_ids = {role.id for role in roles}

    current_links = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    current_ids = {link.role_id for link in current_links}

    for role_id in current_ids - selected_ids:
        db.query(UserRole).filter(UserRole.user_id == user.id, UserRole.role_id == role_id).delete()

    for role_id in selected_ids - current_ids:
        db.add(UserRole(user_id=user.id, role_id=role_id, readiness_score=0.0, last_practiced_at=datetime.utcnow()))

    db.commit()

    return RoleSelectionResponse(selected_roles=roles)
