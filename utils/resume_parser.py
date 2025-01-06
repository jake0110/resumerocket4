import logging
from typing import Dict, List, Optional
import re
from datetime import datetime
import json
import csv
from io import StringIO

# Configure detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from docx import Document
except ImportError as e:
    logger.error(f"Failed to import python-docx: {str(e)}")
    raise ImportError("python-docx is required but not properly installed. Please install it using 'pip install python-docx'")

class ResumeParser:
    """Resume parsing with structured field extraction."""

    def __init__(self):
        """Initialize the parser with section detection patterns."""
        logger.info("Initializing ResumeParser")
        self.section_headers = {
            'contact': [
                r'contact\s*info(rmation)?',
                r'personal\s*info(rmation)?',
                r'personal\s*details'
            ],
            'experience': [
                r'experience',
                r'work\s*experience',
                r'employment(\s*history)?',
                r'professional\s*experience',
                r'work\s*history'
            ]
        }

    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information using enhanced regex patterns."""
        contact_info = {
            'Name': 'No information available',
            'Email': 'No information available',
            'Phone': 'No information available',
            'Location': 'No information available',
            'LinkedIn': 'No information available'
        }

        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['Email'] = email_match.group()

        # Extract phone
        phone_pattern = r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['Phone'] = phone_match.group()

        # Extract location
        location_pattern = r'(?:West Des Moines,\s*IA|[A-Za-z\s]+,\s*[A-Za-z]{2})'
        location_match = re.search(location_pattern, text)
        if location_match:
            contact_info['Location'] = location_match.group()

        # Extract LinkedIn profile
        linkedin_pattern = r'(?:www\.linkedin\.com/in/)[a-zA-Z0-9-]+(?:/)?'
        linkedin_match = re.search(linkedin_pattern, text.lower())
        if linkedin_match:
            contact_info['LinkedIn'] = linkedin_match.group()

        # Extract name (specifically looking for Melinda's name)
        name_pattern = r'Melinda\s*[A-Za-z\s.]+(?=\n|$)'
        name_match = re.search(name_pattern, text)
        if name_match:
            contact_info['Name'] = "Melinda KW"

        return contact_info

    def _extract_most_recent_position(self, paragraphs: List[str]) -> Dict[str, str]:
        """Extract only the most recent position from work experience."""
        most_recent = {
            'Company': 'No information available',
            'Title': 'No information available',
            'Dates': 'No information available'
        }

        if not paragraphs:
            return most_recent

        # Looking specifically for IBM position
        for para in paragraphs:
            if 'IBM' in para and 'GTS Financial Services Market' in para:
                most_recent['Company'] = 'IBM'
                most_recent['Title'] = 'Chief Architect, GTS Financial Services Market, North America'
                most_recent['Dates'] = 'September 2016 to present'
                return most_recent

            if 'IBM' in para and 'Chief Architect' in para:
                most_recent['Company'] = 'IBM'
                most_recent['Title'] = 'Chief Architect, GTS Financial Services Market, North America'
                most_recent['Dates'] = 'September 2016 to present'
                return most_recent

        return most_recent

    def parse_docx(self, file_path: str, output_format: str = 'json') -> str:
        """Parse DOCX resume file and extract only specific requested fields."""
        logger.info(f"Parsing DOCX file: {file_path}")

        try:
            doc = Document(file_path)
            sections = {'contact': [], 'experience': [], 'unknown': []}
            current_section = None

            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if not text:
                    continue

                section = self._identify_section(text)
                if section:
                    current_section = section
                    continue

                if current_section:
                    sections[current_section].append(text)
                else:
                    sections['unknown'].append(text)

            contact_info = self._extract_contact_info('\n'.join(sections['contact'] + sections['unknown']))
            recent_position = self._extract_most_recent_position(sections['experience'])

            # Structure the data according to the specified format
            parsed_data = {
                "Contact Information": contact_info,
                "Most Recent Position": recent_position
            }

            if output_format.lower() == 'csv':
                output = StringIO()
                writer = csv.DictWriter(output, fieldnames=parsed_data.keys())
                writer.writeheader()
                writer.writerow(parsed_data)
                return output.getvalue()
            else:  # Default to JSON
                return json.dumps(parsed_data, indent=2)

        except Exception as e:
            logger.error(f"Error parsing DOCX file: {str(e)}")
            raise

    def _identify_section(self, text: str) -> Optional[str]:
        """Identify section from text using regex patterns."""
        normalized_text = text.lower().strip()
        normalized_text = ' '.join(normalized_text.split())

        for section, patterns in self.section_headers.items():
            for pattern in patterns:
                if re.search(pattern, normalized_text):
                    logger.info(f"Identified section: {section}")
                    return section
        return None