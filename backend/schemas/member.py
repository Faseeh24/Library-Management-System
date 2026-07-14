from typing import Optional
from pydantic import BaseModel


class MemberCreate(BaseModel):
    name: str


class MemberUpdate(BaseModel):
    name: Optional[str] = None
