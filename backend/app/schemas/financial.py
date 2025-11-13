from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MonthlyFinancialCreate(BaseModel):
    """Schema for creating a monthly financial record"""
    user_id: str
    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)
    
    # Income details
    salary: float = Field(default=0, ge=0)
    bonus: float = Field(default=0, ge=0)
    other_income: float = Field(default=0, ge=0)
    
    # Expense details
    rent: float = Field(default=0, ge=0)
    groceries: float = Field(default=0, ge=0)
    utilities: float = Field(default=0, ge=0)
    transportation: float = Field(default=0, ge=0)
    entertainment: float = Field(default=0, ge=0)
    healthcare: float = Field(default=0, ge=0)
    education: float = Field(default=0, ge=0)
    other_expenses: float = Field(default=0, ge=0)


class MonthlyFinancialModel(MonthlyFinancialCreate):
    """Schema for monthly financial record response"""
    id: str
    total_income: float
    total_expenses: float
    monthly_savings: float
    created_at: datetime
    updated_at: Optional[datetime] = None


class YearlySummary(BaseModel):
    """Schema for yearly financial summary"""
    year: int
    total_income: float
    total_expenses: float
    total_savings: float
    monthly_average_savings: float
    months_recorded: int


class YearlyComparison(BaseModel):
    """Schema for year-over-year comparison"""
    current_year: int
    previous_year: Optional[int]
    current_year_savings: float
    previous_year_savings: Optional[float]
    change_amount: Optional[float]
    change_percentage: Optional[float]
    trend: str  # "increasing", "decreasing", or "no_data"

