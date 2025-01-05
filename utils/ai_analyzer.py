import os
import logging
from openai import OpenAI
from typing import Dict, Any
import json

logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    """AI-powered resume analysis using OpenAI GPT."""

    def __init__(self):
        """Initialize the OpenAI client with API key from environment."""
        try:
            self.api_key = os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

            # Initialize OpenAI client - simplified initialization
            self.client = OpenAI(api_key=self.api_key)
            self.model = "gpt-4-turbo-preview"  # Latest model as of January 2024
            logger.info("Successfully initialized OpenAI client")

        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise

    def analyze_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze resume content using GPT and provide structured feedback.
        Using a simple initial prompt for testing the integration.
        """
        try:
            # Construct a simple analysis prompt for initial testing
            prompt = self._construct_analysis_prompt(resume_data)
            logger.info("Generated analysis prompt")

            # Get GPT analysis with simplified system message
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "system",
                    "content": """You are a resume analyst. Provide a basic analysis with:
                    - A score from 1-10
                    - 2-3 key strengths
                    - 2-3 areas for improvement
                    - 2-3 specific suggestions
                    - A brief overall analysis

                    Respond in JSON format:
                    {
                        "overall_score": number,
                        "strengths": [string],
                        "weaknesses": [string],
                        "suggestions": [string],
                        "analysis": "string"
                    }"""
                }, {
                    "role": "user",
                    "content": prompt
                }],
                response_format={"type": "json_object"}
            )

            # Parse and return the analysis
            analysis = json.loads(response.choices[0].message.content)
            logger.info("Successfully analyzed resume with GPT")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            raise

    def _construct_analysis_prompt(self, resume_data: Dict[str, Any]) -> str:
        """Construct a simple prompt for initial testing."""
        sections = []

        # Add basic context
        sections.append("Please analyze this resume for the following role:")
        sections.append(f"Target Role: {resume_data.get('user_context', {}).get('role', 'Not specified')}")
        sections.append("\nResume Content:")

        # Add parsed content sections
        if resume_data.get('contact'):
            sections.append("\nContact Information:")
            contact = resume_data['contact']
            sections.extend([
                f"Name: {contact.get('name', 'Not provided')}",
                f"Email: {contact.get('email', 'Not provided')}"
            ])

        if resume_data.get('education'):
            sections.append("\nEducation:")
            for edu in resume_data['education']:
                sections.append(
                    f"- {edu.get('degree', '')} from {edu.get('institution', '')} "
                    f"({edu.get('graduation_year', '')})"
                )

        if resume_data.get('experience'):
            sections.append("\nExperience:")
            for exp in resume_data['experience']:
                sections.append(f"- {exp.get('position', '')} at {exp.get('company', '')}")
                sections.append(f"  Duration: {exp.get('duration', '')}")
                if exp.get('description'):
                    sections.extend([f"  • {item}" for item in exp['description']])

        if resume_data.get('skills'):
            sections.append("\nSkills:")
            sections.append(", ".join(resume_data['skills']))

        return "\n".join(sections)