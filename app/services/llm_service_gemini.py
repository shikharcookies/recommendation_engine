"""Gemini LLM Service using Google's Gemini API (free tier available)."""
import json
import asyncio
from typing import Dict, List, Any
import httpx
import time


class GeminiLLMService:
    """Generate narrative content using Google Gemini API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Using gemini-flash-latest (free tier model)
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
        self.max_retries = 5  # Increased retries for rate limiting
        self.last_request_time = 0
        self.min_request_interval = 3.0  # Increased to 3 seconds between requests
    
    async def generate_narrative(
        self,
        counterparty_name: str,
        structured_analysis: Dict[str, str],
        signals: List[Dict[str, Any]],
        scores: Dict[str, int]
    ) -> Dict[str, str]:
        """
        Generate narrative content (strengths, weaknesses, recommendation).
        Also summarizes lengthy structured analysis sections.
        Returns a dictionary with 'strengths', 'weaknesses', 'recommendation', and summarized sections.
        """
        prompt = self._build_prompt(counterparty_name, structured_analysis, signals, scores)
        
        for attempt in range(self.max_retries):
            try:
                response = await self._call_api(prompt)
                narrative = self._parse_response(response)
                return narrative
            except httpx.HTTPStatusError as e:
                error_detail = f"HTTP {e.response.status_code}"
                try:
                    error_body = e.response.json()
                    error_detail += f": {error_body}"
                except:
                    error_detail += f": {e.response.text[:200]}"
                
                if e.response.status_code == 429:
                    # Rate limit hit - use longer backoff
                    wait_time = min(60, (2 ** attempt) * 5)  # 5s, 10s, 20s, 40s, 60s
                    print(f"Rate limit hit (429), waiting {wait_time}s before retry {attempt + 1}/{self.max_retries}")
                    await asyncio.sleep(wait_time)
                elif attempt == self.max_retries - 1:
                    raise ValueError(f"Failed to generate narrative after {self.max_retries} attempts: {error_detail}")
                else:
                    print(f"HTTP error on attempt {attempt + 1}: {error_detail}")
                    await asyncio.sleep(2 ** attempt)  # Standard exponential backoff
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                if attempt == self.max_retries - 1:
                    raise ValueError(f"Failed to generate narrative after {self.max_retries} attempts: {error_msg}")
                print(f"Error on attempt {attempt + 1}: {error_msg}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise ValueError("Failed to generate narrative")
    
    def _build_prompt(
        self,
        counterparty_name: str,
        structured_analysis: Dict[str, str],
        signals: List[Dict[str, Any]],
        scores: Dict[str, int]
    ) -> str:
        """Build the prompt for Gemini with summarization instructions."""
        signals_text = json.dumps(signals, indent=2)
        
        # Build concise analysis summary
        analysis_parts = []
        for section, content in structured_analysis.items():
            if content and content.strip():
                analysis_parts.append(f"{section.replace('_', ' ').title()}: {content[:200]}...")
        analysis_summary = "\n".join(analysis_parts) if analysis_parts else "No detailed analysis provided"
        
        prompt = f"""You are a credit analyst assistant. Generate a concise recommendation memo for {counterparty_name}.

Analysis Summary:
{analysis_summary}

Extracted Financial Signals:
{signals_text}

Risk Scores (1=best, 5=worst):
- Asset Quality: {scores.get('asset_quality', 3)}
- Liquidity: {scores.get('liquidity', 3)}
- Capitalisation: {scores.get('capitalisation', 3)}
- Profitability: {scores.get('profitability', 3)}

Generate a CONCISE response with:
1. Key Strengths (2-3 bullet points, each max 15 words)
2. Key Weaknesses (2-3 bullet points, each max 15 words)
3. Recommendation (1 paragraph, 3-4 sentences max)
4. Summarized sections (each max 2 sentences):
   - company_profile_summary
   - assets_summary
   - liquidity_summary
   - strategy_summary
   - means_summary
   - performance_summary

Be specific, concise, and reference the financial signals and scores.

Format your response as JSON with keys: "strengths", "weaknesses", "recommendation", "company_profile_summary", "assets_summary", "liquidity_summary", "strategy_summary", "means_summary", "performance_summary"."""
        
        return prompt
    
    async def _call_api(self, prompt: str) -> Dict[str, Any]:
        """Call the Gemini API using the correct format with rate limiting."""
        # Rate limiting: ensure minimum interval between requests
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last_request)
        
        headers = {
            'Content-Type': 'application/json',
            'x-goog-api-key': self.api_key
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.api_url, json=payload, headers=headers)
            self.last_request_time = time.time()
            response.raise_for_status()
            return response.json()
    
    async def generate_bullet_points(self, section_name: str, text: str) -> List[str]:
        """
        Generate intelligent bullet points for a section using LLM.
        Returns 3-6 bullet points depending on content complexity.
        
        NOTE: This method is kept for backward compatibility but consider using
        generate_bullet_points_batch() to reduce API calls.
        """
        if not text or not text.strip():
            return []
        
        prompt = f"""You are a financial analyst. Convert the following {section_name.replace('_', ' ')} text into clear, concise bullet points.

