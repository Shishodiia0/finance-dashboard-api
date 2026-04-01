from datetime import date
from typing import List, Optional
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from src.models.financial_record import FinancialRecord, RecordType
from src.schemas.dashboard import DashboardSummary, CategoryTotal, MonthlyTrend, WeeklyTrend


def _base_query(db: Session, date_from: Optional[date], date_to: Optional[date]):
    q = db.query(FinancialRecord).filter(FinancialRecord.is_deleted.is_(False))
    if date_from:
        q = q.filter(FinancialRecord.date >= date_from)
    if date_to:
        q = q.filter(FinancialRecord.date <= date_to)
    return q


def get_summary(db: Session, date_from: Optional[date] = None, date_to: Optional[date] = None) -> DashboardSummary:
    row = _base_query(db, date_from, date_to).with_entities(
        func.coalesce(func.sum(case((FinancialRecord.type == RecordType.income, FinancialRecord.amount), else_=0)), 0).label("income"),
        func.coalesce(func.sum(case((FinancialRecord.type == RecordType.expense, FinancialRecord.amount), else_=0)), 0).label("expenses"),
    ).one()
    return DashboardSummary(
        total_income=row.income,
        total_expenses=row.expenses,
        net_balance=row.income - row.expenses,
    )


def get_category_totals(db: Session, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[CategoryTotal]:
    rows = (
        _base_query(db, date_from, date_to)
        .with_entities(FinancialRecord.category, func.sum(FinancialRecord.amount).label("total"))
        .group_by(FinancialRecord.category)
        .order_by(func.sum(FinancialRecord.amount).desc())
        .all()
    )
    return [CategoryTotal(category=r.category, total=r.total) for r in rows]


def get_monthly_trends(db: Session, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[MonthlyTrend]:
    rows = (
        _base_query(db, date_from, date_to)
        .with_entities(
            func.to_char(FinancialRecord.date, "YYYY-MM").label("month"),
            func.coalesce(func.sum(case((FinancialRecord.type == RecordType.income, FinancialRecord.amount), else_=0)), 0).label("income"),
            func.coalesce(func.sum(case((FinancialRecord.type == RecordType.expense, FinancialRecord.amount), else_=0)), 0).label("expenses"),
        )
        .group_by("month")
        .order_by("month")
        .all()
    )
    return [MonthlyTrend(month=r.month, income=r.income, expenses=r.expenses) for r in rows]


def get_weekly_trends(db: Session, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[WeeklyTrend]:
    rows = (
        _base_query(db, date_from, date_to)
        .with_entities(
            func.to_char(FinancialRecord.date, "IYYY-\"W\"IW").label("week"),
            func.coalesce(func.sum(case((FinancialRecord.type == RecordType.income, FinancialRecord.amount), else_=0)), 0).label("income"),
            func.coalesce(func.sum(case((FinancialRecord.type == RecordType.expense, FinancialRecord.amount), else_=0)), 0).label("expenses"),
        )
        .group_by("week")
        .order_by("week")
        .all()
    )
    return [WeeklyTrend(week=r.week, income=r.income, expenses=r.expenses) for r in rows]
def get_weekly_trends(db: Session, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[WeeklyTrend]:
    dialect = db.bind.dialect.name
    if dialect == "postgresql":
        week_label = func.to_char(FinancialRecord.date, "IYYY-\"W\"IW")
    else:
        week_label = func.strftime("%Y-W%W", FinancialRecord.date)
    rows = (
        _base_query(db, date_from, date_to)
        .with_entities(
            week_label.label("week"),
            func.coalesce(func.sum(case((FinancialRecord.type == RecordType.income, FinancialRecord.amount), else_=0)), 0).label("income"),
            func.coalesce(func.sum(case((FinancialRecord.type == RecordType.expense, FinancialRecord.amount), else_=0)), 0).label("expenses"),
        )
        .group_by("week")
        .order_by("week")
        .all()
    )
    return [WeeklyTrend(week=r.week, income=r.income, expenses=r.expenses) for r in rows]


def get_recent_records(db: Session, limit: int = 5) -> List[FinancialRecord]:
    return (
        db.query(FinancialRecord)
        .filter(FinancialRecord.is_deleted.is_(False))
        .order_by(FinancialRecord.date.desc())
        .limit(limit)
        .all()
    )
