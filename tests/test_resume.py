import unittest
from utils.resume_parser import ResumeParser
import os
import json

class TestResumeParser(unittest.TestCase):
    def setUp(self):
        self.parser = ResumeParser()

    def test_contact_info_extraction(self):
        text = """John Doe Smith
123 Main St, New York, NY
john.doe@example.com
(555) 123-4567
linkedin.com/in/johndoe
"""
        contact_info = self.parser._extract_contact_info(text)
        self.assertEqual(contact_info['name'], 'John Doe Smith')
        self.assertEqual(contact_info['email'], 'john.doe@example.com')
        self.assertEqual(contact_info['phone'], '(555) 123-4567')
        self.assertTrue('New York' in contact_info['location'])
        self.assertEqual(contact_info['linkedin'], 'linkedin.com/in/johndoe')

    def test_missing_info_handling(self):
        text = "Some random text without contact information"
        contact_info = self.parser._extract_contact_info(text)
        self.assertEqual(contact_info['name'], 'No information available')
        self.assertEqual(contact_info['email'], 'No information available')

    def test_most_recent_position(self):
        paragraphs = [
            "Software Engineer - Tech Corp (Jan 2023 - Present)",
            "Previous role that should be ignored"
        ]
        position = self.parser._extract_most_recent_position(paragraphs)
        self.assertEqual(position['duration'], 'Jan 2023 - Present')
        self.assertTrue('Tech Corp' in position['company'])

if __name__ == '__main__':
    unittest.main()
