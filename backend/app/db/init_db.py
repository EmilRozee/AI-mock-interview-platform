from sqlalchemy.orm import Session

from app.models.role import Role

PREDEFINED_ROLES = [
    "Software Developer",
    "Data Analyst",
    "Product Manager",
    "Business Analyst",
    "QA Engineer",
]


def seed_roles(db: Session) -> None:
    existing = {role.role_name for role in db.query(Role).all()}
    missing = [Role(role_name=role_name) for role_name in PREDEFINED_ROLES if role_name not in existing]

    if missing:
        db.add_all(missing)
        db.commit()
