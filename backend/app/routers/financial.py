from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..schemas.financial import (
    MonthlyFinancialCreate,
    MonthlyFinancialModel,
    YearlySummary,
    YearlyComparison
)
from ..db.mongo import get_db
from ..utils.auth import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/api/financial", tags=["financial"])


def calculate_totals(record: dict) -> dict:
    """Calculate total income, expenses, and savings"""
    total_income = record.get("salary", 0) + record.get("bonus", 0) + record.get("other_income", 0)
    total_expenses = (
        record.get("rent", 0) +
        record.get("groceries", 0) +
        record.get("utilities", 0) +
        record.get("transportation", 0) +
        record.get("entertainment", 0) +
        record.get("healthcare", 0) +
        record.get("education", 0) +
        record.get("other_expenses", 0)
    )
    monthly_savings = total_income - total_expenses
    
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "monthly_savings": monthly_savings
    }


@router.post("", response_model=MonthlyFinancialModel)
async def create_financial_record(
    data: MonthlyFinancialCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new monthly financial record"""
    
    # Check if record already exists for this month/year
    existing = await db.financial_records.find_one({
        "user_id": current_user["email"],
        "year": data.year,
        "month": data.month
    })
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Record already exists for {data.month}/{data.year}"
        )
    
    # Calculate totals
    totals = calculate_totals(data.dict())
    
    # Create document
    doc = {
        **data.dict(),
        "user_id": current_user["email"],
        **totals,
        "created_at": datetime.utcnow(),
        "updated_at": None
    }
    
    result = await db.financial_records.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    
    return MonthlyFinancialModel(**doc)


@router.get("", response_model=List[MonthlyFinancialModel])
async def get_financial_records(
    year: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all financial records, optionally filtered by year"""
    
    query = {"user_id": current_user["email"]}
    if year:
        query["year"] = year
    
    cursor = db.financial_records.find(query).sort([("year", -1), ("month", -1)])
    records = await cursor.to_list(length=None)
    
    for record in records:
        record["id"] = str(record.pop("_id"))
    
    return [MonthlyFinancialModel(**r) for r in records]


@router.get("/summary/{year}", response_model=YearlySummary)
async def get_yearly_summary(
    year: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get summary for a specific year"""
    cursor = db.financial_records.find({
        "user_id": current_user["email"],
        "year": year
    })
    records = await cursor.to_list(length=None)
    
    if not records:
        raise HTTPException(status_code=404, detail=f"No records found for year {year}")
    
    total_income = sum(r["total_income"] for r in records)
    total_expenses = sum(r["total_expenses"] for r in records)
    total_savings = sum(r["monthly_savings"] for r in records)
    
    return YearlySummary(
        year=year,
        total_income=total_income,
        total_expenses=total_expenses,
        total_savings=total_savings,
        monthly_average_savings=total_savings / len(records) if records else 0,
        months_recorded=len(records)
    )


@router.get("/comparison/{year}", response_model=YearlyComparison)
async def get_yearly_comparison(
    year: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Compare savings between current year and previous year"""
    # Get current year data
    cursor = db.financial_records.find({
        "user_id": current_user["email"],
        "year": year
    })
    current_records = await cursor.to_list(length=None)
    
    if not current_records:
        raise HTTPException(status_code=404, detail=f"No records found for year {year}")
    
    current_savings = sum(r["monthly_savings"] for r in current_records)
    
    # Get previous year data
    previous_year = year - 1
    cursor = db.financial_records.find({
        "user_id": current_user["email"],
        "year": previous_year
    })
    previous_records = await cursor.to_list(length=None)
    
    if previous_records:
        previous_savings = sum(r["monthly_savings"] for r in previous_records)
        change_amount = current_savings - previous_savings
        change_percentage = (change_amount / previous_savings * 100) if previous_savings != 0 else 0
        trend = "increasing" if change_amount > 0 else "decreasing" if change_amount < 0 else "stable"
        
        return YearlyComparison(
            current_year=year,
            previous_year=previous_year,
            current_year_savings=current_savings,
            previous_year_savings=previous_savings,
            change_amount=change_amount,
            change_percentage=change_percentage,
            trend=trend
        )
    else:
        return YearlyComparison(
            current_year=year,
            previous_year=None,
            current_year_savings=current_savings,
            previous_year_savings=None,
            change_amount=None,
            change_percentage=None,
            trend="no_data"
        )


@router.put("/{record_id}", response_model=MonthlyFinancialModel)
async def update_financial_record(
    record_id: str,
    data: MonthlyFinancialCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update an existing financial record"""
    # Verify record exists and belongs to user
    existing = await db.financial_records.find_one({
        "_id": ObjectId(record_id),
        "user_id": current_user["email"]
    })
    
    if not existing:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Calculate new totals
    totals = calculate_totals(data.dict())
    
    # Update document
    update_data = {
        **data.dict(),
        **totals,
        "updated_at": datetime.utcnow()
    }
    
    await db.financial_records.update_one(
        {"_id": ObjectId(record_id)},
        {"$set": update_data}
    )
    
    updated = await db.financial_records.find_one({"_id": ObjectId(record_id)})
    updated["id"] = str(updated.pop("_id"))
    
    return MonthlyFinancialModel(**updated)


@router.delete("/{record_id}")
async def delete_financial_record(
    record_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete a financial record"""
    result = await db.financial_records.delete_one({
        "_id": ObjectId(record_id),
        "user_id": current_user["email"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return {"message": "Record deleted successfully"}

