import os
import pytest
from app import create_app
from app.models import db

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

def test_file_upload(app):
    with open('test.docx', 'w') as f:
        f.write('test content')
    
    client = app.test_client()
    with open('test.docx', 'rb') as f:
        response = client.post('/', 
            data={'file': (f, 'test.docx')},
            content_type='multipart/form-data')

    assert b'uploaded successfully' in response.data
    os.remove('test.docx') 