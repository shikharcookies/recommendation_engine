from typing import Dict, List, Any, Optional


class ScoringEngine:
    """Compute deterministic rule-based risk scores."""

    def compute_scores(
        self,
        structured_analysis: Dict[str, str],
        signals: List[Dict[str, Any]]
    ) -> Dict[str, int]:

        signal_values = self._extract_signal_values(signals)

        asset_quality = self._score_asset_quality(
            signal_values.get("NPL")
        )

        liquidity = self._score_liquidity(
            signal_values.get("LCR"),
            signal_values.get("loan_to_deposit")
        )

        capitalisation = self._score_capitalisation(
            signal_values.get("CET1")
        )

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
        """
        Extract signal values into dictionary.

        Keeps the FIRST detected value to prevent
        overwriting with historical values.
        """

        result: Dict[str, float] = {}

        for signal in signals:

            signal_type = signal.get("signal_type")
            value = signal.get("value")

            if signal_type and value is not None:

                if signal_type not in result:
                    result[signal_type] = float(value)

        return result

    def _score_asset_quality(self, npl: Optional[float]) -> int:

        if npl is None:
            return 3

        if npl < 2:
            return 5
        elif npl < 4:
            return 4
        elif npl < 6:
            return 3
        elif npl < 10:
            return 2
        else:
            return 1

    def _score_liquidity(
        self,
        lcr: Optional[float],
        loan_to_deposit: Optional[float]
    ) -> int:

        if lcr is not None:

            if lcr > 150:
                return 5
            elif lcr > 120:
                return 4
            elif lcr > 100:
                return 3
            elif lcr > 80:
                return 2
            else:
                return 1

        if loan_to_deposit is not None:

            if loan_to_deposit < 60:
                return 5
            elif loan_to_deposit < 80:
                return 4
            elif loan_to_deposit < 100:
                return 3
            elif loan_to_deposit < 120:
                return 2
            else:
                return 1

        return 3

    def _score_capitalisation(self, cet1: Optional[float]) -> int:

        if cet1 is None:
            return 3

        if cet1 > 15:
            return 5
        elif cet1 > 12:
            return 4
        elif cet1 > 10:
            return 3
        elif cet1 > 8:
            return 2
        else:
            return 1

    def _score_profitability(
        self,
        roae: Optional[float],
        cost_to_income: Optional[float]
    ) -> int:

        if roae is None and cost_to_income is None:
            return 3

        if roae is not None and roae > 12 and (cost_to_income is None or cost_to_income < 50):
            return 5

        if roae is not None and roae > 10 and (cost_to_income is None or cost_to_income < 60):
            return 4

        if (roae is not None and roae > 8) or (cost_to_income is not None and cost_to_income < 70):
            return 3

        if (roae is not None and roae > 5) or (cost_to_income is not None and cost_to_income < 80):
            return 2

        return 1