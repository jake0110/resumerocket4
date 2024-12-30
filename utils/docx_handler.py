from docx import Document
from pathlib import Path
from typing import Dict, Union, Optional
import logging

class DocxHandler:
    def __init__(self, logging_level: int = logging.INFO):
        self.logger = self._setup_logging(logging_level)

    def _setup_logging(self, level: int) -> logging.Logger:
        logger = logging.getLogger('DocxHandler')
        logger.setLevel(level)
        return logger

    def extract_text(self, file_path: Union[str, Path]) -> Dict[str, Union[str, bool]]:
        try:
            doc = Document(file_path)
            full_text = []
            
            # Extract text from paragraphs
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():  # Skip empty paragraphs
                    full_text.append(paragraph.text)
            
            return {
                'success': True,
                'content': '\n'.join(full_text),
                'error': None
            }
            
        except Exception as e:
            self.logger.error(f'Error processing document: {str(e)}')
            return {
                'success': False,
                'content': None,
                'error': str(e)
            } 