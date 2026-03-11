"""Mock LLM Service for testing without OpenRouter credits."""
from typing import Dict, List, Any


class MockLLMService:
    """Generate mock narrative content without calling external APIs."""
    
    async def generate_narrative(
        self,
        counterparty_name: str,
        structured_analysis: Dict[str, str],
        signals: List[Dict[str, Any]],
        scores: Dict[str, int]
    ) -> Dict[str, str]:
        """
        Generate mock narrative content based on scores.
        Returns a dictionary with 'strengths', 'weaknesses', 'recommendation', and summarized sections.
        """
        
        # Generate strengths based on good scores (1-2)
        strengths = self._generate_strengths(counterparty_name, scores, signals)
        
        # Generate weaknesses based on poor scores (4-5)
        weaknesses = self._generate_weaknesses(counterparty_name, scores, signals)
        
        # Generate recommendation based on overall assessment
        recommendation = self._generate_recommendation(counterparty_name, scores)
        
        # Generate summarized sections (max 2 sentences each)
        summaries = self._generate_summaries(structured_analysis)
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendation": recommendation,
            **summaries  # Merge summarized sections
        }
    
    def _generate_strengths(
        self,
        counterparty_name: str,
        scores: Dict[str, int],
        signals: List[Dict[str, Any]]
    ) -> str:
        """Generate strengths based on good scores."""
        strengths = []
        
        if scores.get('asset_quality', 3) <= 2:
            strengths.append("• Strong asset quality with low non-performing loan ratios")
        
        if scores.get('liquidity', 3) <= 2:
            strengths.append("• Robust liquidity position with healthy coverage ratios")
        
        if scores.get('capitalisation', 3) <= 2:
            strengths.append("• Well-capitalized with strong regulatory capital buffers")
        
        if scores.get('profitability', 3) <= 2:
            strengths.append("• Solid profitability metrics and efficient cost management")
        
        if not strengths:
            strengths.append("• Stable financial position with adequate risk management")
        
        return "\n".join(strengths)
    
    def _generate_weaknesses(
        self,
        counterparty_name: str,
        scores: Dict[str, int],
        signals: List[Dict[str, Any]]
    ) -> str:
        """Generate weaknesses based on poor scores."""
        weaknesses = []
        
        if scores.get('asset_quality', 3) >= 4:
            weaknesses.append("• Elevated non-performing loan levels requiring attention")
        
        if scores.get('liquidity', 3) >= 4:
            weaknesses.append("• Liquidity position below optimal levels")
        
        if scores.get('capitalisation', 3) >= 4:
            weaknesses.append("• Capital ratios approaching regulatory minimums")
        
        if scores.get('profitability', 3) >= 4:
            weaknesses.append("• Profitability under pressure with elevated cost ratios")
        
        if not weaknesses:
            weaknesses.append("• Some areas for improvement in operational efficiency")
        
        return "\n".join(weaknesses)
    
    def _generate_recommendation(
        self,
        counterparty_name: str,
        scores: Dict[str, int]
    ) -> str:
        """Generate recommendation based on overall scores."""
        avg_score = sum(scores.values()) / len(scores)
        
        if avg_score <= 2.0:
            return (
                f"{counterparty_name} demonstrates strong credit fundamentals across all key metrics. "
                f"The institution maintains robust capital buffers, healthy liquidity, and solid asset quality. "
                f"We recommend maintaining the current credit relationship with standard monitoring procedures."
            )
        elif avg_score <= 3.0:
            return (
                f"{counterparty_name} presents a satisfactory credit profile with adequate risk management. "
                f"While some metrics show room for improvement, the overall financial position remains stable. "
                f"We recommend continuing the credit relationship with regular monitoring of key indicators."
            )
        elif avg_score <= 4.0:
            return (
                f"{counterparty_name} shows some areas of concern that warrant closer attention. "
                f"Several key metrics are below optimal levels, suggesting increased credit risk. "
                f"We recommend enhanced monitoring and consideration of risk mitigation measures."
            )
        else:
            return (
                f"{counterparty_name} exhibits elevated credit risk across multiple dimensions. "
                f"Significant weaknesses in key financial metrics require immediate attention. "
                f"We recommend a comprehensive review of the credit relationship and implementation of risk mitigation strategies."
            )
    
    def _generate_summaries(self, structured_analysis: Dict[str, str]) -> Dict[str, str]:
        """Generate concise summaries (max 2 sentences) for each structured analysis section."""
        summaries = {}
        
        # Company Profile Summary
        if structured_analysis.get('company_profile'):
            text = structured_analysis['company_profile'][:300]
            summaries['company_profile_summary'] = (
                f"The institution operates in the financial services sector. "
                f"It maintains a diversified business model with established market presence."
            )
        else:
            summaries['company_profile_summary'] = "Company profile information not available."
        
        # Assets Summary
        if structured_analysis.get('assets'):
            summaries['assets_summary'] = (
                f"Asset portfolio demonstrates adequate diversification. "
                f"Non-performing loan levels are within acceptable ranges."
            )
        else:
            summaries['assets_summary'] = "Asset information not available."
        
        # Liquidity Summary
        if structured_analysis.get('liquidity'):
            summaries['liquidity_summary'] = (
                f"Liquidity position meets regulatory requirements. "
                f"Coverage ratios indicate sufficient short-term funding capacity."
            )
        else:
            summaries['liquidity_summary'] = "Liquidity information not available."
        
        # Strategy Summary
        if structured_analysis.get('strategy'):
            summaries['strategy_summary'] = (
                f"Strategic direction focuses on core business strengths. "
                f"Management demonstrates clear priorities for growth and risk management."
            )
        else:
            summaries['strategy_summary'] = "Strategy information not available."
        
        # Means Summary
        if structured_analysis.get('means'):
            summaries['means_summary'] = (
                f"Capital resources support current operations. "
                f"Funding structure appears stable with diversified sources."
            )
        else:
            summaries['means_summary'] = "Means information not available."
        
        # Performance Summary
        if structured_analysis.get('performance'):
            summaries['performance_summary'] = (
                f"Financial performance shows consistent results. "
                f"Key profitability metrics align with sector benchmarks."
            )
        else:
            summaries['performance_summary'] = "Performance information not available."
        
        return summaries
    
    async def generate_bullet_points(self, section_name: str, text: str) -> List[str]:
        """
        Generate bullet points using simple rule-based approach (mock).
        Returns 3-6 bullet points depending on content.
        """
        import re
        
        if not text or not text.strip():
            return []
        
        text = text.strip()
        
        # Handle numbered lists specially
        # Look for patterns like "1. text 2. text" or "1) text 2) text"
        numbered_pattern = r'(?:^|\s)(\d+[\.\)])\s+([^0-9]+?)(?=\s*\d+[\.\)]|\s*$)'
        numbered_matches = list(re.finditer(numbered_pattern, text, re.MULTILINE))
        
        if len(numbered_matches) >= 2:
            # Extract numbered items
            bullets = []
            for match in numbered_matches:
                item_text = match.group(2).strip()
                # Clean up
                item_text = re.sub(r'\s+', ' ', item_text)
                if len(item_text) > 15:
                    bullets.append(item_text)
            
            # Also capture any text before the first number
            first_match_start = numbered_matches[0].start()
            if first_match_start > 0:
                intro_text = text[:first_match_start].strip()
                intro_text = re.sub(r'^[A-Z][a-z\s]+:\s*', '', intro_text)
                if len(intro_text) > 15:
                    bullets.insert(0, intro_text)
            
            return bullets[:6] if bullets else self._simple_split(text)
        
        # No numbered list, use simple splitting
        return self._simple_split(text)
    
    def _simple_split(self, text: str) -> List[str]:
        """Simple sentence-based splitting."""
        import re
        
        # Split by sentences
        sentences = re.split(r'[.!?]\s+', text.strip())
        
        # Clean and filter sentences
        bullets = []
        for sentence in sentences:
            sentence = sentence.strip()
            
            # Skip very short sentences
            if len(sentence) < 20:
                continue
            
            # Remove section markers and numbering
            sentence = re.sub(r'^[A-Z][a-z\s]+:\s*', '', sentence)
            sentence = re.sub(r'^\d+[\.\)]\s*', '', sentence)
            
            # Skip if it's just a label
            if sentence.endswith(':'):
                continue
            
            # Clean up whitespace
            sentence = re.sub(r'\s+', ' ', sentence)
            
            bullets.append(sentence)
        
        # Return 3-6 bullets based on content
        if len(bullets) <= 3:
            return bullets
        elif len(bullets) <= 6:
            return bullets[:6]
        else:
            # If more than 6, take every nth to get ~5 bullets
            step = max(1, len(bullets) // 5)
            return [bullets[i] for i in range(0, min(len(bullets), 30), step)][:5]
    
    async def generate_bullet_points_batch(self, prompt: str) -> Dict[str, List[str]]:
        """
        Mock batch bullet point generation.
        Extracts section names from prompt and generates mock bullets for each.
        """
        import re
        
        # Extract sections from the prompt
        section_pattern = r'SECTION:\s*([^\n]+)\s*TEXT:\s*([^\n]+(?:\n(?!SECTION:)[^\n]+)*)'
        matches = re.finditer(section_pattern, prompt, re.MULTILINE | re.DOTALL)
        
        result = {}
        for match in matches:
            section_name = match.group(1).strip().lower().replace(' ', '_')
            section_text = match.group(2).strip()
            
            # Generate bullets for this section
            bullets = await self.generate_bullet_points(section_name, section_text)
            if bullets:
                result[section_name] = bullets
        
        return result
