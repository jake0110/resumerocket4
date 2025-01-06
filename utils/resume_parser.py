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
    """Resume parser with improved pattern matching and error handling."""

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

            # Extract text with font information for better name detection
            paragraphs = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    # Check if text is likely a header by checking font properties
                    is_header = False
                    font_size = None
                    is_bold = False

                    for run in para.runs:
                        if hasattr(run.font, 'size') and run.font.size:
                            try:
                                # Convert to points if necessary (some files store in half-points)
                                font_size = float(run.font.size) / 12700 if run.font.size > 100 else float(run.font.size)
                                if font_size > 12:
                                    is_header = True
                            except (ValueError, TypeError):
                                pass

                        if run.font.bold:
                            is_bold = True
                            is_header = True

                    paragraphs.append({
                        'text': text,
                        'is_header': is_header,
                        'font_size': font_size,
                        'is_bold': is_bold,
                        'original_paragraph': para
                    })
                    logger.debug(f"Extracted paragraph: {text[:50]}... (Header: {is_header}, Font size: {font_size}, Bold: {is_bold})")

            if not paragraphs:
                logger.warning("No content found in document")
                return {'contact': {}, 'experience': []}

            # Extract contact information with improved detection
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

    def _extract_contact_info(self, paragraphs: List[Dict]) -> Dict:
        """Extract contact information with improved pattern matching."""
        contact_info = {
            'name': 'No information available',
            'email': 'No information available',
            'phone': 'No information available',
            'location': 'No information available'
        }

        # Enhanced patterns for better matching
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',    # (123) 456-7890
            r'\+\d{1,2}\s*\d{3}[-.]?\d{3}[-.]?\d{4}',  # +1 123-456-7890
            r'\b\d{3}[.]?\d{3}[.]?\d{4}\b'  # 123.456.7890
        ]
        location_patterns = [
            r'(?i)(\d+\s+[A-Za-z\s]+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard)[.,]?\s+[A-Z]{2}\s*\d{5}(?:-\d{4})?)',  # Full address
            r'(?i)(.*?,\s*[A-Z]{2}\s*\d{5}(?:-\d{4})?)',  # City, ST 12345
            r'(?i)([A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5})',     # City, ST 12345 without comma
            r'(?i)([A-Za-z\s]+,\s*[A-Z]{2})'              # City, ST
        ]

        # Process first few paragraphs for name detection
        for i, para in enumerate(paragraphs[:5]):  # Look at first 5 paragraphs
            text = para['text'].strip()
            is_header = para['is_header']
            is_bold = para.get('is_bold', False)
            font_size = para.get('font_size')

            # Enhanced name detection with improved logic
            if contact_info['name'] == 'No information available':
                words = text.split()
                name_at_top = i < 2  # Name is typically in first two paragraphs

                # Check for likely name format
                if 1 <= len(words) <= 4 and (is_header or is_bold or name_at_top):
                    # Validate name format
                    valid_name = True
                    for word in words:
                        # Allow for different name formats
                        if not (
                            (word[0].isupper() and word[1:].islower()) or  # Standard capitalization
                            (len(word) == 2 and word[0].isupper() and word[1] == '.') or  # Initials
                            word.isupper() or  # All caps
                            word in ['van', 'de', 'la', 'von', 'der']  # Common name particles
                        ):
                            valid_name = False
                            break

                    # Additional validation
                    if valid_name and not any(word.lower() in text.lower() 
                                          for word in ['resume', 'cv', 'curriculum', 'vitae', 
                                                     'experience', 'education', 'skills']):
                        contact_info['name'] = text
                        logger.info(f"Found name: {text}")

            # Email detection
            if contact_info['email'] == 'No information available':
                email_matches = re.findall(email_pattern, text.lower())
                if email_matches:
                    contact_info['email'] = email_matches[0]
                    logger.info(f"Found email: {email_matches[0]}")

            # Phone detection with improved cleaning
            if contact_info['phone'] == 'No information available':
                for pattern in phone_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        # Clean phone number format
                        phone = matches[0]
                        # Keep only digits and plus sign
                        phone = ''.join(c for c in phone if c.isdigit() or c == '+')
                        if len(phone) >= 10:  # Valid phone numbers should have at least 10 digits
                            contact_info['phone'] = phone
                            logger.info(f"Found phone: {phone}")
                            break

            # Location detection with improved patterns
            if contact_info['location'] == 'No information available':
                for pattern in location_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        location = matches[0]
                        if isinstance(location, tuple):
                            location = location[0]
                        location = location.strip()
                        # Normalize spaces and remove extra commas
                        location = re.sub(r'\s+', ' ', location)
                        location = re.sub(r',\s*,', ',', location)
                        location = location.strip(' ,')
                        contact_info['location'] = location
                        logger.info(f"Found location: {location}")
                        break

        # Log any missing fields
        missing_fields = [field for field, value in contact_info.items() 
                         if value == 'No information available']
        if missing_fields:
            logger.warning(f"Missing contact information fields: {', '.join(missing_fields)}")

        return contact_info

    def _extract_experience(self, paragraphs: List[Dict]) -> List[Dict]:
        """Extract experience entries with improved detection."""
        experiences = []
        current_exp = None
        in_experience_section = False

        try:
            for para in paragraphs:
                text = para['text'].strip()
                is_header = para['is_header']

                if not text:
                    continue

                # Detect experience section with more variations
                if any(keyword in text.lower() for keyword in 
                      ['experience', 'work history', 'employment', 'professional experience',
                       'career history', 'work experience']):
                    in_experience_section = True
                    logger.debug(f"Found experience section: {text}")
                    continue

                if not in_experience_section:
                    continue

                # New experience entry detection with improved logic
                if (is_header or 
                    (text[0].isupper() and len(text.split()) <= 4) or
                    any(text.lower().startswith(prefix) for prefix in ['senior ', 'lead ', 'chief '])):

                    if current_exp and current_exp.get('company'):
                        experiences.append(current_exp)

                    current_exp = {
                        'company': text,
                        'position': '',
                        'duration': '',
                        'description': []
                    }
                elif current_exp:
                    # Improved categorization of lines
                    if not current_exp['position'] and text[0].isupper():
                        current_exp['position'] = text
                    elif not current_exp['duration'] and re.search(r'\b(19|20)\d{2}\b|present|current', text.lower()):
                        current_exp['duration'] = text
                    else:
                        # Remove bullet points and normalize
                        cleaned_text = re.sub(r'^[-•●\s]+', '', text).strip()
                        if cleaned_text:
                            current_exp['description'].append(cleaned_text)

            # Add final experience entry
            if current_exp and current_exp.get('company'):
                experiences.append(current_exp)

            logger.info(f"Extracted {len(experiences)} experience entries")
            return experiences

        except Exception as e:
            logger.error(f"Error extracting experience: {str(e)}", exc_info=True)
            return []

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