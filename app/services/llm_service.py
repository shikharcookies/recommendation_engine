import json
import asyncio
from typing import Dict, List, Any
import httpx
from app.config import settings


class LLMService:
    """Generate narrative content using OpenRouter API."""
    
    def __init__(self):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "anthropic/claude-3.5-sonnet"
        self.temperature = 0.3
        self.max_tokens = 2000
        self.max_retries = 3
    
    async def generate_narrative(
        self,
        counterparty_name: str,
        structured_analysis: Dict[str, str],
        signals: List[Dict[str, Any]],
        scores: Dict[str, int]
    ) -> Dict[str, str]:
        """
        Generate narrative content (strengths, weaknesses, recommendation).
        Returns a dictionary with 'strengths', 'weaknesses', and 'recommendation' keys.
        """
        prompt = self._build_prompt(counterparty_name, structured_analysis, signals, scores)
        
        for attempt in range(self.max_retries):
            try:
                response = await self._call_api(prompt)
                narrative = self._parse_response(response)
                return narrative
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise ValueError(f"Failed to generate narrative after {self.max_retries} attempts: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise ValueError("Failed to generate narrative")
    
    def _build_prompt(
        self,
        counterparty_name: str,
        structured_analysis: Dict[str, str],
        signals: List[Dict[str, Any]],
        scores: Dict[str, int]
    ) -> str:
        """Build the prompt for the LLM."""
        signals_text = json.dumps(signals, indent=2)
        analysis_text = json.dumps(structured_analysis, indent=2)
        
        prompt = f"""You are a credit analyst assistant. Generate a recommendation memo for {counterparty_name}.

Structured Analysis:
{analysis_text}

Financial Signals:
{signals_text}

Risk Scores (1=best, 5=worst):
- Asset Quality: {scores.get('asset_quality', 3)}
- Liquidity: {scores.get('liquidity', 3)}
- Capitalisation: {scores.get('capitalisation', 3)}
- Profitability: {scores.get('profitability', 3)}

Generate:
1. Key Strengths (2-3 bullet points)
2. Key Weaknesses (2-3 bullet points)
3. Recommendation (1 paragraph, 3-5 sentences)

Be specific and reference the data provided.

Format your response as JSON with keys: "strengths", "weaknesses", "recommendation"."""
        
        return prompt
    
    async def _call_api(self, prompt: str) -> Dict[str, Any]:
        """Call the OpenRouter API."""
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, str]:
        """Parse the API response to extract narrative content."""
        try:
            content = response["choices"][0]["message"]["content"]
            
            # Try to parse as JSON first
            try:
                narrative = json.loads(content)
                if all(key in narrative for key in ["strengths", "weaknesses", "recommendation"]):
                    return narrative
            except json.JSONDecodeError:
                pass
            
            # Fallback: parse as plain text
            return self._parse_plain_text(content)
        except (KeyError, IndexError) as e:
            raise ValueError(f"Failed to parse API response: {str(e)}")
    
    def _parse_plain_text(self, content: str) -> Dict[str, str]:
        """Parse plain text response into structured narrative."""
        # Simple fallback parsing
        lines = content.split('\n')
        strengths = []
        weaknesses = []
        recommendation = []
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if 'strength' in line.lower():
                current_section = 'strengths'
            elif 'weakness' in line.lower():
                current_section = 'weaknesses'
            elif 'recommendation' in line.lower():
                current_section = 'recommendation'
            elif current_section == 'strengths':
                strengths.append(line)
            elif current_section == 'weaknesses':
                weaknesses.append(line)
            elif current_section == 'recommendation':
                recommendation.append(line)
        
        return {
            "strengths": '\n'.join(strengths) if strengths else "Analysis pending",
            "weaknesses": '\n'.join(weaknesses) if weaknesses else "Analysis pending",
            "recommendation": ' '.join(recommendation) if recommendation else "Further analysis required"
        }
