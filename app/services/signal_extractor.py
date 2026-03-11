import re
from typing import List, Dict, Any


class SignalExtractor:
    """Extract financial signals from analysis text using precise regex patterns."""
    
    # Flexible patterns that match various text formats
    SIGNAL_PATTERNS = {
        "CET1": r"(?i)CET[\s\-]?1(?:\s+ratio)?[^\d]{0,20}?(\d+\.?\d*)\s*%",
        "NPL": r"(?i)(\d+\.?\d*)\s*%\s+NPL|NPL[^\d]{0,20}?(\d+\.?\d*)\s*%",
        "LCR": r"(?i)(?:LCR|liquidity\s+coverage\s+ratio)[^\d]{0,30}?(\d+\.?\d*)\s*%",
        "ROAE": r"(?i)ROAE[^\d]{0,20}?(\d+\.?\d*)\s*%",
        "cost_to_income": r"(?i)(?:C/I|cost[\s\-]to[\s\-]income)[^\d]{0,20}?(\d+\.?\d*)\s*%",
        "loan_to_deposit": r"(?i)loan[\s\-]to[\s\-]deposit(?:\s+ratio)?[^\d]{0,30}?(\d+\.?\d*)\s*%",
        "liquid_assets_ratio": r"(?i)liquid\s+assets?\s*/\s*total\s+assets?[^\d]{0,30}?(\d+\.?\d*)\s*%",
    }
    
    def extract_signals(self, analysis_text: str) -> List[Dict[str, Any]]:
        """
        Extract financial signals from analysis text using regex pattern matching.
        Returns a list of unique signal dictionaries with type, value, unit, and context.
        Only keeps the LAST occurrence of each signal type (most recent value).
        """
        signals_dict = {}  # Use dict to keep only last occurrence of each signal type
        
        if not analysis_text:
            return []
        
        # Search for each signal type in the full text
        for signal_type, pattern in self.SIGNAL_PATTERNS.items():
            matches = list(re.finditer(pattern, analysis_text, re.IGNORECASE | re.DOTALL))
            
            # Only keep the LAST match for each signal type (most recent value)
            if matches:
                match = matches[-1]  # Get the last occurrence
                
                try:
                    # For NPL, check both capture groups (value before or after "NPL")
                    if signal_type == "NPL":
                        value = float(match.group(1) if match.group(1) else match.group(2))
                    else:
                        value = float(match.group(1))
                    
                    # Extract context (surrounding text, max 150 chars)
                    start = max(0, match.start() - 75)
                    end = min(len(analysis_text), match.end() + 75)
                    context = analysis_text[start:end].strip()
                    
                    # Store in dict (will overwrite if duplicate signal_type)
                    signals_dict[signal_type] = {
                        "signal_type": signal_type,
                        "value": value,
                        "unit": "%",
                        "context": context
                    }
                    
                except (ValueError, IndexError, TypeError):
                    continue
        
        # Convert dict values to list
        return list(signals_dict.values())