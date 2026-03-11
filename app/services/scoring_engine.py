from typing import Dict, List, Any, Optional


class ScoringEngine:
    """Compute deterministic rule-based risk scores."""
    
    def compute_scores(
        self,
        structured_analysis: Dict[str, str],
        signals: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Compute risk scores based on structured analysis and signals.
        All scores are integers between 1 (best) and 5 (worst).
        """
        # Extract signal values
        signal_values = self._extract_signal_values(signals)
        
        # Compute individual scores
        asset_quality = self._score_asset_quality(signal_values.get("NPL"))
        liquidity = self._score_liquidity(signal_values.get("LCR"))
        capitalisation = self._score_capitalisation(signal_values.get("CET1"))
        profitability = self._score_profitability(
            signal_values.get("ROAE"),
            signal_values.get("cost_to_income")
        )
        
        return {
            "asset_quality": asset_quality,
            "liquidity": liquidity,
            "capitalisation": capitalisation,
            "profitability": profitability
        }
    
    def _extract_signal_values(self, signals: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract signal values into a dictionary keyed by signal type."""
        result = {}
        for signal in signals:
            signal_type = signal.get("signal_type")
            value = signal.get("value")
            if signal_type and value is not None:
                result[signal_type] = value
        return result
    
    def _score_asset_quality(self, npl: Optional[float]) -> int:
        """Score asset quality based on NPL ratio. 5=Excellent, 1=Poor"""
        if npl is None:
            return 3  # Neutral score
        
        if npl < 2.0:
            return 5  # Excellent
        elif npl < 4.0:
            return 4  # Good
        elif npl < 6.0:
            return 3  # Moderate
        elif npl < 10.0:
            return 2  # Weak
        else:
            return 1  # Poor
    
    def _score_liquidity(self, lcr: Optional[float]) -> int:
        """Score liquidity based on LCR. 5=Excellent, 1=Poor"""
        if lcr is None:
            return 3  # Neutral score
        
        if lcr > 150.0:
            return 5  # Excellent
        elif lcr > 120.0:
            return 4  # Good
        elif lcr > 100.0:
            return 3  # Moderate
        elif lcr > 80.0:
            return 2  # Weak
        else:
            return 1  # Poor
    
    def _score_capitalisation(self, cet1: Optional[float]) -> int:
        """Score capitalisation based on CET1 ratio. 5=Excellent, 1=Poor"""
        if cet1 is None:
            return 3  # Neutral score
        
        if cet1 > 15.0:
            return 5  # Excellent
        elif cet1 > 12.0:
            return 4  # Good
        elif cet1 > 10.0:
            return 3  # Moderate
        elif cet1 > 8.0:
            return 2  # Weak
        else:
            return 1  # Poor
    
    def _score_profitability(
        self,
        roae: Optional[float],
        cost_to_income: Optional[float]
    ) -> int:
        """Score profitability based on ROAE and cost-to-income ratio. 5=Excellent, 1=Poor"""
        if roae is None and cost_to_income is None:
            return 3  # Neutral score
        
        # Best case: high ROAE and low cost-to-income
        if roae is not None and roae > 12.0 and (cost_to_income is None or cost_to_income < 50.0):
            return 5  # Excellent
        
        # Good case
        if roae is not None and roae > 10.0 and (cost_to_income is None or cost_to_income < 60.0):
            return 4  # Good
        
        # Moderate case
        if (roae is not None and roae > 8.0) or (cost_to_income is not None and cost_to_income < 70.0):
            return 3  # Moderate
        
        # Poor case
        if (roae is not None and roae > 5.0) or (cost_to_income is not None and cost_to_income < 80.0):
            return 2  # Weak
        
        # Worst case
        return 1  # Poor
