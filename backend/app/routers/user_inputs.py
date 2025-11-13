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
)
from app.services.allocation import PortfolioAllocationSystem
from app.services.sip import estimate_portfolio_return, calculate_monthly_sip
from app.llm.portfolio_summarizer import generate_portfolio_summary

router = APIRouter(prefix="/inputs", tags=["inputs"])


@router.post("", response_model=UserInputResult)
async def create_user_input(payload: UserInputCreate, db=Depends(get_db)) -> Any:
    doc = {
        "target_corpus": payload.target_corpus,
        "horizon": payload.horizon,
        "risk_profile": payload.risk_profile,
        "timestamp": datetime.now(timezone.utc),
    }
    result = await db["user_inputs"].insert_one(doc)

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
    
    # Generate AI summary before building portfolio table
    ai_summary_temp = generate_portfolio_summary(
        target_corpus=payload.target_corpus,
        horizon=payload.horizon,
        risk_profile=payload.risk_profile,
        allocation=allocation_dict,
        sip={"expected_return_annual": expected_return, "monthly_sip": monthly_sip},
        portfolio_table=[]  # Will be populated below
    )

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

    # Generate final AI summary with complete portfolio table
    ai_summary = generate_portfolio_summary(
        target_corpus=payload.target_corpus,
        horizon=payload.horizon,
        risk_profile=payload.risk_profile,
        allocation=allocation_dict,
        sip={"expected_return_annual": expected_return, "monthly_sip": monthly_sip},
        portfolio_table=portfolio_table
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
async def get_user_inputs(db=Depends(get_db)) -> Any:
    """Retrieve all user inputs/goals"""
    cursor = db["user_inputs"].find().sort("timestamp", -1).limit(50)
    docs = await cursor.to_list(length=50)
    
    results = []
    for doc in docs:
        results.append(
            UserInputModel(
                id=str(doc["_id"]),
                target_corpus=doc["target_corpus"],
                horizon=doc["horizon"],
                risk_profile=doc["risk_profile"],
                timestamp=doc["timestamp"]
            )
        )
    
    return results


