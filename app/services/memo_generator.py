from datetime import datetime
from typing import Dict, List, Any
from jinja2 import Template


class MemoGenerator:
    """Generate formatted recommendation memos using Jinja2 templates."""
    
    MEMO_TEMPLATE = """COUNTERPARTY RECOMMENDATION

Counterparty: {{ counterparty.name }}
Country: {{ counterparty.country or 'N/A' }}
Sector: {{ counterparty.sector or 'N/A' }}
Date: {{ current_date }}

RISK SCORES
Asset Quality: {{ scores.asset_quality }}/5
Liquidity: {{ scores.liquidity }}/5
Capitalisation: {{ scores.capitalisation }}/5
Profitability: {{ scores.profitability }}/5

OVERVIEW
{{ narrative.get('company_profile_summary', structured_analysis.company_profile[:300] if structured_analysis.company_profile else 'No company profile available.') }}

STRENGTHS
{{ narrative.strengths }}

WEAKNESSES
{{ narrative.weaknesses }}

RECOMMENDATION
{{ narrative.recommendation }}
"""
    
    def generate_memo(
        self,
        counterparty: Dict[str, Any],
        structured_analysis: Dict[str, str],
        signals: List[Dict[str, Any]],
        scores: Dict[str, int],
        narrative: Dict[str, str]
    ) -> str:
        """Generate a formatted recommendation memo."""
        template = Template(self.MEMO_TEMPLATE)
        
        memo = template.render(
            counterparty=counterparty,
            structured_analysis=structured_analysis,
            signals=signals,
            scores=scores,
            narrative=narrative,
            current_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        return memo
