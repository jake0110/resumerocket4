import logging
from flask import Flask, request, render_template, jsonify
from utils.docx_handler import DocxHandler
from pathlib import Path
from werkzeug.utils import secure_filename
from uuid import uuid4
import os
import zipfile

app = Flask(__name__)
docx_handler = DocxHandler()

# Configuration
UPLOAD_FOLDER = Path('output/generated')
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB limit
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Setup logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.endswith('.docx'):
        return jsonify({'error': 'Please upload a .docx file'}), 400

    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_CONTENT_LENGTH:
        return jsonify({
            'error': f'File too large. Maximum size is {MAX_CONTENT_LENGTH/1024/1024:.1f}MB'
        }), 413

    unique_filename = f"{uuid4()}_{secure_filename(file.filename)}"
    file_path = UPLOAD_FOLDER / unique_filename

    try:
        # Check if the file is a valid DOCX
        if not is_valid_docx(file):
            return jsonify({'error': 'Invalid DOCX file'}), 400

        # Save and process file
        file.save(file_path)
        
        # Extract text
        result = docx_handler.extract_text(file_path)
        
        # Add filename to response if successful
        if result['success']:
            result['filename'] = unique_filename
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

    finally:
        # Ensure cleanup happens even if processing fails
        cleanup_file(file_path)

def cleanup_file(file_path):
    """Remove the processed file and log the operation."""
    try:
        if file_path.exists():
            file_path.unlink()
            logging.info(f"Successfully cleaned up file: {file_path}")
    except Exception as e:
        logging.error(f"Failed to clean up file {file_path}: {e}")

@app.route('/api/status')
def service_status():
    return jsonify({
        'status': 'operational',
        'version': '0.1.0',
        'upload_folder': str(UPLOAD_FOLDER)
    })

def is_valid_docx(file):
    try:
        # Check the magic number
        file.seek(0)
        magic_number = file.read(4)
        if magic_number != b'PK\x03\x04':
            return False
        
        # Check internal structure
        file.seek(0)
        with zipfile.ZipFile(file, 'r') as zip_ref:
            required_files = ['[Content_Types].xml', 'word/']
            zip_contents = zip_ref.namelist()
            for required_file in required_files:
                if not any(item.startswith(required_file) for item in zip_contents):
                    return False
        return True
    except zipfile.BadZipFile:
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

#checking CC connection with replit#