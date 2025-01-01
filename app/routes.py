from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from .models import db, UploadedFile
import os
from .ai_processor import process_resume

bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
            
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            uploaded_file = UploadedFile(
                filename=filename,
                file_size=os.path.getsize(file_path)
            )
            db.session.add(uploaded_file)
            db.session.commit()
            
            return f'File {filename} uploaded successfully!'
        else:
            flash('Only .docx files are allowed')
            return redirect(request.url)
            
    return render_template('upload.html')

@bp.route('/process/<int:file_id>', methods=['POST'])
def process_file(file_id):
    if process_resume(file_id):
        return {'status': 'success', 'message': 'Resume processed successfully'}
    return {'status': 'error', 'message': 'Processing failed'}, 400