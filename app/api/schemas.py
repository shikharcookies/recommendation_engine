from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator, model_validator


class CounterpartyInput(BaseModel):
    name: str = Field(..., min_length=1)
    country: Optional[str] = None
    sector: Optional[str] = None
    intrinsic_hrc: Optional[float] = None
    intrinsic_pd: Optional[float] = None
    counterparty_hrc: Optional[float] = None
    counterparty_pd: Optional[float] = None
    
    @field_validator('name')
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError('Counterparty name cannot be empty')
        return v
    
    @field_validator('intrinsic_hrc', 'intrinsic_pd', 'counterparty_hrc', 'counterparty_pd')
    @classmethod
    def validate_numeric(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not isinstance(v, (int, float)):
            raise ValueError('Must be a valid number')
        return v


class AnalysisInput(BaseModel):
    analysis_text: Optional[str] = None
    pdf_file: Optional[Union[bytes, str]] = None  # Accept both bytes and base64 string
    docx_file: Optional[Union[bytes, str]] = None  # Accept both bytes and base64 string
    
    @model_validator(mode='after')
    def validate_input_source(self):
        sources = [self.analysis_text, self.pdf_file, self.docx_file]
        if sum(x is not None for x in sources) != 1:
            raise ValueError('Exactly one input source required')
        return self


class StructuredAnalysisSchema(BaseModel):
    company_profile: str
    assets: str
    liquidity: str
    strategy: str
    means: str
    performance: str



class RiskSignalSchema(BaseModel):
    signal_type: str
    value: float
    unit: str
    context: str


class ScoresSchema(BaseModel):
    asset_quality: int = Field(..., ge=1, le=5)
    liquidity: int = Field(..., ge=1, le=5)
    capitalisation: int = Field(..., ge=1, le=5)
    profitability: int = Field(..., ge=1, le=5)


class AnalysisResponse(BaseModel):
    analysis_id: str
    structured_analysis: StructuredAnalysisSchema
    structured_analysis_bullets: Optional[dict] = None
    signals: List[RiskSignalSchema]
    scores: ScoresSchema
    memo: str


class RecommendationResponse(BaseModel):
    analysis_id: str
    memo: str


class ExportRequest(BaseModel):
    analysis_id: str
