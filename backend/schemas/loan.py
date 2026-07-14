from typing import Optional
from pydantic import BaseModel


class LoanCreate(BaseModel):
    book_id: int
    member_id: int


class LoanUpdate(BaseModel):
    book_id: Optional[int] = None
    member_id: Optional[int] = None
