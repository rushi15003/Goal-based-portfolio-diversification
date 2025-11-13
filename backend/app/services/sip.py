from typing import Dict
import math


DEFAULT_RETURN_EQUITY = 0.12
DEFAULT_RETURN_DEBT = 0.07
# Alts fixed 10%, split 5% Real Estate (8%), 5% Gold/Silver (5%) → avg 6.5%
DEFAULT_RETURN_ALTS = (0.08 + 0.05) / 2


def estimate_portfolio_return(allocation: Dict[str, float]) -> float:
    """
    Estimate annual expected portfolio return using default fallbacks.
    """
    equity = allocation.get("equity", 0.0)
    debt = allocation.get("debt", 0.0)
    alts = allocation.get("alts", 0.0)
    expected = (
        equity * DEFAULT_RETURN_EQUITY +
        debt * DEFAULT_RETURN_DEBT +
        alts * DEFAULT_RETURN_ALTS
    )
    return expected


def calculate_monthly_sip(target_corpus: int, horizon_years: int, annual_return: float) -> int:
    """
    Ordinary annuity formula:
    P = FV * r / ((1 + r)^n - 1)
    where r is monthly rate, n = months
    Rounded to nearest 100.
    """
    months = horizon_years * 12
    monthly_rate = annual_return / 12.0
    if monthly_rate <= 0 or months <= 0:
        return 0

    denominator = (1.0 + monthly_rate) ** months - 1.0
    if denominator <= 0:
        return 0

    p = target_corpus * monthly_rate / denominator
    # Round to nearest 100 for practicality
    rounded = int(100 * round(p / 100.0))
    return rounded


