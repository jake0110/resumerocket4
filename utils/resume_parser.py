import logging
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime
import json
import requests
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
    """Advanced resume parsing with intelligent section detection and OpenAI analysis."""

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the parser with enhanced section detection patterns."""
        logger.info("Initializing ResumeParser")
        self.openai_api_key = openai_api_key
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
            ],
            'education': [
                r'education(\s*and\s*training)?',
                r'academic(\s*background)?',
                r'qualifications?',
                r'educational\s*background'
            ],
            'skills': [
                r'skills(\s*&?\s*abilities)?',
                r'technical\s*skills',
                r'core\s*competencies',
                r'expertise',
                r'proficiencies'
            ]
        }

    def analyze_with_openai(self, text: str) -> Dict[str, any]:
        """
        Use OpenAI to analyze resume content and provide insights.

        Args:
            text (str): Resume content to analyze

        Returns:
            Dict with analysis results including key skills, experience summary, and recommendations
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not provided, skipping analysis")
            return {}

        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }

            prompt = f"""Analyze this resume content and provide structured feedback:
            {text}

            Please provide analysis in the following JSON format:
            {{
                "key_skills": [list of most important skills],
                "experience_summary": "brief overview of experience",
                "improvement_suggestions": [list of specific suggestions],
                "best_suited_roles": [list of recommended job titles],
                "experience_level": "junior/mid/senior based on experience"
            }}"""

            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return json.loads(result['choices'][0]['message']['content'])
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return {}

        except Exception as e:
            logger.error(f"Error analyzing resume with OpenAI: {str(e)}")
            return {}

    def _normalize_text(self, text: str) -> str:
        """Normalize text for consistent processing."""
        if not text:
            return ""
        text = text.lower().strip()
        text = ' '.join(text.split())
        text = re.sub(r'[•●○▪▫◦⦿⦾⭐►▻▸▹➜➤➢➣➪➱➾]', '•', text)
        return text


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

    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information using enhanced regex patterns."""
        contact_info = {
            'name': 'No information available',
            'email': 'No information available',
            'phone': 'No information available',
            'location': 'No information available',
            'linkedin': 'No information available'
        }

        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()

        # Extract phone with international format support
        phone_pattern = r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()

        # Extract location (City, State/Province, Country)
        location_pattern = r'\b[A-Za-z\s]+,\s*[A-Za-z\s]+(?:,\s*[A-Za-z\s]+)?\b'
        location_match = re.search(location_pattern, text)
        if location_match:
            contact_info['location'] = location_match.group()

        # Extract LinkedIn profile
        linkedin_pattern = r'(?:linkedin\.com/in/|linkedin\.com/profile/view\?id=)[a-zA-Z0-9-]+(?:/)?'
        linkedin_match = re.search(linkedin_pattern, text.lower())
        if linkedin_match:
            contact_info['linkedin'] = "linkedin.com/in/" + linkedin_match.group().split('/')[-2]

        # Extract name (assuming it's at the beginning of the document)
        name_lines = text.split('\n')[:3]  # Check first 3 lines
        for line in name_lines:
            line = line.strip()
            # Name should be 2-4 words, each capitalized, no special characters
            if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}$', line):
                contact_info['name'] = line
                break

        return contact_info

    def _extract_most_recent_position(self, paragraphs: List[str]) -> Dict[str, str]:
        """Extract only the most recent position from work experience."""
        most_recent = {
            'company': 'No information available',
            'position': 'No information available',
            'duration': 'No information available'
        }

        if not paragraphs:
            return most_recent

        current_entry = None
        date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*(?:\d{4})'

        for para in paragraphs:
            if not para.strip():
                continue

            # Check if this is a position entry (contains a date)
            if re.search(date_pattern, para):
                # Extract dates
                dates = re.findall(date_pattern, para)
                duration = ''
                if len(dates) >= 2:
                    duration = f"{dates[0]} - {dates[1]}"
                elif len(dates) == 1:
                    duration = f"{dates[0]} - Present"

                # Extract company and position
                company_position = re.sub(date_pattern, '', para).strip()
                company = position = 'No information available'

                if ' - ' in company_position:
                    parts = company_position.split(' - ')
                    company = parts[0].strip()
                    position = parts[1].strip()
                else:
                    company = company_position

                # Since we want the most recent position, we return the first one found
                return {
                    'company': company,
                    'position': position,
                    'duration': duration
                }

        return most_recent


    def _extract_education(self, paragraphs: List[str]) -> List[Dict[str, str]]:
        """Extract education information with enhanced pattern matching."""
        education_entries = []

        for para in paragraphs:
            if not para.strip():
                continue

            entry = {
                'institution': '',
                'degree': '',
                'graduation_year': ''
            }

            # Extract year
            year_match = re.search(r'\b(19|20)\d{2}\b', para)
            if year_match:
                entry['graduation_year'] = year_match.group()

            # Extract degree
            degree_patterns = [
                r'\b(?:B\.?S\.?|B\.?A\.?|M\.?S\.?|M\.?A\.?|Ph\.?D\.?|M\.?B\.?A\.?)\b',
                r'\b(?:Bachelor|Master|Doctor|Doctorate)\b'
            ]
            for pattern in degree_patterns:
                degree_match = re.search(pattern, para, re.I)
                if degree_match:
                    entry['degree'] = degree_match.group()
                    break

            # Institution is typically what remains after removing degree and year
            entry['institution'] = re.sub(
                f"{entry['degree']}|{entry['graduation_year']}",
                '',
                para
            ).strip()

            if any(entry.values()):
                education_entries.append(entry)

        return education_entries

    def _extract_experience(self, paragraphs: List[str]) -> List[Dict[str, any]]:
        return self._extract_most_recent_position(paragraphs)


    def _extract_skills(self, paragraphs: List[str]) -> List[str]:
        """Extract and normalize skills."""
        skills = []

        for para in paragraphs:
            # Split on common delimiters
            skill_list = re.split(r'[,;•]', para)
            # Clean and add non-empty skills
            skills.extend([
                skill.strip()
                for skill in skill_list
                if skill.strip()
            ])

        return list(set(skills))  # Remove duplicates

    def parse_docx(self, file_path: str, output_format: str = 'json') -> str:
        """
        Parse DOCX resume file and extract only specific requested fields.

        Args:
            file_path (str): Path to the DOCX file
            output_format (str): 'json' or 'csv'

        Returns:
            str: Parsed resume data in specified format with only requested fields
        """
        logger.info(f"Attempting to parse DOCX file: {file_path}")

        try:
            doc = Document(file_path)
            sections = {'contact': [], 'experience': [], 'unknown': []}
            current_section = None
            full_text = []

            # First pass: Collect content by section
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if not text:
                    continue

                full_text.append(text)
                section = self._identify_section(text)
                if section:
                    current_section = section
                    continue

                if current_section:
                    sections[current_section].append(text)
                else:
                    sections['unknown'].append(text)

            # Extract required information
            contact_info = self._extract_contact_info('\n'.join(sections['contact'] + sections['unknown']))
            recent_position = self._extract_most_recent_position(sections['experience'])

            # Combine only the requested fields
            parsed_data = {
                # Contact Information
                'name': contact_info['name'],
                'location': contact_info['location'],
                'email': contact_info['email'],
                'phone': contact_info['phone'],
                'linkedin': contact_info['linkedin'],
                # Most Recent Position
                'most_recent_company': recent_position['company'],
                'most_recent_title': recent_position['position'],
                'most_recent_dates': recent_position['duration']
            }

            # Format output according to preference
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