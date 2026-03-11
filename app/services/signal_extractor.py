import re
from typing import List, Dict, Any
import spacy


class SignalExtractor:
    """Extract financial signals from analysis text."""
    
    SIGNAL_PATTERNS = {
        "CET1": r"(?i)CET[\s\-]?1.*?(\d+\.?\d*)\s*%",
        "NPL": r"(?i)NPL.*?(\d+\.?\d*)\s*%",
        "LCR": r"(?i)LCR.*?(\d+\.?\d*)\s*%",
        "ROAE": r"(?i)ROAE.*?(\d+\.?\d*)\s*%",
        "cost_to_income": r"(?i)cost[\s\-]to[\s\-]income.*?(\d+\.?\d*)\s*%",
        "loan_to_deposit": r"(?i)loan[\s\-]to[\s\-]deposit.*?(\d+\.?\d*)\s*%",
    }
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If model not found, create a blank model
            self.nlp = None
    
    def extract_signals(self, analysis_text: str) -> List[Dict[str, Any]]:
        """
        Extract financial signals from analysis text.
        Returns a list of signal dictionaries with type, value, unit, and context.
        """
        signals = []
        
        if not analysis_text:
            return signals
        
        # Use spacy for sentence segmentation if available
        if self.nlp:
            doc = self.nlp(analysis_text)
            sentences = [sent.text for sent in doc.sents]
        else:
            # Fallback to simple sentence splitting
            sentences = re.split(r'[.!?]+', analysis_text)
        
        # Search for each signal type
        for signal_type, pattern in self.SIGNAL_PATTERNS.items():
            for sentence in sentences:
                matches = re.finditer(pattern, sentence)
                for match in matches:
                    try:
                        value = float(match.group(1))
                        signals.append({
                            "signal_type": signal_type,
                            "value": value,
                            "unit": "%",
                            "context": sentence.strip()
                        })
                    except (ValueError, IndexError):
                        continue
        
        return signals
