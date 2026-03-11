from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from typing import Dict, Any
from app.api.schemas import (
    CounterpartyInput,
    AnalysisInput,
    AnalysisResponse,
    RecommendationResponse,
    ExportRequest,
    StructuredAnalysisSchema,
    RiskSignalSchema,
    ScoresSchema
)
from app.services.analysis_service import AnalysisService
from app.services.export_service import ExportService

router = APIRouter()
analysis_service = AnalysisService()
export_service = ExportService()


@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze(
    counterparty: CounterpartyInput,
    analysis_input: AnalysisInput
):
    """
    Analyze counterparty and generate recommendation.
    
    Accepts counterparty information and analysis text/file.
    Returns structured analysis, signals, scores, and recommendation memo.
    """
    try:
        import base64
        
        # Convert Pydantic models to dicts
        counterparty_data = counterparty.model_dump()
        analysis_data = analysis_input.model_dump()
        
        # Decode base64 file data if present
        if analysis_data.get('pdf_file'):
            if isinstance(analysis_data['pdf_file'], str):
                analysis_data['pdf_file'] = base64.b64decode(analysis_data['pdf_file'])
        
        if analysis_data.get('docx_file'):
            if isinstance(analysis_data['docx_file'], str):
                analysis_data['docx_file'] = base64.b64decode(analysis_data['docx_file'])
        
        # Execute analysis pipeline
        result = await analysis_service.create_analysis(
            counterparty_data=counterparty_data,
            analysis_input=analysis_data
        )
        
        # Convert to response schema
        return AnalysisResponse(
            analysis_id=result["analysis_id"],
            structured_analysis=StructuredAnalysisSchema(**result["structured_analysis"]),
            structured_analysis_bullets=result.get("structured_analysis_bullets"),  # Add bullets!
            signals=[RiskSignalSchema(**s) for s in result["signals"]],
            scores=ScoresSchema(**result["scores"]),
            memo=result["memo"]
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )



@router.get("/analysis/{id}", status_code=status.HTTP_200_OK)
async def get_analysis(id: str):
    """
    Retrieve a saved analysis by ID.
    
    Returns structured analysis, signals, and scores.
    """
    result = analysis_service.get_analysis(id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {id} not found"
        )
    
    return {
        "analysis_id": result["analysis_id"],
        "structured_analysis": result["structured_analysis"],
        "signals": result["signals"],
        "scores": result["scores"]
    }


@router.get("/recommendation/{id}", response_model=RecommendationResponse, status_code=status.HTTP_200_OK)
async def get_recommendation(id: str):
    """
    Retrieve a saved recommendation memo by analysis ID.
    
    Returns the recommendation memo text.
    """
    memo = analysis_service.get_recommendation(id)
    
    if not memo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation for analysis ID {id} not found"
        )
    
    return RecommendationResponse(
        analysis_id=id,
        memo=memo
    )



@router.post("/export/pdf", status_code=status.HTTP_200_OK)
async def export_pdf(request: ExportRequest):
    """
    Export recommendation memo as PDF.
    
    Returns a PDF file.
    """
    memo = analysis_service.get_recommendation(request.analysis_id)
    
    if not memo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation for analysis ID {request.analysis_id} not found"
        )
    
    try:
        pdf_bytes = export_service.generate_pdf(memo)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=recommendation_{request.analysis_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@router.post("/export/docx", status_code=status.HTTP_200_OK)
async def export_docx(request: ExportRequest):
    """
    Export recommendation memo as DOCX.
    
    Returns a DOCX file.
    """
    memo = analysis_service.get_recommendation(request.analysis_id)
    
    if not memo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation for analysis ID {request.analysis_id} not found"
        )
    
    try:
        docx_bytes = export_service.generate_docx(memo)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=recommendation_{request.analysis_id}.docx"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate DOCX: {str(e)}"
        )
