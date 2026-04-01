from typing import Optional
from pydantic import BaseModel, EmailStr
from src.models.user import Role


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: Role = Role.viewer


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
