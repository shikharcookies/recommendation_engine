"""Text summarization service to convert lengthy text into bullet points."""
from typing import List
import re


class TextSummarizer:
    """Convert lengthy text into concise bullet points."""
    
    @staticmethod
    def summarize_to_bullets(text: str, max_bullets: int = 5) -> List[str]:
        """
        Convert text into bullet points.
        Handles complex text with sections, arrows, and multiple delimiters.
        """
        if not text or not text.strip():
            return []
        
        # Clean up the text
        text = text.strip()
        
        # Split by common section markers and delimiters
        sentences = []
        
        # First, try to split by section markers (->)
        if '->' in text:
            parts = text.split('->')
            for part in parts:
                part = part.strip()
                if part and len(part) > 10:  # Ignore very short parts
                    # Further split by sentences
                    sub_sentences = re.split(r'[.!?]\s+', part)
                    sentences.extend([s.strip() for s in sub_sentences if s.strip() and len(s.strip()) > 15])
        else:
            # Split by sentences
            sentences = re.split(r'[.!?]\s+', text)
            sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 15]
        
        # If still no good sentences, try splitting by newlines
        if not sentences:
            sentences = [s.strip() for s in text.split('\n') if s.strip() and len(s.strip()) > 15]
        
        # If still nothing, split by colons or semicolons
        if not sentences:
            sentences = re.split(r'[:;]\s+', text)
            sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 15]
        
        # If still no sentences, return the whole text as one bullet (truncated)
        if not sentences:
            return [text[:200] + '...' if len(text) > 200 else text]
        
        # Clean up bullets
        cleaned_bullets = []
        for sentence in sentences[:max_bullets * 2]:  # Get more than needed, then filter
            bullet = sentence.strip()
            
            # Remove section labels like "Ownership and Management", "Main Activity:", etc.
            bullet = re.sub(r'^[A-Z][a-z\s]+:\s*', '', bullet)
            bullet = re.sub(r'^[A-Z][a-z\s]+\s*->\s*', '', bullet)
            
            # Remove trailing periods
            if bullet.endswith('.'):
                bullet = bullet[:-1]
            
            # Skip if too short or just a label
            if len(bullet) < 20 or bullet.endswith(':'):
                continue
            
            # Truncate if too long
            if len(bullet) > 150:
                bullet = bullet[:147] + '...'
            
            cleaned_bullets.append(bullet)
            
            if len(cleaned_bullets) >= max_bullets:
                break
        
        # If we got nothing, return first 200 chars
        if not cleaned_bullets:
            return [text[:200] + '...' if len(text) > 200 else text]
        
        return cleaned_bullets[:max_bullets]
    
    @staticmethod
    def format_as_html_list(bullets: List[str]) -> str:
        """Format bullets as HTML unordered list."""
        if not bullets:
            return "<p>No information available.</p>"
        
        html = "<ul>"
        for bullet in bullets:
            html += f"<li>{bullet}</li>"
        html += "</ul>"
        return html
