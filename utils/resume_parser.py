from docx import Document
from typing import Dict, List, Optional
import logging
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParser:
    """Handles parsing of resume documents in DOCX format with advanced text processing."""

    def __init__(self):
        """Initialize the parser with None document."""
        self.document = None
        self.section_headers = {
            'contact': ['contact', 'personal information', 'personal details'],
            'education': ['education', 'academic background', 'qualifications'],
            'experience': ['experience', 'work experience', 'employment history', 'professional experience'],
            'skills': ['skills', 'technical skills', 'competencies', 'expertise']
        }

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text by removing extra whitespace and special characters.

        Args:
            text (str): Text to normalize

        Returns:
            str: Normalized text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = ' '.join(text.split())
        # Convert to lowercase for comparison
        text = text.lower()
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,;:-]', '', text)
        return text.strip()

    def _identify_section(self, paragraph: str) -> Optional[str]:
        """
        Identify which section a paragraph belongs to based on keywords.

        Args:
            paragraph (str): Paragraph text to analyze

        Returns:
            Optional[str]: Section name if identified, None otherwise
        """
        normalized_text = self._normalize_text(paragraph)

        for section, headers in self.section_headers.items():
            if any(header in normalized_text for header in headers):
                return section
        return None

    def parse_docx(self, file_path: str) -> Dict[str, any]:
        """
        Parse a DOCX format resume file and extract its content with section identification.

        Args:
            file_path (str): Path to the DOCX file

        Returns:
            Dict[str, any]: Dictionary containing parsed resume content with sections

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

            current_section = None
            sections = {
                'contact': [],
                'education': [],
                'experience': [],
                'skills': [],
                'unknown': []
            }

            # Process paragraphs with section detection
            for paragraph in self.document.paragraphs:
                if not paragraph.text.strip():
                    continue

                # Check if this paragraph is a section header
                section = self._identify_section(paragraph.text)
                if section:
                    current_section = section
                    continue

                # Add content to appropriate section
                if current_section:
                    sections[current_section].append(self._normalize_text(paragraph.text))
                else:
                    sections['unknown'].append(self._normalize_text(paragraph.text))

            # Process tables
            tables_data = self._extract_tables()

            # Combine everything into the required format
            parsed_content = {
                'raw_text': self._extract_full_text(),
                'sections': sections,
                'tables': tables_data,
                'metadata': {
                    'parsed_at': datetime.now().isoformat(),
                    'sections_found': [k for k, v in sections.items() if v and k != 'unknown']
                }
            }

            return parsed_content

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
                row_data = [self._normalize_text(cell.text) for cell in row.cells]
                table_data.append(row_data)
            tables.append(table_data)
        return tables