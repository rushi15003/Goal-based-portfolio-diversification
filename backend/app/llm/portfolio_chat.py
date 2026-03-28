"""
Portfolio Q&A helper using Gemini via google.generativeai.
Answers user questions about their specific portfolio context.
"""

from typing import List, Dict, Any

from app.core.config import settings

try:
    import google.generativeai as genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None


def _get_gemini_model():
    """
    Configure and return a Gemini GenerativeModel.

    Uses a stable, widely available text model id.
    """
    api_key = settings.gemini_api_key
    if not genai or not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        # Model id commonly available for text chat in google.generativeai
        return genai.GenerativeModel("gemini-1.5-flash-latest")
    except Exception:
        return None


def _summarise_portfolio(
    target_corpus: float,
    horizon: int,
    risk_profile: str,
    allocation: dict,
    sip: dict,
    portfolio_table: List[Dict[str, Any]],
) -> str:
    """Create a short textual summary of the portfolio."""
    equity_pct = allocation.get("equity", 0) * 100
    debt_pct = allocation.get("debt", 0) * 100
    alts_pct = allocation.get("alts", 0) * 100
    expected_return = sip.get("expected_return_annual", 0) * 100
    monthly_sip_amount = sip.get("monthly_sip", 0)

    lines = [
        f"Target corpus: ₹{target_corpus:,.0f}",
        f"Horizon: {horizon} years",
        f"Risk profile: {risk_profile}",
        f"Allocation: {equity_pct:.1f}% Equity, {debt_pct:.1f}% Debt, {alts_pct:.1f}% Alternatives (Gold/Silver)",
        f"Modelled annual return: {expected_return:.1f}%",
        f"Monthly SIP: ₹{monthly_sip_amount:,.0f}",
    ]

    if portfolio_table:
        lines.append("Key portfolio lines (asset_class / sub_category / allocation% / monthly SIP):")
        for row in portfolio_table[:5]:
            lines.append(
                f"- {row.get('asset_class')} / {row.get('sub_category')}: "
                f"{row.get('allocation', 0):.1f}% "
                f"(₹{row.get('monthly_sip', 0):,.0f} per month)"
            )

    return "\n".join(lines)


def answer_portfolio_question(
    question: str,
    target_corpus: float,
    horizon: int,
    risk_profile: str,
    allocation: dict,
    sip: dict,
    portfolio_table: list,
) -> str:
    """
    Answer a question about this specific portfolio using Gemini.
    Falls back with a clear message if Gemini is not available.
    """
    model = _get_gemini_model()
    summary = _summarise_portfolio(
        target_corpus=target_corpus,
        horizon=horizon,
        risk_profile=risk_profile,
        allocation=allocation,
        sip=sip,
        portfolio_table=portfolio_table,
    )

    if model is None:
        return (
            "Gemini is not configured correctly on the server. Please check GEMINI_API_KEY "
            "in the backend .env file and ensure the server has internet access."
        )

    prompt = (
        "You are a SEBI-style, long-term focused financial planning assistant.\n\n"
        "ONLY answer based on the user's portfolio context below. Do NOT invent portfolio numbers.\n"
        "Do NOT give tax, legal, or product-specific advice. Speak in simple, clear Indian retail\n"
        "investor language, and always remind the user that this is educational, not personalized advice.\n\n"
        "User's portfolio context:\n"
        f"{summary}\n\n"
        "User's question:\n"
        f"{question}\n\n"
        "Now answer the question in 2–4 short paragraphs or bullet points, referencing their\n"
        "allocations, SIP, horizon, and risk profile where relevant.\n"
    )

    try:
        response = model.generate_content(prompt)
        text = getattr(response, "text", "").strip()
        if not text:
            raise ValueError("Empty response from Gemini")
        return text
    except Exception as e:  # pragma: no cover - safety net
        return (
            "I tried to call Gemini but ran into an error on the server:\n"
            f"{type(e).__name__}: {e}\n\n"
            "Your portfolio and question were received correctly, but the AI call failed. "
            "Please check server logs, GEMINI_API_KEY, and network connectivity."
        )

