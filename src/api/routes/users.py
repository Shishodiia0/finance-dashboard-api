from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.dependencies import admin_only
from src.db.session import get_db
from src.models.user import User
from src.schemas.user import UserOut, UserUpdate
from src.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(admin_only)):
    return user_service.list_users(db)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    return user_service.get_user_or_404(db, user_id)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    return user_service.update_user(db, user_id, data)
