try:
    from docx import Document
except ImportError as e:
    raise ImportError(f"Failed to import python-docx. Please ensure it's installed correctly: {str(e)}")

from typing import Dict, List, Optional, Tuple
import logging
import re
from datetime import datetime
import json

# Configure detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParser:
    """Advanced resume parsing with intelligent section detection and structured output."""

    def __init__(self):
        """Initialize the parser with enhanced section detection patterns."""
        logger.info("Initializing ResumeParser")
        self.document = None
        self.section_headers = {
            'contact': [
                r'contact\s*info(rmation)?',
                r'personal\s*info(rmation)?',
                r'personal\s*details'
            ],
            'education': [
                r'education(\s*and\s*training)?',
                r'academic(\s*background)?',
                r'qualifications?',
                r'educational\s*background'
            ],
            'experience': [
                r'experience',
                r'work\s*experience',
                r'employment(\s*history)?',
                r'professional\s*experience',
                r'work\s*history'
            ],
            'skills': [
                r'skills(\s*&?\s*abilities)?',
                r'technical\s*skills',
                r'core\s*competencies',
                r'expertise',
                r'proficiencies'
            ]
        }
        logger.info("ResumeParser initialized successfully")

    def _normalize_text(self, text: str) -> str:
        """Normalize text with enhanced character handling."""
        if not text:
            return ""
        text = text.lower().strip()
        text = ' '.join(text.split())
        text = re.sub(r'[•●○▪▫◦⦿⦾⭐►▻▸▹➜➤➢➣➪➱➾]', '•', text)
        text = re.sub(r'[^\w\s.,;:•\-()]', '', text)
        return text

    def _identify_section(self, paragraph: str) -> Optional[str]:
        """
        Enhanced section identification with regex pattern matching.

        Args:
            paragraph (str): Paragraph text to analyze

        Returns:
            Optional[str]: Section name if identified, None otherwise
        """
        normalized_text = self._normalize_text(paragraph)

        for section, patterns in self.section_headers.items():
            for pattern in patterns:
                if re.search(pattern, normalized_text):
                    logger.info(f"Identified section: {section} from text: {normalized_text}")
                    return section
        return None

    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """
        Extract contact information using regex patterns.

        Args:
            text (str): Text to extract contact info from

        Returns:
            Dict[str, str]: Extracted contact information
        """
        contact_info = {
            'name': '',
            'email': '',
            'phone': '',
            'location': ''
        }

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()

        # Phone pattern
        phone_pattern = r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()

        # Location pattern (City, State/Province)
        location_pattern = r'\b[A-Za-z\s]+,\s*[A-Za-z\s]+\b'
        location_match = re.search(location_pattern, text)
        if location_match:
            contact_info['location'] = location_match.group()

        return contact_info

    def _extract_education(self, paragraphs: List[str]) -> List[Dict[str, str]]:
        """
        Extract education information with degree and date detection.

        Args:
            paragraphs (List[str]): Education section paragraphs

        Returns:
            List[Dict[str, str]]: List of education entries
        """
        education = []
        current_entry = {}

        degree_patterns = [
            r'\b(?:B\.?S\.?|B\.?A\.?|M\.?S\.?|M\.?A\.?|Ph\.?D\.?|M\.?B\.?A\.?)\b',
            r'\b(?:Bachelor|Master|Doctor|Doctorate)\b'
        ]

        date_pattern = r'\b(19|20)\d{2}\b'

        for para in paragraphs:
            if any(re.search(pattern, para, re.I) for pattern in degree_patterns):
                if current_entry:
                    education.append(current_entry)
                current_entry = {
                    'institution': '',
                    'degree': '',
                    'graduation_year': '',
                    'field': ''
                }

                # Extract degree
                for pattern in degree_patterns:
                    degree_match = re.search(pattern, para, re.I)
                    if degree_match:
                        current_entry['degree'] = degree_match.group()
                        break

                # Extract year
                year_match = re.search(date_pattern, para)
                if year_match:
                    current_entry['graduation_year'] = year_match.group()

                # Extract institution (usually the first line)
                current_entry['institution'] = re.sub(
                    f"{current_entry['degree']}|{current_entry['graduation_year']}", 
                    '', 
                    para
                ).strip()

        if current_entry:
            education.append(current_entry)

        return education

    def _extract_experience(self, paragraphs: List[str]) -> List[Dict[str, any]]:
        """
        Extract work experience with enhanced date and position detection.

        Args:
            paragraphs (List[str]): Experience section paragraphs

        Returns:
            List[Dict[str, any]]: List of experience entries
        """
        experience = []
        current_entry = {}

        date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*(?:\d{4})'

        for para in paragraphs:
            # New entry typically starts with company name and dates
            if re.search(date_pattern, para):
                if current_entry:
                    experience.append(current_entry)
                current_entry = {
                    'company': '',
                    'position': '',
                    'duration': '',
                    'description': [],
                    'achievements': []
                }

                # Extract dates
                dates = re.findall(date_pattern, para)
                if len(dates) >= 2:
                    current_entry['duration'] = f"{dates[0]} - {dates[1]}"
                elif len(dates) == 1:
                    current_entry['duration'] = f"{dates[0]} - Present"

                # Extract company and position
                company_position = re.sub(date_pattern, '', para).strip()
                parts = company_position.split('-')
                if len(parts) >= 2:
                    current_entry['company'] = parts[0].strip()
                    current_entry['position'] = parts[1].strip()
                else:
                    current_entry['company'] = company_position

            # Bullet points typically indicate responsibilities or achievements
            elif '•' in para:
                if current_entry:
                    if any(word in para.lower() for word in ['achieved', 'increased', 'improved', 'reduced', 'led']):
                        current_entry['achievements'].append(para.replace('•', '').strip())
                    else:
                        current_entry['description'].append(para.replace('•', '').strip())

        if current_entry:
            experience.append(current_entry)

        return experience

    def _extract_skills(self, paragraphs: List[str]) -> Dict[str, List[str]]:
        """
        Extract and categorize skills.

        Args:
            paragraphs (List[str]): Skills section paragraphs

        Returns:
            Dict[str, List[str]]: Categorized skills
        """
        skills = {
            'technical': [],
            'soft': [],
            'languages': [],
            'tools': []
        }

        technical_indicators = ['programming', 'software', 'database', 'framework', 'technology']
        soft_indicators = ['communication', 'leadership', 'management', 'teamwork', 'problem solving']
        language_indicators = ['fluent in', 'native', 'bilingual', 'spoken', 'written']
        tool_indicators = ['tools', 'platforms', 'applications', 'software']

        for para in paragraphs:
            skills_list = [s.strip() for s in re.split(r'[,;•]', para) if s.strip()]

            for skill in skills_list:
                skill_lower = skill.lower()

                # Categorize based on indicators
                if any(ind in skill_lower for ind in technical_indicators):
                    skills['technical'].append(skill)
                elif any(ind in skill_lower for ind in soft_indicators):
                    skills['soft'].append(skill)
                elif any(ind in skill_lower for ind in language_indicators):
                    skills['languages'].append(skill)
                elif any(ind in skill_lower for ind in tool_indicators):
                    skills['tools'].append(skill)
                else:
                    # Default to technical if no clear category
                    skills['technical'].append(skill)

        return skills

    def parse_docx(self, file_path: str) -> Dict[str, any]:
        """Parse DOCX resume with enhanced section detection."""
        if not file_path:
            logger.error("File path is empty")
            raise ValueError("File path cannot be empty")

        try:
            logger.info(f"Attempting to parse DOCX file: {file_path}")
            self.document = Document(file_path)

            sections_content = {
                'contact': [],
                'education': [],
                'experience': [],
                'skills': [],
                'unknown': []
            }

            current_section = None

            # First pass: Collect content by section
            for paragraph in self.document.paragraphs:
                text = paragraph.text.strip()
                if not text:
                    continue

                # Check for section headers
                section = self._identify_section(text)
                if section:
                    logger.info(f"Found section header: {section}")
                    current_section = section
                    continue

                # Add content to appropriate section
                if current_section:
                    sections_content[current_section].append(text)
                else:
                    # Try to identify contact info
                    if any(re.search(pattern, text.lower()) for pattern in 
                          [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                           r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b']):
                        sections_content['contact'].append(text)
                        logger.info("Found contact information outside of contact section")
                    else:
                        sections_content['unknown'].append(text)

            logger.info("Initial parsing completed. Processing sections...")

            # Process sections with specialized extractors
            parsed_content = {
                'contact': self._extract_contact_info('\n'.join(sections_content['contact'])),
                'education': self._extract_education(sections_content['education']),
                'experience': self._extract_experience(sections_content['experience']),
                'skills': self._extract_skills(sections_content['skills']),
                'metadata': {
                    'parsed_at': datetime.now().isoformat(),
                    'sections_found': [k for k, v in sections_content.items() if v and k != 'unknown'],
                }
            }

            logger.info(f"Successfully parsed resume with sections: {parsed_content['metadata']['sections_found']}")
            return parsed_content

        except Exception as e:
            logger.error(f"Error parsing DOCX file: {str(e)}")
            raise