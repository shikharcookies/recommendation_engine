from typing import Dict, Any, Optional
from app.services.database_service import DatabaseService
from app.services.text_extraction_service import TextExtractionService
from app.services.analysis_parser import AnalysisParser
from app.services.signal_extractor import SignalExtractor
from app.services.scoring_engine import ScoringEngine
from app.services.llm_service import LLMService
from app.services.llm_service_gemini import GeminiLLMService
from app.services.llm_service_mock import MockLLMService
from app.services.memo_generator import MemoGenerator
from app.services.text_summarizer import TextSummarizer
from app.config import settings


class AnalysisService:
    """Orchestrate the full analysis pipeline."""
    
    def __init__(self, database_service: Optional[DatabaseService] = None, use_mock_llm: bool = False):
        self.db = database_service or DatabaseService()
        self.text_extractor = TextExtractionService()
        self.parser = AnalysisParser()
        self.signal_extractor = SignalExtractor()
        self.scoring_engine = ScoringEngine()
        self.summarizer = TextSummarizer()
        
        # Determine which LLM service to use
        api_key = getattr(settings, 'gemini_api_key', None) or getattr(settings, 'openrouter_api_key', 'your_api_key_here')
        
        if use_mock_llm or api_key == 'your_api_key_here' or not api_key:
            self.llm_service = MockLLMService()
            print("⚠️  Using Mock LLM Service (no API calls)")
        elif hasattr(settings, 'gemini_api_key') and settings.gemini_api_key and settings.gemini_api_key != 'your_api_key_here':
            self.llm_service = GeminiLLMService(settings.gemini_api_key)
            print("✓ Using Google Gemini LLM Service (Free Tier)")
        elif hasattr(settings, 'openrouter_api_key') and settings.openrouter_api_key and settings.openrouter_api_key != 'your_api_key_here':
            self.llm_service = LLMService()
            print("✓ Using OpenRouter LLM Service")
        else:
            self.llm_service = MockLLMService()
            print("⚠️  Using Mock LLM Service (no API calls)")
        
        self.memo_generator = MemoGenerator()
    
    async def create_analysis(
        self,
        counterparty_data: Dict[str, Any],
        analysis_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the full analysis pipeline.
        Returns a dictionary with analysis_id, structured_analysis, signals, scores, and memo.
        """
        try:
            # Stage 1: Extract text from input
            analysis_text = self._extract_text(analysis_input)
            
            # Stage 2: Create counterparty record
            counterparty = self.db.create_counterparty(
                name=counterparty_data["name"],
                country=counterparty_data.get("country"),
                sector=counterparty_data.get("sector"),
                intrinsic_hrc=counterparty_data.get("intrinsic_hrc"),
                intrinsic_pd=counterparty_data.get("intrinsic_pd"),
                counterparty_hrc=counterparty_data.get("counterparty_hrc"),
                counterparty_pd=counterparty_data.get("counterparty_pd")
            )
            
            # Stage 3: Parse structured sections
            structured_analysis = self.parser.parse(analysis_text)
            
            # Stage 4: Create analysis record
            analysis = self.db.create_analysis(
                counterparty_id=counterparty.id,
                analysis_text=analysis_text,
                structured_analysis=structured_analysis
            )
            
            # Stage 5: Extract financial signals (graceful degradation)
            try:
                signals = self.signal_extractor.extract_signals(analysis_text)
            except Exception:
                signals = []
            
            # Stage 6: Store signals
            if signals:
                self.db.create_signals(analysis.id, signals)
            
            # Stage 7: Compute scores
            scores = self.scoring_engine.compute_scores(structured_analysis, signals)
            
            # Stage 8: Store scores
            self.db.create_scores(
                analysis_id=analysis.id,
                asset_quality=scores["asset_quality"],
                liquidity=scores["liquidity"],
                capitalisation=scores["capitalisation"],
                profitability=scores["profitability"]
            )
            
            # Stage 9: Generate narrative using LLM (with fallback to mock on failure)
            try:
                narrative = await self.llm_service.generate_narrative(
                    counterparty_name=counterparty.name,
                    structured_analysis=structured_analysis,
                    signals=signals,
                    scores=scores
                )
            except Exception as e:
                print(f"⚠️  LLM narrative generation failed: {e}")
                print("⚠️  Falling back to mock narrative generation")
                # Fallback to mock service
                from app.services.llm_service_mock import MockLLMService
                mock_service = MockLLMService()
                narrative = await mock_service.generate_narrative(
                    counterparty_name=counterparty.name,
                    structured_analysis=structured_analysis,
                    signals=signals,
                    scores=scores
                )
            
            # Stage 10: Generate memo
            memo = self.memo_generator.generate_memo(
                counterparty=counterparty_data,
                structured_analysis=structured_analysis,
                signals=signals,
                scores=scores,
                narrative=narrative
            )
            
            # Stage 11: Store recommendation
            self.db.create_recommendation(
                analysis_id=analysis.id,
                memo=memo
            )
            
            # Stage 12: Create summarized bullet points for UI display using LLM
            # Batch all sections into a single API call to avoid rate limiting
            try:
                structured_analysis_bullets = await self._generate_all_bullet_points(structured_analysis)
            except Exception as e:
                print(f"⚠️  LLM bullet generation failed: {e}")
                print("⚠️  Falling back to mock bullet generation")
                # Fallback to mock service
                from app.services.llm_service_mock import MockLLMService
                mock_service = MockLLMService()
                structured_analysis_bullets = {}
                for section, content in structured_analysis.items():
                    if content and content.strip():
                        bullets = await mock_service.generate_bullet_points(section, content)
                        if bullets:
                            structured_analysis_bullets[f"{section}_bullets"] = bullets
            
            return {
                "analysis_id": analysis.id,
                "structured_analysis": structured_analysis,
                "structured_analysis_bullets": structured_analysis_bullets,
                "signals": signals,
                "scores": scores,
                "memo": memo
            }
        
        except Exception as e:
            raise e

    async def _generate_all_bullet_points(self, structured_analysis: Dict[str, str]) -> Dict[str, list]:
        """
        Generate bullet points for all sections in a single API call to avoid rate limiting.
        """
        # Filter out empty sections
        sections_to_process = {k: v for k, v in structured_analysis.items() if v and v.strip()}
        
        if not sections_to_process:
            return {}
        
        # Build a single prompt for all sections
        prompt = "You are a financial analyst. Convert the following sections into bullet points.\n\n"
        
        for section, content in sections_to_process.items():
            prompt += f"SECTION: {section.replace('_', ' ').title()}\n"
            prompt += f"TEXT: {content}\n\n"
        
        prompt += """INSTRUCTIONS:
- For each section, generate 3-6 bullet points (choose based on content complexity)
- Each bullet should be a complete, meaningful statement
- Do NOT truncate or cut off sentences
- Do NOT add numbering or bullet symbols (just the text)
- Keep each point under 150 characters if possible, but prioritize completeness over length
- Focus on key information and insights
- Remove redundant information

Return a JSON object where keys are section names (company_profile, assets, liquidity, strategy, means, performance) and values are arrays of bullet point strings.

Example format:
{
  "company_profile": ["point 1", "point 2", "point 3"],
  "assets": ["point 1", "point 2"],
  "liquidity": ["point 1", "point 2", "point 3", "point 4"]
}"""

        try:
            result = await self.llm_service.generate_bullet_points_batch(prompt)
            
            # Add "_bullets" suffix to keys
            return {f"{k}_bullets": v for k, v in result.items()}
        except Exception as e:
            print(f"Warning: Batch bullet generation failed: {e}")
            # Fallback: return empty dict
            return {}
    
    
    def _extract_text(self, analysis_input: Dict[str, Any]) -> str:
        """Extract text from various input formats."""
        if analysis_input.get("analysis_text"):
            return self.text_extractor.clean_text(analysis_input["analysis_text"])
        elif analysis_input.get("pdf_file"):
            return self.text_extractor.extract_from_pdf(analysis_input["pdf_file"])
        elif analysis_input.get("docx_file"):
            return self.text_extractor.extract_from_docx(analysis_input["docx_file"])
        else:
            raise ValueError("No valid input source provided")
    
    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a saved analysis."""
        analysis = self.db.get_analysis(analysis_id)
        if not analysis:
            return None
        
        return {
            "analysis_id": analysis.id,
            "structured_analysis": analysis.structured_analysis,
            "signals": [
                {
                    "signal_type": s.signal_type,
                    "value": s.value,
                    "unit": s.unit,
                    "context": s.context
                }
                for s in analysis.signals
            ],
            "scores": {
                "asset_quality": analysis.scores.asset_quality,
                "liquidity": analysis.scores.liquidity,
                "capitalisation": analysis.scores.capitalisation,
                "profitability": analysis.scores.profitability
            } if analysis.scores else None
        }
    
    def get_recommendation(self, analysis_id: str) -> Optional[str]:
        """Retrieve a saved recommendation memo."""
        recommendation = self.db.get_recommendation(analysis_id)
        if not recommendation:
            return None
        return recommendation.memo
