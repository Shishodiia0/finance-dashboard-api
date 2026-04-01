from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.dependencies import admin_only, get_current_user
from src.db.session import get_db
from src.models.financial_record import RecordType
from src.models.user import User
from src.schemas.financial_record import RecordCreate, RecordFilters, RecordOut, RecordUpdate
from src.services import record_service

router = APIRouter(prefix="/records", tags=["records"])


@router.get("", response_model=List[RecordOut])
def list_records(
    type: Optional[RecordType] = Query(None),
    category: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    filters = RecordFilters(type=type, category=category, date_from=date_from, date_to=date_to)
    return record_service.list_records(db, filters, skip, limit)


@router.get("/{record_id}", response_model=RecordOut)
def get_record(record_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return record_service.get_record_or_404(db, record_id)


@router.post("", response_model=RecordOut, status_code=201)
def create_record(data: RecordCreate, db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    return record_service.create_record(db, data, current_user.id)


@router.patch("/{record_id}", response_model=RecordOut)
def update_record(record_id: int, data: RecordUpdate, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    return record_service.update_record(db, record_id, data)


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    record_service.soft_delete_record(db, record_id)
