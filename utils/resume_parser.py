"""Resume parsing module with improved error handling and logging."""
import logging
import re
from typing import Dict, Optional, List
import json
import os
import requests
try:
    from docx import Document
except ImportError as e:
    logging.error(f"Failed to import python-docx: {str(e)}")
    raise ImportError("Please ensure python-docx is installed: pip install python-docx")

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ResumeParser:
    """Resume parsing with improved error handling."""

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the parser with optional OpenAI API key."""
        self.api_key = openai_api_key
        logger.debug("ResumeParser initialized")

    def parse_docx(self, file_path: str) -> Dict:
        """Parse DOCX resume file with enhanced error handling."""
        logger.info(f"Starting to parse DOCX file: {file_path}")

        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                raise FileNotFoundError(f"File not found: {file_path}")

            try:
                doc = Document(file_path)
            except Exception as e:
                logger.error(f"Error opening document: {str(e)}")
                raise ValueError(f"Error opening document. Please ensure it's a valid .docx file: {str(e)}")

            paragraphs = []

            # Extract text with detailed logging
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    paragraphs.append(text)
                    logger.debug(f"Extracted paragraph: {text[:50]}...")

            if not paragraphs:
                logger.warning("No content found in document")
                return {'contact': {}, 'experience': []}

            # Extract structured information
            contact_info = self._extract_contact_info(paragraphs)
            experience = self._extract_experience(paragraphs)

            result = {
                'contact': contact_info,
                'experience': experience
            }

            logger.info("Successfully parsed resume")
            return result

        except Exception as e:
            logger.error(f"Error parsing DOCX: {str(e)}", exc_info=True)
            raise

    def _extract_contact_info(self, paragraphs: List[str]) -> Dict:
        """Extract contact information with improved pattern matching."""
        contact_info = {
            'name': '',
            'email': '',
            'phone': '',
            'location': ''
        }

        # Improved patterns for better matching
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',    # (123) 456-7890
            r'\+\d{1,2}\s*\d{3}[-.]?\d{3}[-.]?\d{4}',  # +1 123-456-7890
            r'\b\d{10}\b'  # 1234567890
        ]
        location_patterns = [
            r'(?i)(.*?,\s*[A-Z]{2}\s*\d{5}(?:-\d{4})?)',  # City, ST 12345
            r'(?i)(.*?,\s*[A-Z]{2}(?:\s+\d{5})?)',  # City, ST
            r'(?i)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})'  # City, ST
        ]

        # Name detection with improved logic
        for para in paragraphs:
            text = para.strip()
            if not text:
                continue

            # Name detection - look for professional name formats
            words = text.split()
            if not contact_info['name'] and len(words) <= 4:  # Allow up to 4 words for names
                # Check if it looks like a name (proper capitalization, no special chars)
                if all(word[0].isupper() and word[1:].islower() and word.isalpha() for word in words):
                    # Additional validation - ensure it's not a company name or location
                    if not any(common_word in text.lower() for common_word in ['inc', 'llc', 'corp', 'street', 'road', 'ave']):
                        contact_info['name'] = text
                        logger.info(f"Found name: {text}")

            # Email detection
            if not contact_info['email']:
                email_matches = re.findall(email_pattern, text.lower())
                if email_matches:
                    contact_info['email'] = email_matches[0]
                    logger.info(f"Found email: {contact_info['email']}")

            # Phone detection
            if not contact_info['phone']:
                for pattern in phone_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        # Clean up phone format
                        phone = re.sub(r'[^\d+]', '', matches[0])
                        if len(phone) >= 10:
                            contact_info['phone'] = phone
                            logger.info(f"Found phone: {phone}")
                            break

            # Location detection
            if not contact_info['location']:
                for pattern in location_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        location = matches[0].strip()
                        contact_info['location'] = location
                        logger.info(f"Found location: {location}")
                        break

        # Log missing fields for debugging
        missing_fields = [field for field, value in contact_info.items() if not value]
        if missing_fields:
            logger.warning(f"Missing contact information fields: {', '.join(missing_fields)}")

        logger.debug(f"Extracted contact info: {contact_info}")
        return contact_info

    def _extract_experience(self, paragraphs: List[str]) -> List[Dict]:
        """Extract experience entries with improved detection."""
        experiences = []
        current_exp = None
        in_experience_section = False

        experience_headers = ['experience', 'work history', 'employment']

        for para in paragraphs:
            text = para.strip()
            if not text:
                continue

            # Detect experience section
            if any(header in text.lower() for header in experience_headers):
                in_experience_section = True
                logger.debug("Found experience section")
                continue

            if not in_experience_section:
                continue

            # New experience entry detection
            if text[0].isupper() and len(text.split()) <= 4:
                if current_exp:
                    experiences.append(current_exp)

                current_exp = {
                    'company': text,
                    'position': '',
                    'duration': '',
                    'description': []
                }
            elif current_exp:
                # Categorize the line
                if not current_exp['position'] and text[0].isupper():
                    current_exp['position'] = text
                elif not current_exp['duration'] and any(x in text.lower() for x in ['present', '20', '19']):
                    current_exp['duration'] = text
                else:
                    current_exp['description'].append(text)

        # Add final experience entry
        if current_exp:
            experiences.append(current_exp)

        logger.info(f"Extracted {len(experiences)} experience entries")
        return experiences

    def enhance_with_ai(self, parsed_data: Dict) -> Dict:
        """Enhance parsed data with AI analysis."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required for AI analysis")

        try:
            # Prepare resume text for analysis
            resume_text = self._prepare_resume_text(parsed_data)
            logger.debug("Prepared resume text for AI analysis")

            # Make API request
            response = self._make_openai_request(resume_text)

            # Process response
            if response.status_code == 200:
                result = response.json()
                ai_analysis = json.loads(result['choices'][0]['message']['content'])
                parsed_data['ai_analysis'] = ai_analysis
                logger.info("Successfully added AI analysis")
            else:
                logger.error(f"OpenAI API error: {response.text}")
                raise Exception(f"OpenAI API error: {response.status_code}")

            return parsed_data

        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}", exc_info=True)
            raise

    def _prepare_resume_text(self, parsed_data: Dict) -> str:
        """Prepare resume text for AI analysis."""
        resume_text = []

        # Add contact information
        if 'contact' in parsed_data:
            contact = parsed_data['contact']
            resume_text.extend([
                f"Name: {contact.get('name', '')}",
                f"Email: {contact.get('email', '')}",
                f"Phone: {contact.get('phone', '')}",
                f"Location: {contact.get('location','')}",
                ""
            ])

        # Add experience information
        if 'experience' in parsed_data:
            resume_text.append("Experience:")
            for exp in parsed_data['experience']:
                resume_text.extend([
                    f"\nCompany: {exp.get('company', '')}",
                    f"Position: {exp.get('position', '')}",
                    f"Duration: {exp.get('duration', '')}",
                    "Description:"
                ])
                for desc in exp.get('description', []):
                    resume_text.append(f"- {desc}")
                resume_text.append("")

        return "\n".join(resume_text)

    def _make_openai_request(self, resume_text: str):
        """Make request to OpenAI API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional resume analyzer. Provide analysis in JSON format."
                },
                {
                    "role": "user",
                    "content": f"Analyze this resume and provide insights:\n\n{resume_text}"
                }
            ],
            "response_format": {"type": "json_object"}
        }

        return requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )