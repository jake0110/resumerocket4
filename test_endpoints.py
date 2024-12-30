import requests
import json
from pathlib import Path
from utils.docx_handler import DocxHandler
import unittest
from app import app, is_valid_docx
from io import BytesIO
import os
from unittest.mock import patch, MagicMock

def test_status_endpoint():
    """Test the API status endpoint"""
    response = requests.get('http://localhost:8080/api/status')
    print("\nStatus Endpoint Test:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_upload_endpoint():
    """Test file upload with valid docx file"""
    test_file = Path('output/generated/test.docx')
    
    with open(test_file, 'rb') as f:
        files = {'file': ('test.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        response = requests.post('http://localhost:8080/api/upload', files=files)
    
    print("\nUpload Endpoint Test (Valid File):")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_invalid_file_type():
    """Test file upload with invalid file type"""
    # Create a test txt file
    test_txt = Path('test.txt')
    test_txt.write_text('This is a test text file')
    
    with open(test_txt, 'rb') as f:
        files = {'file': ('test.txt', f, 'text/plain')}
        response = requests.post('http://localhost:8080/api/upload', files=files)
    
    print("\nUpload Endpoint Test (Invalid File):")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Cleanup
    test_txt.unlink()

def test_oversized_file():
    """Test file upload with a file larger than 5MB"""
    # Create a large test file (6MB)
    test_large = Path('test_large.docx')
    with open(test_large, 'wb') as f:
        f.write(b'0' * (6 * 1024 * 1024))  # 6MB of data
    
    try:
        with open(test_large, 'rb') as f:
            files = {'file': ('test_large.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post('http://localhost:8080/api/upload', files=files)
        
        print("\nUpload Endpoint Test (Oversized File):")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    finally:
        # Cleanup
        test_large.unlink()

class TestFileUpload(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.test_files = []

    def tearDown(self):
        # Cleanup any test files created
        for test_file in self.test_files:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_valid_docx_file(self):
        valid_docx_content = b'PK\x03\x04' + b'\x00' * 100
        valid_docx = BytesIO(valid_docx_content)
        valid_docx.name = 'test.docx'

        response = self.app.post('/api/upload', data={'file': (valid_docx, 'test.docx')})
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json)
        self.assertTrue(response.json['success'])

    def test_invalid_docx_file(self):
        invalid_docx_content = b'INVALID' + b'\x00' * 100
        invalid_docx = BytesIO(invalid_docx_content)
        invalid_docx.name = 'test.docx'

        response = self.app.post('/api/upload', data={'file': (invalid_docx, 'test.docx')})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'File does not have a valid DOCX signature')

    @patch('zipfile.ZipFile')
    def test_missing_internal_structure(self, mock_zipfile):
        # Mock the zipfile to simulate missing internal structure
        mock_zip = MagicMock()
        mock_zip.namelist.return_value = []
        mock_zipfile.return_value.__enter__.return_value = mock_zip

        missing_structure_content = b'PK\x03\x04' + b'\x00' * 100
        missing_structure = BytesIO(missing_structure_content)
        missing_structure.name = 'test.docx'

        response = self.app.post('/api/upload', data={'file': (missing_structure, 'test.docx')})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'DOCX file is missing required internal structure')

    @patch('zipfile.ZipFile')
    def test_valid_zip_invalid_content(self, mock_zipfile):
        # Mock the zipfile to simulate invalid content
        mock_zip = MagicMock()
        mock_zip.namelist.return_value = ['[Content_Types].xml', 'word/']
        mock_zipfile.return_value.__enter__.return_value = mock_zip

        valid_zip_invalid_content = b'PK\x03\x04' + b'invalid content'
        invalid_content = BytesIO(valid_zip_invalid_content)
        invalid_content.name = 'test.docx'

        response = self.app.post('/api/upload', data={'file': (invalid_content, 'test.docx')})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'DOCX file content is invalid')

    def test_oversized_file(self):
        oversized_content = b'PK\x03\x04' + b'\x00' * (6 * 1024 * 1024)
        oversized_file = BytesIO(oversized_content)
        oversized_file.name = 'test_large.docx'

        response = self.app.post('/api/upload', data={'file': (oversized_file, 'test_large.docx')})
        self.assertEqual(response.status_code, 413)
        self.assertIn('error', response.json)
        self.assertTrue('File too large' in response.json['error'])

if __name__ == '__main__':
    print("Running API Tests...")
    test_status_endpoint()
    test_upload_endpoint()
    test_invalid_file_type()
    test_oversized_file()
    unittest.main() 