from docx import Document
from pathlib import Path

def create_test_document():
    # Create output directory if it doesn't exist
    output_dir = Path('output/generated')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a new document
    doc = Document()
    doc.add_paragraph('This is a test document for checking our docx handler functionality.')
    
    # Save the document
    test_file_path = output_dir / 'test.docx'
    doc.save(test_file_path)
    return test_file_path

if __name__ == '__main__':
    file_path = create_test_document()
    print(f'Test document created at: {file_path}') 