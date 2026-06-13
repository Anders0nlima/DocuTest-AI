import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { apiClient } from '../api/client';

export const Sidebar: React.FC = () => {
  const [history, setHistory] = useState<any[]>([]);
  const location = useLocation();

  // We refetch history whenever the route changes so new uploads appear immediately
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await apiClient.get('/docs/jobs');
        setHistory(response.data);
      } catch (err) {
        console.error('Failed to fetch history', err);
      }
    };
    fetchHistory();
  }, [location.pathname]);

  return (
    <div className="sidebar glass-panel" style={{ width: '280px', height: '100vh', position: 'fixed', left: 0, top: 0, overflowY: 'auto', padding: '1.5rem', borderRadius: 0, borderRight: '1px solid var(--border-color)', zIndex: 10 }}>
      <h2 className="text-xl mb-6" style={{ color: '#a5b4fc', fontWeight: 'bold' }}>Generation History</h2>
      
      <div className="flex flex-col gap-3">
        {history.length === 0 ? (
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>No documents generated yet.</p>
        ) : (
          history.map(job => (
            <Link 
              to={`/dashboard/${job.id}`} 
              key={job.id}
              style={{ padding: '0.75rem', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '8px', textDecoration: 'none', color: 'inherit', transition: 'background 0.2s' }}
              className="hover:bg-slate-800"
            >
              <div style={{ fontWeight: 500, fontSize: '0.95rem' }}>{job.filename}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.25rem', display: 'flex', justifyContent: 'space-between' }}>
                <span>{new Date(job.created_at).toLocaleDateString()}</span>
                <span style={{ 
                  color: job.status === 'COMPLETED' ? '#6ee7b7' : job.status === 'FAILED' ? '#fca5a5' : '#a5b4fc' 
                }}>
                  {job.status}
                </span>
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
};
