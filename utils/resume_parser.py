"""
Module for handling resume parsing via Airparser integration through Make.com.
This module provides the interface between our application and Airparser through Make.com webhooks.
"""
import logging
import os
import json
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)

class AirparserMakeIntegration:
    """Handles interaction with Airparser via Make.com webhooks."""

    def __init__(self):
        self.make_webhook_url = os.getenv('MAKE_WEBHOOK_URL')
        self.make_status_url = os.getenv('MAKE_STATUS_URL')

    def prepare_file_for_parsing(self, file_path: str, file_content: bytes, file_name: str) -> Dict[str, Any]:
        """
        Prepares and sends a file to Airparser via Make.com webhook.

        Args:
            file_path: Path to the temporary file
            file_content: Binary content of the file
            file_name: Original filename

        Returns:
            Dict containing parsing status and job ID
        """
        try:
            if not self.make_webhook_url:
                logger.warning("Make.com webhook URL not configured")
                return {
                    'status': 'error',
                    'message': 'Make.com integration not configured'
                }

            # Prepare multipart form data
            files = {
                'resume': (file_name, file_content, 'application/octet-stream')
            }

            # Send to Make.com webhook
            response = requests.post(
                self.make_webhook_url,
                files=files,
                timeout=30
            )

            if response.status_code == 200:
                try:
                    result = response.json()
                    return {
                        'status': 'pending',
                        'job_id': result.get('job_id'),
                        'message': 'File sent to Airparser for processing'
                    }
                except json.JSONDecodeError:
                    return {
                        'status': 'error',
                        'message': 'Invalid response from Make.com webhook'
                    }
            else:
                return {
                    'status': 'error',
                    'message': f'Failed to send file to Make.com: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"Error preparing file for Airparser: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error preparing file: {str(e)}'
            }

    def check_parsing_status(self, job_id: str) -> Dict[str, Any]:
        """
        Checks the status of a parsing job.

        Args:
            job_id: The job ID returned from the initial upload

        Returns:
            Dict containing current status and parsed data if available
        """
        if not self.make_status_url:
            return {
                'status': 'error',
                'message': 'Status check URL not configured'
            }

        try:
            response = requests.get(
                f"{self.make_status_url}?job_id={job_id}",
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': 'error',
                    'message': f'Failed to check parsing status: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"Error checking parsing status: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error checking status: {str(e)}'
            }

def process_resume(file_path: str, file_content: bytes, file_name: str) -> Dict[str, Any]:
    """
    Main interface function for resume processing.
    Handles the complete flow from file receipt to parsed data return.

    Args:
        file_path: Path to the temporary file
        file_content: Binary content of the file
        file_name: Original filename

    Returns:
        Dict containing processing status and any parsed data
    """
    parser = AirparserMakeIntegration()

    # Send file to Airparser via Make.com
    upload_result = parser.prepare_file_for_parsing(file_path, file_content, file_name)

    if upload_result['status'] == 'error':
        return upload_result

    # Return initial status - the frontend will poll for updates
    return {
        'status': 'pending',
        'job_id': upload_result.get('job_id'),
        'message': 'Resume submitted for parsing'
    }