from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from docx import Document
from docx.shared import Pt


class ExportService:
    """Generate PDF and DOCX exports of recommendation memos."""
    
    def generate_pdf(self, memo: str) -> bytes:
        """Generate a PDF file from memo text."""
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        # Build content
        styles = getSampleStyleSheet()
        story = []
        
        # Split memo into paragraphs and add to story
        for line in memo.split('\n'):
            if line.strip():
                para = Paragraph(line, styles['Normal'])
                story.append(para)
                story.append(Spacer(1, 0.1 * inch))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def generate_docx(self, memo: str) -> bytes:
        """Generate a DOCX file from memo text."""
        doc = Document()
        
        # Add memo content
        for line in memo.split('\n'):
            if line.strip():
                paragraph = doc.add_paragraph(line)
                # Set font
                for run in paragraph.runs:
                    run.font.size = Pt(12)
        
        # Save to buffer
        buffer = BytesIO()
        doc.save(buffer)
        docx_bytes = buffer.getvalue()
        buffer.close()
        
        return docx_bytes
