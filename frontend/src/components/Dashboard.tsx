import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiClient } from '../api/client';
import SwaggerUI from 'swagger-ui-react';
import 'swagger-ui-react/swagger-ui.css';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

type Tab = 'docs' | 'tests' | 'security';

export const Dashboard: React.FC = () => {
  const { jobId } = useParams();
  const [jobData, setJobData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>('docs');

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

  const { openapi_spec, test_suite, security_insights } = jobData.result;

  return (
    <div style={{ width: '100%', padding: '2rem 0' }}>
      <div className="flex items-center justify-between" style={{ marginBottom: '2rem' }}>
        <div>
          <h1 className="text-3xl" style={{ fontWeight: 'bold' }}>Analysis Dashboard</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Generated from: {jobData.filename}</p>
        </div>
        <Link 
          to="/" 
          style={{ padding: '0.5rem 1rem', background: 'rgba(255,255,255,0.1)', borderRadius: '0.5rem', textDecoration: 'none', color: 'inherit' }}
        >
          &larr; Analyze Another File
        </Link>
      </div>

      {/* Tabs */}
      <div className="flex" style={{ gap: '1rem', marginBottom: '1.5rem' }}>
        <button 
          onClick={() => setActiveTab('docs')} 
          className={`tab-btn ${activeTab === 'docs' ? 'active' : ''}`}
        >
          API Docs
        </button>
        <button 
          onClick={() => setActiveTab('tests')} 
          className={`tab-btn ${activeTab === 'tests' ? 'active' : ''}`}
        >
          Test Scripts
        </button>
        <button 
          onClick={() => setActiveTab('security')} 
          className={`tab-btn ${activeTab === 'security' ? 'active' : ''}`}
        >
          Security Insights
        </button>
      </div>

      <div className="glass-panel" style={{ overflow: 'hidden', minHeight: '60vh' }}>
        
        {activeTab === 'docs' && (
          <div style={{ backgroundColor: '#ffffff', padding: '1rem' }}>
            <SwaggerUI spec={openapi_spec} />
          </div>
        )}

        {activeTab === 'tests' && (
          <div style={{ padding: '1.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
              Generated Test Suite ({test_suite.framework})
            </h2>
            <SyntaxHighlighter 
              language="python" 
              style={vscDarkPlus} 
              customStyle={{ borderRadius: '8px', margin: 0, padding: '1rem', border: '1px solid var(--border-color)' }}
            >
              {test_suite.code}
            </SyntaxHighlighter>
          </div>
        )}

        {activeTab === 'security' && (
          <div style={{ padding: '1.5rem' }}>
             <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>
               DevSecOps Analysis
             </h2>
             {!security_insights || security_insights.length === 0 ? (
               <div style={{ padding: '1rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', borderLeft: '4px solid #10b981', borderRadius: '4px' }}>
                 <p style={{ color: '#6ee7b7' }}>✅ Excellent! No security flaws detected in the static analysis.</p>
               </div>
             ) : (
               <div className="flex flex-col gap-4">
                 {security_insights.map((insight: any, idx: number) => (
                   <div key={idx} style={{ padding: '1rem', borderLeft: '4px solid #ef4444', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: '4px' }}>
                      <strong style={{ display: 'block', marginBottom: '0.5rem', color: '#fca5a5' }}>
                        Route: {insight.route}
                      </strong>
                      <p style={{ color: '#f8fafc' }}>{insight.issue}</p>
                   </div>
                 ))}
               </div>
             )}
          </div>
        )}

      </div>
    </div>
  );
};
