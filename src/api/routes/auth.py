from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.core.dependencies import admin_only, get_current_user
from src.core.limiter import limiter
from src.db.session import get_db
from src.models.user import User
from src.schemas.user import LoginRequest, PasswordChange, TokenOut, UserCreate, UserOut
from src.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    return user_service.create_user(db, data)


@router.post("/login", response_model=TokenOut)
@limiter.limit("10/minute")
def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    token = user_service.authenticate_user(db, data.email, data.password)
    return TokenOut(access_token=token)


@router.patch("/me/password", status_code=204)
def change_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_service.change_password(db, current_user, data)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
