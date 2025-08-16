"""Text Cleaner - Text preprocessing and cleaning utilities"""

import re
from typing import Dict, List


class TextCleaner:
    def __init__(self, config: Dict = None):
        self.config = config or {}
    
    def clean(self, text: str, **kwargs) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters if requested
        if kwargs.get('remove_special_chars', False):
            text = re.sub(r'[^\w\s]', '', text)
        
        # Convert to lowercase if requested
        if kwargs.get('lowercase', False):
            text = text.lower()
        
        # Strip leading/trailing whitespace
        return text.strip()
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def remove_html_tags(self, text: str) -> str:
        """Remove HTML tags from text"""
        return re.sub(r'<[^>]+>', '', text)
    
    def clean_stream(self, text: str, chunk_size: int = 8192):
        """Generator for streaming text cleaning to reduce memory usage"""
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            yield self.clean(chunk)
    
    def count_words_streaming(self, text: str, chunk_size: int = 8192) -> int:
        """Count words in streaming fashion for large texts"""
        word_count = 0
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            cleaned_chunk = self.clean(chunk)
            word_count += len(cleaned_chunk.split())
        return word_count