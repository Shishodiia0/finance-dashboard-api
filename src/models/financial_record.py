from __future__ import annotations
import enum
from datetime import date, datetime
from typing import Optional
from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class RecordType(str, enum.Enum):
    income = "income"
    expense = "expense"


class FinancialRecord(Base):
    __tablename__ = "financial_records"
    __table_args__ = {"schema": "finance"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    type: Mapped[RecordType] = mapped_column(Enum(RecordType), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    owner_id: Mapped[int] = mapped_column(ForeignKey("finance.users.id"), nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="records")
