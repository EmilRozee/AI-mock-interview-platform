from typing import List

from pydantic import BaseModel, Field


class RoleRead(BaseModel):
    id: int
    role_name: str

    class Config:
        from_attributes = True


class RoleSelectionRequest(BaseModel):
    role_ids: List[int] = Field(min_length=1)


class RoleSelectionResponse(BaseModel):
    selected_roles: List[RoleRead]
