from docx import Document
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParser:
    """Handles parsing of resume documents in DOCX format."""

    def __init__(self):
        """Initialize the parser with None document."""
        self.document = None

    def parse_docx(self, file_path: str) -> Dict[str, str]:
        """
        Parse a DOCX format resume file and extract its content.

        Args:
            file_path (str): Path to the DOCX file

        Returns:
            Dict[str, str]: Dictionary containing parsed resume content

        Raises:
            ValueError: If file_path is invalid or file cannot be opened
            Exception: For other parsing errors
        """
        if not file_path:
            raise ValueError("File path cannot be empty")

        try:
            self.document = Document(file_path)
            if not self.document:
                raise ValueError("Failed to load document")

            content = {
                'raw_text': self._extract_full_text(),
                'paragraphs': self._extract_paragraphs(),
                'tables': self._extract_tables()
            }
            return content
        except Exception as e:
            logger.error(f"Error parsing DOCX file: {str(e)}")
            raise

    def _extract_full_text(self) -> str:
        """Extract all text content from the document."""
        if not self.document:
            return ""
        return "\n".join([paragraph.text for paragraph in self.document.paragraphs if paragraph.text.strip()])

    def _extract_paragraphs(self) -> List[str]:
        """Extract all paragraphs from the document."""
        if not self.document:
            return []
        return [para.text for para in self.document.paragraphs if para.text.strip()]

    def _extract_tables(self) -> List[List[List[str]]]:
        """Extract all tables from the document."""
        if not self.document:
            return []

        tables = []
        for table in self.document.tables:
            table_data = []
            for row in table.rows:
                row_data = [cell.text for cell in row.cells]
                table_data.append(row_data)
            tables.append(table_data)
        return tables