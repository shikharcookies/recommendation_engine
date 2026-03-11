import re
from typing import Dict


class AnalysisParser:
    """Parse unstructured analysis text into structured sections."""
    
    SECTION_PATTERNS = {
        "company_profile": r"(?i)(?:^|\n)#{0,3}\s*(?:company\s+profile|profile)\s*[:\n]",
        "assets": r"(?i)(?:^|\n)#{0,3}\s*assets\s*[:\n]",
        "liquidity": r"(?i)(?:^|\n)#{0,3}\s*liquidity\s*[:\n]",
        "strategy": r"(?i)(?:^|\n)#{0,3}\s*strategy\s*[:\n]",
        "means": r"(?i)(?:^|\n)#{0,3}\s*means\s*[:\n]",
        "performance": r"(?i)(?:^|\n)#{0,3}\s*performance\s*[:\n]",
    }
    
    def parse(self, analysis_text: str) -> Dict[str, str]:
        """
        Extract structured sections from analysis text.
        Returns a dictionary with all section keys, using empty strings for missing sections.
        """
        result = {
            "company_profile": "",
            "assets": "",
            "liquidity": "",
            "strategy": "",
            "means": "",
            "performance": ""
        }
        
        if not analysis_text:
            return result
        
        # Find all section headers and their positions
        section_positions = []
        for section_name, pattern in self.SECTION_PATTERNS.items():
            matches = list(re.finditer(pattern, analysis_text))
            for match in matches:
                section_positions.append((match.start(), section_name))
        
        # Sort by position
        section_positions.sort(key=lambda x: x[0])
        
        # Extract content between sections
        for i, (start_pos, section_name) in enumerate(section_positions):
            # Find the end position (start of next section or end of text)
            if i + 1 < len(section_positions):
                end_pos = section_positions[i + 1][0]
            else:
                end_pos = len(analysis_text)
            
            # Extract and clean the section content
            content = analysis_text[start_pos:end_pos]
            
            # Remove the header line
            lines = content.split('\n')
            if lines:
                lines = lines[1:]  # Skip header line
            content = '\n'.join(lines).strip()
            
            result[section_name] = content
        
        return result
