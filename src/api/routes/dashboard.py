from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.dependencies import analyst_or_above
from src.db.session import get_db
from src.models.user import User
from src.schemas.dashboard import CategoryTotal, DashboardSummary, MonthlyTrend, WeeklyTrend
from src.schemas.financial_record import RecordOut
from src.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(analyst_or_above),
):
    return dashboard_service.get_summary(db, date_from, date_to)


@router.get("/categories", response_model=List[CategoryTotal])
def category_totals(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(analyst_or_above),
):
    return dashboard_service.get_category_totals(db, date_from, date_to)


@router.get("/trends", response_model=List[MonthlyTrend])
def monthly_trends(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(analyst_or_above),
):
    return dashboard_service.get_monthly_trends(db, date_from, date_to)


@router.get("/weekly", response_model=List[WeeklyTrend])
def weekly_trends(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(analyst_or_above),
):
    return dashboard_service.get_weekly_trends(db, date_from, date_to)


@router.get("/recent", response_model=List[RecordOut])
def recent_records(db: Session = Depends(get_db), _: User = Depends(analyst_or_above)):
    return dashboard_service.get_recent_records(db)
