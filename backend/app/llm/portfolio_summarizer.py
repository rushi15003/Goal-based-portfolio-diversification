"""
LLM-based Portfolio Summarizer
Generates natural language summaries of portfolio allocations
"""

def generate_portfolio_summary(
    target_corpus: float,
    horizon: int,
    risk_profile: str,
    allocation: dict,
    sip: dict,
    portfolio_table: list
) -> str:
    """
    Generate a concise AI-powered summary of the portfolio allocation.
    """
    
    # Extract key metrics
    equity_pct = allocation.get("equity", 0) * 100
    debt_pct = allocation.get("debt", 0) * 100
    alts_pct = allocation.get("alts", 0) * 100
    expected_return = sip.get("expected_return_annual", 0) * 100
    monthly_sip_amount = sip.get("monthly_sip", 0)
    
    # Calculate total investment
    total_investment = monthly_sip_amount * 12 * horizon
    wealth_multiplier = target_corpus / total_investment if total_investment > 0 else 0
    
    # Generate concise insights
    risk_insight = _get_concise_risk_insight(risk_profile, equity_pct)
    strategy_insight = _get_concise_strategy(horizon, wealth_multiplier)
    
    # Compose a brief summary
    summary = f"""**AI Portfolio Insights**

Your {risk_profile.lower()} portfolio with {equity_pct:.0f}% equity and {debt_pct:.0f}% debt is designed for a {horizon}-year horizon. {risk_insight}

By investing ₹{monthly_sip_amount:,.0f} monthly, you're projected to grow your investment {wealth_multiplier:.1f}x to reach ₹{target_corpus:,.0f}. {strategy_insight}

**Key Advice:** Maintain consistent SIP contributions, review annually, and stay disciplined through market cycles for optimal results.
"""
    
    return summary


def _get_concise_risk_insight(risk_profile: str, equity_pct: float) -> str:
    """Generate concise risk insight"""
    if risk_profile == "Conservative":
        return "This allocation prioritizes stability and capital preservation with lower volatility."
    elif risk_profile == "Moderate":
        return "This balanced approach offers reasonable growth potential while managing downside risk."
    else:  # Aggressive
        return "This growth-focused strategy maximizes long-term wealth creation through higher equity exposure."


def _get_concise_strategy(horizon: int, wealth_multiplier: float) -> str:
    """Generate concise strategy insight"""
    if horizon <= 3:
        return "Your short-term focus emphasizes capital safety with steady returns."
    elif horizon <= 7:
        return "Your medium-term horizon allows you to benefit from market cycles while managing risk."
    else:
        if wealth_multiplier >= 2.5:
            return "Your long investment horizon enables powerful compounding for substantial wealth creation."
        else:
            return "Your timeline provides flexibility to navigate market volatility effectively."

