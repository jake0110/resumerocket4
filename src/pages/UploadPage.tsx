import { ResumeUpload } from '../components/ResumeUpload';

export function UploadPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Upload Your Resume
          </h1>
          <p className="mt-2 text-gray-600">
            Upload your resume in Word format (.doc or .docx)
          </p>
        </div>
        
        <div className="flex justify-center">
          <ResumeUpload />
        </div>
      </div>
    </div>
  );
} 