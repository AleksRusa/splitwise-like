from typing import Optional
from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str
    description: str


class GroupChangeData(BaseModel):
    name: Optional[str]
    description: Optional[str]


class GroupOwner(BaseModel):
    group_owner_id: int
