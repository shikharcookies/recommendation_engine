import re
from io import BytesIO
from typing import Optional
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document


class TextExtractionService:
    def extract_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF file bytes."""
        try:
            text = pdf_extract_text(BytesIO(file_bytes))
            return self.clean_text(text)
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_from_docx(self, file_bytes: bytes) -> str:
        """Extract text from DOCX file bytes."""
        try:
            doc = Document(BytesIO(file_bytes))
            paragraphs = [para.text for para in doc.paragraphs]
            text = "\n".join(paragraphs)
            return self.clean_text(text)
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove control characters except newlines and tabs
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize whitespace (multiple spaces to single space)
        text = re.sub(r' +', ' ', text)
        
        # Normalize multiple newlines to maximum of 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
