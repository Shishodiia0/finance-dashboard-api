from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float


class CategoryTotal(BaseModel):
    category: str
    total: float


class MonthlyTrend(BaseModel):
    month: str
    income: float
    expenses: float


class WeeklyTrend(BaseModel):
    week: str  # ISO week: "YYYY-WNN"
    income: float
    expenses: float
