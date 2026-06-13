import React, { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';

type JobStatus = 'PENDING' | 'COMPLETED' | 'FAILED';

export const UploadZone: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    
    const selectedFile = acceptedFiles[0];
    setFile(selectedFile);
    setError(null);
    setStatus('PENDING');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await apiClient.post('/docs/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setJobId(response.data.job_id);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to upload file');
      setStatus('FAILED');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/x-python': ['.py'],
      'application/javascript': ['.js'],
      'application/typescript': ['.ts']
    },
    maxFiles: 1
  });

  // Polling logic
  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;

    const pollStatus = async () => {
      if (!jobId || status !== 'PENDING') return;

      try {
        const response = await apiClient.get(`/docs/jobs/${jobId}`);
        const currentStatus = response.data.status as JobStatus;
        setStatus(currentStatus);

        if (currentStatus === 'COMPLETED') {
          // Navigate to dashboard with job data
          setTimeout(() => {
            navigate(`/dashboard/${jobId}`);
          }, 1500); // Small delay to let user see "COMPLETED" status
        } else if (currentStatus === 'FAILED') {
          setError(response.data.error_message || 'Processing failed');
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    };

    if (jobId && status === 'PENDING') {
      intervalId = setInterval(pollStatus, 2000); // Poll every 2 seconds
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [jobId, status, navigate]);

  return (
    <div className="w-full flex flex-col items-center">
      {!jobId && !error && (
        <div 
          {...getRootProps()} 
          className={`glass-panel upload-zone ${isDragActive ? 'active' : ''}`}
        >
          <input {...getInputProps()} />
          <div className="upload-icon">
            {isDragActive ? '✨' : '📄'}
          </div>
          <div className="upload-text">
            {isDragActive 
              ? 'Drop the code file here...' 
              : 'Drag & drop your backend code'}
          </div>
          <div className="upload-hint">
            Supports FastAPI (.py), Express (.js), and TS (.ts)
          </div>
        </div>
      )}

      {(jobId || error) && (
        <div className="glass-panel status-container">
          <div className="upload-text">
            {file?.name}
          </div>
          
          {status === 'PENDING' && (
            <div className="flex flex-col items-center gap-4">
              <div className="spinner"></div>
              <div className="status-badge status-pending">
                AI is analyzing routes...
              </div>
            </div>
          )}

          {status === 'COMPLETED' && (
            <div className="flex flex-col items-center gap-4">
              <div className="text-3xl">✅</div>
              <div className="status-badge status-completed">
                Analysis Complete!
              </div>
              <div className="upload-hint">Redirecting to dashboard...</div>
            </div>
          )}

          {status === 'FAILED' && (
            <div className="flex flex-col items-center gap-4">
              <div className="text-3xl">❌</div>
              <div className="status-badge status-failed">
                Analysis Failed
              </div>
              <div className="text-sm text-center max-w-xs" style={{ color: '#fca5a5' }}>
                {error}
              </div>
              <button 
                onClick={() => { setJobId(null); setFile(null); setError(null); }}
                className="mt-4 px-4 py-2 rounded-lg font-medium btn-primary"
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
