import unittest
from app import app
import os
from pathlib import Path
from docx import Document

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Ensure test upload folder exists
        self.upload_folder = Path('output/test_uploads')
        self.upload_folder.mkdir(parents=True, exist_ok=True)

    def test_index_route(self):
        """Test the index route returns 200"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_status_endpoint(self):
        """Test the status endpoint returns correct information"""
        response = self.app.get('/api/status')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'operational')
        self.assertTrue('version' in data)

    def test_upload_no_file(self):
        """Test upload endpoint with no file"""
        response = self.app.post('/api/upload')
        self.assertEqual(response.status_code, 400)

    def test_upload_invalid_file(self):
        """Test upload endpoint with invalid file type"""
        data = {
            'file': (open('requirements.txt', 'rb'), 'test.txt')
        }
        response = self.app.post('/api/upload', data=data)
        self.assertEqual(response.status_code, 400)

    def test_upload_valid_file(self):
        """Test upload endpoint with valid docx file"""
        # Create a test docx file
        test_file_path = self.upload_folder / 'test.docx'
        doc = Document()
        doc.add_paragraph('This is test content for the document')
        doc.save(test_file_path)

        data = {
            'file': (open(test_file_path, 'rb'), 'test.docx')
        }
        response = self.app.post('/api/upload', data=data)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        """Clean up test files after each test"""
        for file in self.upload_folder.glob('*'):
            file.unlink()
        self.upload_folder.rmdir()

if __name__ == '__main__':
    unittest.main()