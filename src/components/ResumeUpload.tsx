import { useState } from 'react';
import { Upload } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';

export function ResumeUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string>('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    
    if (!selectedFile) {
      return;
    }

    // Check if file is a Word document
    const isWordFile = selectedFile.name.endsWith('.doc') || selectedFile.name.endsWith('.docx');
    
    if (!isWordFile) {
      setError('Please upload a Word document (.doc or .docx)');
      setFile(null);
      return;
    }

    setError('');
    setFile(selectedFile);
  };

  return (
    <Card className="w-full max-w-md p-6">
      <div className="flex flex-col items-center gap-4">
        <div className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg hover:border-gray-400 transition-colors">
          <input
            type="file"
            accept=".doc,.docx"
            onChange={handleFileChange}
            className="hidden"
            id="resume-upload"
          />
          <label 
            htmlFor="resume-upload" 
            className="flex flex-col items-center cursor-pointer"
          >
            <Upload className="w-8 h-8 text-gray-500" />
            <span className="mt-2 text-sm text-gray-500">
              {file ? file.name : 'Upload your resume'}
            </span>
          </label>
        </div>
        
        {error && (
          <p className="text-sm text-red-500">{error}</p>
        )}

        {file && (
          <Button 
            className="w-full"
            onClick={() => {
              // Handle file upload here
              console.log('Uploading file:', file);
            }}
          >
            Upload Resume
          </Button>
        )}
      </div>
    </Card>
  );
} 