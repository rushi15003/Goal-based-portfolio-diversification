"""
Enhanced Portfolio Allocation System
=====================================
Integrates:
1. Rule-based strategic allocation (based on risk & horizon)
2. Hybrid ML + Multi-Factor tactical allocation (within asset classes)
3. Dynamic portfolio construction with rankings
"""

from typing import Literal, Dict, List, Tuple
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
try:
    import cloudpickle  # type: ignore
except Exception:  # pragma: no cover
    cloudpickle = None

# Type definitions
RiskProfile = Literal["Conservative", "Moderate", "Aggressive"]


class PortfolioAllocationSystem:
    """
    Complete portfolio allocation system combining rule-based and ML approaches
    """
    
    def __init__(self, scorer_path: str = 'hybrid_scorer.pkl'):
        """
        Initialize the allocation system
        
        Parameters:
        -----------
        scorer_path : str
            Path to the trained hybrid scorer object
        """
        # Resolve scorer path: if relative, resolve next to this file (services dir)
        base_dir = Path(__file__).parent
        sp = Path(scorer_path)
        if not sp.is_absolute():
            sp = base_dir / sp
        self.scorer_path = str(sp)
        self.scorer = None
        self.current_rankings = None
        
        # Asset class to ticker mapping
        self.asset_mapping = {
            'Large Cap': '^NSEI',
            'Mid Cap': 'MID150BEES.NS',
            'Small Cap': 'BSE-SMLCAP.BO',
            'Debt': 'LIQUIDBEES.NS',
            'Gold': 'GOLDBEES.NS',
            'Silver': 'SILVERBEES.NS'
        }
        
        # Load scorer if available
        self._load_scorer()
    
    def _load_scorer(self):
        """Load the hybrid scorer"""
        try:
            if Path(self.scorer_path).exists():
                # Prefer cloudpickle if available (handles notebook-defined classes)
                if cloudpickle is not None:
                    with open(self.scorer_path, 'rb') as f:
                        self.scorer = cloudpickle.load(f)
                else:
                    self.scorer = joblib.load(self.scorer_path)
                print(f"✓ Loaded hybrid scorer from {self.scorer_path}")
                
                # Get current rankings
                if hasattr(self.scorer, 'ranked_df') and self.scorer.ranked_df is not None:
                    self.current_rankings = self.scorer.ranked_df
                    print(f"✓ Current rankings loaded ({len(self.current_rankings)} assets)")
            else:
                print(f"⚠ Scorer file not found at {self.scorer_path}")
                print("  → Will use rule-based allocation only")
        except Exception as e:
            print(f"⚠ Error loading scorer: {e}")
            print("  → Will use rule-based allocation only")
    
    def rule_based_allocation(
        self, 
        horizon_years: int, 
        risk_profile: RiskProfile
    ) -> Dict[str, float]:
        """
        Strategic asset allocation based on horizon and risk profile
        
        Parameters:
        -----------
        horizon_years : int
            Investment horizon in years
        risk_profile : RiskProfile
            One of "Conservative", "Moderate", "Aggressive"
        
        Returns:
        --------
        Dict mapping asset classes to allocation percentages
        """
        # Determine time bucket
        if horizon_years < 3:
            bucket = "lt3"
        elif 3 <= horizon_years <= 7:
            bucket = "3to7"
        else:
            bucket = ">7"
        
        # Allocation grid
        grid = {
            "lt3": {
                "Conservative": {"equity": 0.15, "debt": 0.75, "gold": 0.05, "silver": 0.05},
                "Moderate":     {"equity": 0.25, "debt": 0.65, "gold": 0.05, "silver": 0.05},
                "Aggressive":   {"equity": 0.35, "debt": 0.55, "gold": 0.05, "silver": 0.05},
            },
            "3to7": {
                "Conservative": {"equity": 0.40, "debt": 0.50, "gold": 0.05, "silver": 0.05},
                "Moderate":     {"equity": 0.55, "debt": 0.35, "gold": 0.05, "silver": 0.05},
                "Aggressive":   {"equity": 0.65, "debt": 0.25, "gold": 0.05, "silver": 0.05},
            },
            ">7": {
                "Conservative": {"equity": 0.60, "debt": 0.30, "gold": 0.05, "silver": 0.05},
                "Moderate":     {"equity": 0.75, "debt": 0.15, "gold": 0.05, "silver": 0.05},
                "Aggressive":   {"equity": 0.85, "debt": 0.05, "gold": 0.05, "silver": 0.05},
            },
        }
        
        return grid[bucket][risk_profile]
    
    def get_equity_breakdown(
        self, 
        total_equity_allocation: float
    ) -> Dict[str, float]:
        """
        Break down equity allocation into Large/Mid/Small Cap based on ML rankings
        
        Parameters:
        -----------
        total_equity_allocation : float
            Total equity allocation (e.g., 0.85 for 85%)
        
        Returns:
        --------
        Dict with allocations for Large Cap, Mid Cap, Small Cap
        """
        if self.current_rankings is None:
            # Fallback: Equal weight or default split
            print("⚠ No rankings available, using default equity split")
            return {
                'Large Cap': total_equity_allocation * 0.50,  # 50% large
                'Mid Cap': total_equity_allocation * 0.30,    # 30% mid
                'Small Cap': total_equity_allocation * 0.20   # 20% small
            }
        
        # Get equity sub-categories from rankings
        equity_assets = ['Large Cap', 'Mid Cap', 'Small Cap']
        equity_rankings = self.current_rankings[
            self.current_rankings['asset_class'].isin(equity_assets)
        ].copy()
        
        if len(equity_rankings) == 0:
            print("⚠ No equity rankings found, using default split")
            return {
                'Large Cap': total_equity_allocation * 0.50,
                'Mid Cap': total_equity_allocation * 0.30,
                'Small Cap': total_equity_allocation * 0.20
            }
        
        # Use hybrid scores for proportional allocation
        # Higher score = higher allocation
        equity_rankings['weight'] = (
            equity_rankings['hybrid_score'] / equity_rankings['hybrid_score'].sum()
        )
        
        allocation = {}
        for _, row in equity_rankings.iterrows():
            allocation[row['asset_class']] = total_equity_allocation * row['weight']
        
        return allocation
    
    def get_alternatives_breakdown(
        self,
        total_alt_allocation: float
    ) -> Dict[str, float]:
        """
        Break down alternatives (gold/silver) based on rankings
        
        Parameters:
        -----------
        total_alt_allocation : float
            Total alternatives allocation
        
        Returns:
        --------
        Dict with allocations for Gold and Silver
        """
        if self.current_rankings is None:
            # Default: Equal split
            return {
                'Gold': total_alt_allocation * 0.5,
                'Silver': total_alt_allocation * 0.5
            }
        
        # Get alternatives from rankings
        alt_assets = ['Gold', 'Silver']
        alt_rankings = self.current_rankings[
            self.current_rankings['asset_class'].isin(alt_assets)
        ].copy()
        
        if len(alt_rankings) < 2:
            return {
                'Gold': total_alt_allocation * 0.5,
                'Silver': total_alt_allocation * 0.5
            }
        
        # Proportional allocation based on scores
        alt_rankings['weight'] = (
            alt_rankings['hybrid_score'] / alt_rankings['hybrid_score'].sum()
        )
        
        allocation = {}
        for _, row in alt_rankings.iterrows():
            allocation[row['asset_class']] = total_alt_allocation * row['weight']
        
        return allocation
    
    def construct_portfolio(
        self,
        horizon_years: int,
        risk_profile: RiskProfile,
        target_corpus: float,
        monthly_sip: float = None
    ) -> pd.DataFrame:
        """
        Construct complete portfolio with tactical allocation
        
        Parameters:
        -----------
        horizon_years : int
            Investment horizon
        risk_profile : RiskProfile
            Risk profile
        target_corpus : float
            Target amount (for display)
        monthly_sip : float, optional
            Monthly SIP amount (for display)
        
        Returns:
        --------
        DataFrame with complete portfolio breakdown
        """
        print(f"\n{'='*80}")
        print(f"CONSTRUCTING PORTFOLIO")
        print(f"{'='*80}")
        print(f"Horizon: {horizon_years} years | Risk: {risk_profile}")
        print(f"Target Corpus: ₹{target_corpus:,.0f}")
        if monthly_sip:
            print(f"Monthly SIP: ₹{monthly_sip:,.0f}")
        
        # Step 1: Get strategic allocation
        strategic = self.rule_based_allocation(horizon_years, risk_profile)
        
        print(f"\n--- STRATEGIC ALLOCATION (Rule-Based) ---")
        print(f"Equity: {strategic['equity']*100:.1f}%")
        print(f"Debt: {strategic['debt']*100:.1f}%")
        print(f"Gold: {strategic['gold']*100:.1f}%")
        print(f"Silver: {strategic['silver']*100:.1f}%")
        
        # Step 2: Break down equity using rankings
        equity_breakdown = self.get_equity_breakdown(strategic['equity'])
        
        print(f"\n--- TACTICAL EQUITY BREAKDOWN (Hybrid ML + Factors) ---")
        for asset_class, allocation in equity_breakdown.items():
            print(f"{asset_class}: {allocation*100:.2f}%")
        
        # Step 3: Break down alternatives
        total_alt = strategic['gold'] + strategic['silver']
        alt_breakdown = self.get_alternatives_breakdown(total_alt)
        
        print(f"\n--- ALTERNATIVES BREAKDOWN ---")
        for asset_class, allocation in alt_breakdown.items():
            print(f"{asset_class}: {allocation*100:.2f}%")
        
        # Step 4: Construct final portfolio
        portfolio_data = []
        
        # Add equity components
        for asset_class, allocation in equity_breakdown.items():
            ticker = self.asset_mapping.get(asset_class, 'N/A')
            rank = self._get_rank(asset_class)
            score = self._get_score(asset_class)
            
            portfolio_data.append({
                'Asset Class': asset_class,
                'Category': 'Equity',
                'Ticker': ticker,
                'Allocation (%)': allocation * 100,
                'Monthly Amount (₹)': monthly_sip * allocation if monthly_sip else None,
                'Rank': rank,
                'Score': score
            })
        
        # Add debt
        debt_ticker = self.asset_mapping.get('Debt', 'N/A')
        debt_rank = self._get_rank('Debt')
        debt_score = self._get_score('Debt')
        
        portfolio_data.append({
            'Asset Class': 'Debt',
            'Category': 'Debt',
            'Ticker': debt_ticker,
            'Allocation (%)': strategic['debt'] * 100,
            'Monthly Amount (₹)': monthly_sip * strategic['debt'] if monthly_sip else None,
            'Rank': debt_rank,
            'Score': debt_score
        })
        
        # Add alternatives
        for asset_class, allocation in alt_breakdown.items():
            ticker = self.asset_mapping.get(asset_class, 'N/A')
            rank = self._get_rank(asset_class)
            score = self._get_score(asset_class)
            
            portfolio_data.append({
                'Asset Class': asset_class,
                'Category': 'Alternatives',
                'Ticker': ticker,
                'Allocation (%)': allocation * 100,
                'Monthly Amount (₹)': monthly_sip * allocation if monthly_sip else None,
                'Rank': rank,
                'Score': score
            })
        
        portfolio_df = pd.DataFrame(portfolio_data)
        
        # Sort by allocation
        portfolio_df = portfolio_df.sort_values('Allocation (%)', ascending=False)
        
        return portfolio_df
    
    def _get_rank(self, asset_class: str) -> int:
        """Get rank for an asset class"""
        if self.current_rankings is None:
            return None
        
        row = self.current_rankings[self.current_rankings['asset_class'] == asset_class]
        if len(row) > 0:
            return int(row.iloc[0]['rank'])
        return None
    
    def _get_score(self, asset_class: str) -> float:
        """Get hybrid score for an asset class"""
        if self.current_rankings is None:
            return None
        
        row = self.current_rankings[self.current_rankings['asset_class'] == asset_class]
        if len(row) > 0:
            return float(row.iloc[0]['hybrid_score'])
        return None
    
    def display_portfolio(self, portfolio_df: pd.DataFrame):
        """Display portfolio in formatted table"""
        print(f"\n{'='*80}")
        print("FINAL PORTFOLIO")
        print(f"{'='*80}\n")
        
        # Group by category
        for category in ['Equity', 'Debt', 'Alternatives']:
            cat_df = portfolio_df[portfolio_df['Category'] == category]
            if len(cat_df) == 0:
                continue
            
            print(f"\n--- {category.upper()} ---")
            print(f"{'-'*80}")
            
            for _, row in cat_df.iterrows():
                rank_str = f"(Rank #{row['Rank']})" if pd.notna(row['Rank']) else ""
                score_str = f"Score: {row['Score']:.1f}" if pd.notna(row['Score']) else ""
                amount_str = f"₹{row['Monthly Amount (₹)']:,.0f}" if pd.notna(row['Monthly Amount (₹)']) else "N/A"
                
                print(f"{row['Asset Class']:<15} {row['Allocation (%)']:>6.2f}%  "
                      f"{amount_str:>12}  {rank_str:<12} {score_str}")
        
        print(f"\n{'-'*80}")
        total_alloc = portfolio_df['Allocation (%)'].sum()
        total_amount = portfolio_df['Monthly Amount (₹)'].sum() if pd.notna(portfolio_df['Monthly Amount (₹)']).any() else None
        
        print(f"{'TOTAL':<15} {total_alloc:>6.2f}%  ", end="")
        if total_amount:
            print(f"₹{total_amount:>11,.0f}")
        else:
            print()
        print(f"{'='*80}\n")
    
    def get_portfolio_summary(self, portfolio_df: pd.DataFrame) -> Dict:
        """Get summary statistics for the portfolio"""
        summary = {
            'total_allocation': portfolio_df['Allocation (%)'].sum(),
            'num_assets': len(portfolio_df),
            'equity_allocation': portfolio_df[portfolio_df['Category'] == 'Equity']['Allocation (%)'].sum(),
            'debt_allocation': portfolio_df[portfolio_df['Category'] == 'Debt']['Allocation (%)'].sum(),
            'alternatives_allocation': portfolio_df[portfolio_df['Category'] == 'Alternatives']['Allocation (%)'].sum(),
            'top_holding': portfolio_df.iloc[0]['Asset Class'],
            'top_holding_allocation': portfolio_df.iloc[0]['Allocation (%)']
        }
        
        return summary


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_usage():
    """Example of how to use the system"""
    
    # Initialize the system
    allocator = PortfolioAllocationSystem(scorer_path=r'C:\Users\Rushi\Desktop\Portfolio Allocation System\backend\app\services\hybrid_scorer.pkl')
    
    # Example 1: Conservative investor, 5 years
    print("\n" + "="*80)
    print("EXAMPLE 1: Conservative Investor")
    print("="*80)
    
    portfolio1 = allocator.construct_portfolio(
        horizon_years=5,
        risk_profile="Conservative",
        target_corpus=2500000,
        monthly_sip=25000
    )
    
    allocator.display_portfolio(portfolio1)
    
    # Example 2: Aggressive investor, 15 years
    print("\n" + "="*80)
    print("EXAMPLE 2: Aggressive Investor")
    print("="*80)
    
    portfolio2 = allocator.construct_portfolio(
        horizon_years=15,
        risk_profile="Aggressive",
        target_corpus=5000000,
        monthly_sip=22000
    )
    
    allocator.display_portfolio(portfolio2)
    
    # Save portfolios
    portfolio1.to_csv('portfolio_conservative.csv', index=False)
    portfolio2.to_csv('portfolio_aggressive.csv', index=False)
    
    print("\n✓ Portfolios saved to CSV files")


if __name__ == "__main__":
    example_usage()