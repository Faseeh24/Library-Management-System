from enum import Enum
from typing import Optional
from pydantic import BaseModel


class UserRole(str, Enum):
    admin = 'admin'
    librarian = 'librarian'
    member = 'member'


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: UserRole = UserRole.member
    registration_code: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class UserOut(BaseModel):
    id: int
    username: str
    role: str
