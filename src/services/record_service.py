from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.financial_record import FinancialRecord
from src.schemas.financial_record import RecordCreate, RecordUpdate, RecordFilters


def create_record(db: Session, data: RecordCreate, owner_id: int) -> FinancialRecord:
    record = FinancialRecord(**data.model_dump(), owner_id=owner_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_record_or_404(db: Session, record_id: int) -> FinancialRecord:
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted.is_(False),
    ).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


def list_records(db: Session, filters: RecordFilters, skip: int = 0, limit: int = 50) -> List[FinancialRecord]:
    q = db.query(FinancialRecord).filter(FinancialRecord.is_deleted.is_(False))
    if filters.type:
        q = q.filter(FinancialRecord.type == filters.type)
    if filters.category:
        q = q.filter(FinancialRecord.category.ilike(f"%{filters.category}%"))
    if filters.date_from:
        q = q.filter(FinancialRecord.date >= filters.date_from)
    if filters.date_to:
        q = q.filter(FinancialRecord.date <= filters.date_to)
    return q.order_by(FinancialRecord.date.desc()).offset(skip).limit(limit).all()


def update_record(db: Session, record_id: int, data: RecordUpdate) -> FinancialRecord:
    record = get_record_or_404(db, record_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


def soft_delete_record(db: Session, record_id: int) -> None:
    record = get_record_or_404(db, record_id)
    record.is_deleted = True
    db.commit()
