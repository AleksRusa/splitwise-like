from typing import Optional
from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str
    description: str


class GroupData(BaseModel):
    name: Optional[str]
    description: Optional[str]
