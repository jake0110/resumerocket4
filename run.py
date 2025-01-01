from app import create_app
from app.models import db, UploadedFile

app = create_app()
with app.app_context():
    file = UploadedFile.query.first()
    print(f"ID: {file.id}")
    print(f"Filename: {file.filename}")
    print(f"Size: {file.file_size}")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8081, debug=True) 