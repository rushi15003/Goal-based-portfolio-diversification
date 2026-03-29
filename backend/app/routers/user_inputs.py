from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from typing import Any
from bson import ObjectId

from app.db.mongo import get_db
from app.schemas.user_input import (
    UserInputCreate,
    UserInputModel,
    UserInputResult,
    AllocationModel,
    SIPResult,
    Breakdown,
    EquityBreakdown,
    AltsBreakdown,
    PortfolioQuestion,
    PortfolioAnswer,
)
from app.services.allocation import PortfolioAllocationSystem
from app.services.sip import estimate_portfolio_return, calculate_monthly_sip
from app.llm.portfolio_summarizer import generate_portfolio_summary
from app.utils.auth import get_current_user
from app.llm.portfolio_chat import answer_portfolio_question

router = APIRouter(prefix="/inputs", tags=["inputs"])


@router.post("", response_model=UserInputResult)
async def create_user_input(
    payload: UserInputCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
) -> Any:
    """
    Create a new goal/portfolio **for the currently authenticated user**.
    Each user only sees their own goals.
    """
    allocator = PortfolioAllocationSystem()
    strategic_alloc = allocator.rule_based_allocation(payload.horizon, payload.risk_profile)
    allocation_dict = {
        "equity": strategic_alloc.get("equity", 0.0),
        "debt": strategic_alloc.get("debt", 0.0),
        # Map gold + silver to legacy 'alts' for UI compatibility
        "alts": strategic_alloc.get("gold", 0.0) + strategic_alloc.get("silver", 0.0),
    }
    expected_return = estimate_portfolio_return(allocation_dict)
    monthly_sip = calculate_monthly_sip(payload.target_corpus, payload.horizon, expected_return)

    # Build portfolio table
    portfolio_df = allocator.construct_portfolio(
        payload.horizon,
        payload.risk_profile,
        payload.target_corpus,
        monthly_sip
    )
    # Prepare for API serialization (list of dicts, 'Allocation (%)', Asset Class, Category, Monthly SIP)
    portfolio_table = []
    for row in portfolio_df.to_dict(orient="records"):
        # Only expose keys we want
        portfolio_table.append({
            "asset_class": row["Category"],
            "sub_category": row["Asset Class"],
            "allocation": row["Allocation (%)"],
            "monthly_sip": row["Monthly Amount (₹)"] or 0,
        })

    # Persist full goal, scoped to user
    doc = {
        "user_id": current_user["email"],
        "target_corpus": payload.target_corpus,
        "horizon": payload.horizon,
        "risk_profile": payload.risk_profile,
        "timestamp": datetime.now(timezone.utc),
        "allocation": allocation_dict,
        "sip": {
            "expected_return_annual": expected_return,
            "monthly_sip": monthly_sip,
        },
        "portfolio_table": portfolio_table,
    }
    result = await db["user_inputs"].insert_one(doc)

    user_input = UserInputModel(
        id=str(result.inserted_id),
        target_corpus=payload.target_corpus,
        horizon=payload.horizon,
        risk_profile=payload.risk_profile,
        timestamp=doc["timestamp"],
    )
    allocation = AllocationModel(**allocation_dict)
    sip = SIPResult(expected_return_annual=expected_return, monthly_sip=monthly_sip)

    # Hybrid tactical breakdowns
    equity_bd_dict = allocator.get_equity_breakdown(strategic_alloc.get("equity", 0.0))
    alts_total = strategic_alloc.get("gold", 0.0) + strategic_alloc.get("silver", 0.0)
    alts_bd_dict = allocator.get_alternatives_breakdown(alts_total)

    equity_bd = EquityBreakdown(
        large_cap=equity_bd_dict.get("Large Cap", 0.0),
        mid_cap=equity_bd_dict.get("Mid Cap", 0.0),
        small_cap=equity_bd_dict.get("Small Cap", 0.0),
    )
    alts_bd = AltsBreakdown(
        gold=alts_bd_dict.get("Gold", 0.0),
        silver=alts_bd_dict.get("Silver", 0.0),
    )
    breakdown = Breakdown(equity=equity_bd, alts=alts_bd)

    notes = {
        "allocation_basis": "Hybrid system: Rule-based strategic (Equity/Debt/Gold/Silver) with ML+factor tactical layer; UI shows Gold+Silver as Alts.",
        "return_basis": "Fallback default annual returns used until data-driven estimates are enabled.",
    }

    # Generate final AI summary with complete portfolio table
    ai_summary = generate_portfolio_summary(
        target_corpus=payload.target_corpus,
        horizon=payload.horizon,
        risk_profile=payload.risk_profile,
        allocation=allocation_dict,
        sip={"expected_return_annual": expected_return, "monthly_sip": monthly_sip},
        portfolio_table=portfolio_table,
    )

    notes["ai_summary"] = ai_summary

    return UserInputResult(
        user_input=user_input,
        allocation=allocation,
        sip=sip,
        notes=notes,
        breakdown=breakdown,
        portfolio_table=portfolio_table,
    )


