from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(100), unique=True, nullable=False)

    users = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    sessions = relationship("InterviewSession", back_populates="role", cascade="all, delete-orphan")
