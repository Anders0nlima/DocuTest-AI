import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiClient } from '../api/client';
import SwaggerUI from 'swagger-ui-react';
import 'swagger-ui-react/swagger-ui.css';

export const Dashboard: React.FC = () => {
  const { jobId } = useParams();
  const [jobData, setJobData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJobData = async () => {
      try {
        const response = await apiClient.get(`/docs/jobs/${jobId}`);
        if (response.data.status === 'COMPLETED' && response.data.result) {
          setJobData(response.data);
        } else if (response.data.status === 'FAILED') {
          setError(response.data.error_message || 'Job failed during processing.');
        } else {
          setError('Job is still pending or in an invalid state.');
        }
      } catch (err: any) {
        console.error(err);
        setError('Failed to load job data.');
      } finally {
        setLoading(false);
      }
    };

    if (jobId) {
      fetchJobData();
    }
  }, [jobId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center" style={{ marginTop: '5rem' }}>
        <div className="spinner"></div>
        <p className="mt-4" style={{ color: 'var(--text-secondary)' }}>Loading analysis results...</p>
      </div>
    );
  }

  if (error || !jobData) {
    return (
      <div className="flex flex-col items-center justify-center text-center" style={{ marginTop: '5rem' }}>
        <h2 className="text-3xl mb-4" style={{ color: '#fca5a5' }}>Error Loading Dashboard</h2>
        <p className="max-w-xs">{error}</p>
        <Link to="/" className="mt-4 px-4 py-2 btn-primary rounded-lg font-medium" style={{ textDecoration: 'none' }}>
          Back to Home
        </Link>
      </div>
    );
  }

  const { openapi_spec } = jobData.result;

  return (
    <div style={{ width: '100%', padding: '2rem 0' }}>
      <div className="flex items-center justify-between" style={{ marginBottom: '2rem' }}>
        <div>
          <h1 className="text-3xl" style={{ fontWeight: 'bold' }}>API Documentation</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Generated from: {jobData.filename}</p>
        </div>
        <Link 
          to="/" 
          style={{ padding: '0.5rem 1rem', background: 'rgba(255,255,255,0.1)', borderRadius: '0.5rem', textDecoration: 'none', color: 'inherit' }}
        >
          &larr; Analyze Another File
        </Link>
      </div>

      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        {/* Swagger UI expects a light theme context to display its text clearly */}
        <div style={{ backgroundColor: '#ffffff', padding: '1rem' }}>
          <SwaggerUI spec={openapi_spec} />
        </div>
      </div>
    </div>
  );
};