@router.get("", response_model=list[UserInputModel])
async def get_user_inputs(
    db=Depends(get_db),
    current_user=Depends(get_current_user),
) -> Any:
    """
    Retrieve all goals **for the currently authenticated user**.
    Other users' portfolios are not visible.
    """
    cursor = (
        db["user_inputs"]
        .find({"user_id": current_user["email"]})
        .sort("timestamp", -1)
        .limit(50)
    )
    docs = await cursor.to_list(length=50)

    results = []
    for doc in docs:
        results.append(
            UserInputModel(
                id=str(doc["_id"]),
                target_corpus=doc["target_corpus"],
                horizon=doc["horizon"],
                risk_profile=doc["risk_profile"],
                timestamp=doc["timestamp"],
            )
        )

    return results


@router.get("/stats")
async def get_user_goal_stats(
    db=Depends(get_db),
    current_user=Depends(get_current_user),
) -> Any:
    """
    Lightweight stats for the dashboard for the current user.
    Uses stored goals to compute:
    - totalGoals: number of goals
    - totalInvestment: sum of target corpus
    - portfolioValue: alias of totalInvestment (can evolve later)
    """
    cursor = db["user_inputs"].find({"user_id": current_user["email"]})
    docs = await cursor.to_list(length=None)

    total_goals = len(docs)
    total_investment = sum(doc.get("target_corpus", 0) for doc in docs)

    return {
        "totalGoals": total_goals,
        "totalInvestment": total_investment,
        "portfolioValue": total_investment,
    }


@router.post("/chat", response_model=PortfolioAnswer)
async def chat_about_portfolio(
    payload: PortfolioQuestion,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
) -> Any:
    """
    Answer a user's question **about their portfolio**.

    - If `goal_id` is provided, use that specific goal.
    - Otherwise, use the most recent goal for the current user.
    """
    query: dict[str, Any] = {"user_id": current_user["email"]}
    if payload.goal_id:
        try:
            query["_id"] = ObjectId(payload.goal_id)
        except Exception:
            return PortfolioAnswer(
                answer="I couldn't understand which goal you are referring to. Please try again from a freshly created portfolio."
            )

    # Find the relevant goal
    cursor = db["user_inputs"].find(query).sort("timestamp", -1).limit(1)
    docs = await cursor.to_list(length=1)
    if not docs:
        return PortfolioAnswer(
            answer="I couldn't find any saved portfolios for you yet. Please create a goal first, then ask questions about it."
        )

    doc = docs[0]

    allocation = doc.get("allocation") or {}
    sip = doc.get("sip") or {}
    portfolio_table = doc.get("portfolio_table") or []

    answer = answer_portfolio_question(
        question=payload.question,
        target_corpus=doc.get("target_corpus", 0),
        horizon=doc.get("horizon", 0),
        risk_profile=doc.get("risk_profile", "Moderate"),
        allocation=allocation,
        sip=sip,
        portfolio_table=portfolio_table,
        history=[h.model_dump(mode="json") for h in payload.history] if payload.history else None,
    )

    return PortfolioAnswer(answer=answer)
