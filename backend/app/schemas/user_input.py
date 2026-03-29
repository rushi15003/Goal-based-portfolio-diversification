from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, List
from datetime import datetime


RiskProfile = Literal["Conservative", "Moderate", "Aggressive"]


class UserInputCreate(BaseModel):
    target_corpus: int = Field(gt=0)
    horizon: int = Field(ge=1, le=30)
    risk_profile: RiskProfile


class UserInputModel(BaseModel):
    id: str = Field(..., description="MongoDB document id as string")
    target_corpus: int
    horizon: int
    risk_profile: RiskProfile
    timestamp: datetime


class AllocationModel(BaseModel):
    equity: float
    debt: float
    alts: float


class SIPResult(BaseModel):
    expected_return_annual: float = Field(description="Annual expected return used, e.g., 0.112 for 11.2%")
    monthly_sip: int = Field(description="Rounded to nearest 100")


class EquityBreakdown(BaseModel):
    large_cap: float = 0.0
    mid_cap: float = 0.0
    small_cap: float = 0.0


class AltsBreakdown(BaseModel):
    gold: float = 0.0
    silver: float = 0.0


class Breakdown(BaseModel):
    equity: EquityBreakdown
    alts: AltsBreakdown


class UserInputResult(BaseModel):
    user_input: UserInputModel
    allocation: AllocationModel
    sip: SIPResult
    notes: Optional[Dict[str, str]] = None
    breakdown: Optional[Breakdown] = None
    portfolio_table: Optional[list] = None


class ChatMessage(BaseModel):
    role: Literal["user", "model"]
    parts: str


class PortfolioQuestion(BaseModel):
    """Question about a specific portfolio/goal."""

    question: str = Field(..., min_length=2, description="User's natural language question")
    goal_id: Optional[str] = Field(
        default=None,
        description="Optional goal/portfolio id; if omitted, the latest goal is used",
    )
    history: Optional[List[ChatMessage]] = Field(
        default=[],
        description="Previous chat messages in the conversation thread"
    )


class PortfolioAnswer(BaseModel):
    """AI answer to a portfolio question."""

    answer: str
