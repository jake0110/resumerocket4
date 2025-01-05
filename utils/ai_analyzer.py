import os
import logging
from openai import OpenAI
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    """AI-powered resume analysis using OpenAI GPT."""

    def __init__(self):
        """Initialize the OpenAI client with API key from environment."""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
            )

        self.client = OpenAI(api_key=self.api_key)
        # Use gpt-4-turbo-preview as it's the latest model as of January 2024
        self.model = "gpt-4-turbo-preview"

    def analyze_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze resume content using GPT and provide structured feedback.

        Args:
            resume_data: Dictionary containing parsed resume sections and user context

        Returns:
            Dictionary containing analysis results
        """
        try:
            # Construct the analysis prompt
            prompt = self._construct_analysis_prompt(resume_data)

            # Get GPT analysis
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "system",
                    "content": """You are an expert resume analyst. 
                    Analyze the resume and provide feedback in JSON format with the following structure:
                    {
                        "overall_score": (1-10 score),
                        "strengths": [list of key strengths],
                        "weaknesses": [list of areas needing improvement],
                        "suggestions": [specific actionable suggestions],
                        "analysis": "detailed analysis explanation focusing on content quality and impact"
                    }"""
                }, {
                    "role": "user",
                    "content": prompt
                }],
                response_format={"type": "json_object"}
            )

            # Parse and return the analysis
            analysis = response.choices[0].message.content
            logger.info("Successfully analyzed resume with GPT")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            raise

    def _construct_analysis_prompt(self, resume_data: Dict[str, Any]) -> str:
        """Construct a detailed prompt for GPT analysis."""
        sections = []

        # Add user context
        if resume_data.get('user_context'):
            context = resume_data['user_context']
            sections.append("User Context:")
            sections.extend([
                f"- Name: {context.get('name', 'Not provided')}",
                f"- Role: {context.get('role', 'Not provided')}",
                f"- Email: {context.get('email', 'Not provided')}"
            ])

        # Add contact information
        if resume_data.get('contact'):
            sections.append("\nContact Information:")
            contact = resume_data['contact']
            sections.extend([
                f"- Name: {contact.get('name', 'Not provided')}",
                f"- Email: {contact.get('email', 'Not provided')}",
                f"- Phone: {contact.get('phone', 'Not provided')}",
                f"- Location: {contact.get('location', 'Not provided')}"
            ])

        # Add education
        if resume_data.get('education'):
            sections.append("\nEducation:")
            for edu in resume_data['education']:
                sections.append(
                    f"- {edu.get('degree', '')} from {edu.get('institution', '')} "
                    f"({edu.get('graduation_year', '')})"
                )

        # Add experience
        if resume_data.get('experience'):
            sections.append("\nExperience:")
            for exp in resume_data['experience']:
                sections.append(f"- {exp.get('position', '')} at {exp.get('company', '')}")
                sections.append(f"  Duration: {exp.get('duration', '')}")
                if exp.get('description'):
                    sections.extend([f"  • {item}" for item in exp['description']])

        # Add skills
        if resume_data.get('skills'):
            sections.append("\nSkills:")
            sections.append(", ".join(resume_data['skills']))

        # Construct final prompt with role-specific context
        role = resume_data.get('user_context', {}).get('role', '')
        sections.append(f"\nAnalyzing for role: {role}")

        prompt = "\n".join([
            "Please analyze this resume thoroughly for the specified role, focusing on:",
            "1. Alignment of experience and skills with the target role",
            "2. Impact and achievement presentation",
            "3. Overall professional narrative",
            "4. Areas for enhancement specific to the role",
            "\nResume Content:",
            "\n".join(sections)
        ])

        return prompt