TEXT:
{text}

INSTRUCTIONS:
- Generate 3-6 bullet points (choose the appropriate number based on content)
- Each bullet should be a complete, meaningful statement
- Do NOT truncate or cut off sentences
- Do NOT add numbering or bullet symbols (just the text)
- Keep each point under 150 characters if possible, but prioritize completeness over length
- Focus on key information and insights
- Remove redundant information

Return ONLY a JSON array of strings, like: ["point 1", "point 2", "point 3"]"""

        for attempt in range(self.max_retries):
            try:
                response = await self._call_api(prompt)
                content = response["candidates"][0]["content"]["parts"][0]["text"]
                
                # Remove markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                # Parse JSON array
                bullets = json.loads(content)
                
                # Validate it's a list of strings
                if isinstance(bullets, list) and all(isinstance(b, str) for b in bullets):
                    return [b.strip() for b in bullets if b.strip()]
                else:
                    # Fallback to simple splitting
                    return self._fallback_bullets(text)
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limit hit - use longer backoff
                    wait_time = min(60, (2 ** attempt) * 5)
                    print(f"Rate limit hit (429) for bullet points, waiting {wait_time}s before retry {attempt + 1}/{self.max_retries}")
                    await asyncio.sleep(wait_time)
                elif attempt == self.max_retries - 1:
                    print(f"Warning: LLM bullet generation failed for {section_name} after retries: {e}")
                    return self._fallback_bullets(text)
                else:
                    await asyncio.sleep(2 ** attempt)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    print(f"Warning: LLM bullet generation failed for {section_name}: {e}")
                    return self._fallback_bullets(text)
                await asyncio.sleep(2 ** attempt)
        
        # Final fallback
        return self._fallback_bullets(text)
    
    async def generate_bullet_points_batch(self, prompt: str) -> Dict[str, List[str]]:
        """
        Generate bullet points for multiple sections in a single API call.
        This is more efficient and avoids rate limiting.
        
        Args:
            prompt: A pre-formatted prompt containing all sections
            
        Returns:
            Dictionary mapping section names to lists of bullet points
        """
        for attempt in range(self.max_retries):
            try:
                response = await self._call_api(prompt)
                content = response["candidates"][0]["content"]["parts"][0]["text"]
                
                # Remove markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                # Parse JSON object
                result = json.loads(content)
                
                # Validate structure
                if isinstance(result, dict):
                    # Ensure all values are lists of strings
                    validated = {}
                    for section, bullets in result.items():
                        if isinstance(bullets, list) and all(isinstance(b, str) for b in bullets):
                            validated[section] = [b.strip() for b in bullets if b.strip()]
                    return validated
                else:
                    return {}
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limit hit - use longer backoff
                    wait_time = min(60, (2 ** attempt) * 5)
                    print(f"Rate limit hit (429) for batch bullet points, waiting {wait_time}s before retry {attempt + 1}/{self.max_retries}")
                    await asyncio.sleep(wait_time)
                elif attempt == self.max_retries - 1:
                    print(f"Warning: Batch bullet generation failed after retries: {e}")
                    return {}
                else:
                    await asyncio.sleep(2 ** attempt)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    print(f"Warning: Batch bullet generation failed: {e}")
                    return {}
                await asyncio.sleep(2 ** attempt)
        
        return {}

    
    def _fallback_bullets(self, text: str) -> List[str]:
        """Fallback method if LLM fails - simple sentence splitting."""
        import re
        sentences = re.split(r'[.!?]\s+', text)
        bullets = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
        return bullets[:5]  # Max 5 bullets in fallback
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, str]:
        """Parse the Gemini API response to extract narrative content."""
        try:
            # Extract text from Gemini response
            content = response["candidates"][0]["content"]["parts"][0]["text"]
            
            # Try to parse as JSON first
            try:
                # Remove markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                narrative = json.loads(content)
                if all(key in narrative for key in ["strengths", "weaknesses", "recommendation"]):
                    return narrative
            except json.JSONDecodeError:
                pass
            
            # Fallback: parse as plain text
            return self._parse_plain_text(content)
        except (KeyError, IndexError) as e:
            raise ValueError(f"Failed to parse Gemini API response: {str(e)}")
    
    def _parse_plain_text(self, content: str) -> Dict[str, str]:
        """Parse plain text response into structured narrative."""
        lines = content.split('\n')
        strengths = []
        weaknesses = []
        recommendation = []
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            if 'strength' in line_lower:
                current_section = 'strengths'
            elif 'weakness' in line_lower:
                current_section = 'weaknesses'
            elif 'recommendation' in line_lower:
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
