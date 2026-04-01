from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from src.models.financial_record import RecordType


class RecordCreate(BaseModel):
    amount: float
    type: RecordType
    category: str
    date: date
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v


class RecordUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[RecordType] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("amount must be greater than 0")
        return v


class RecordOut(BaseModel):
    id: int
    amount: float
    type: RecordType
    category: str
    date: date
    notes: Optional[str]
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RecordFilters(BaseModel):
    type: Optional[RecordType] = None
    category: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
