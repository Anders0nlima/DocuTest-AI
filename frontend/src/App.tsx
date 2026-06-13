import { Routes, Route, useParams } from "react-router-dom";
import { UploadZone } from "./components/UploadZone";
import './App.css';

function Home() {
  return (
    <div className="home-container">
      <h1 className="hero-title">DocuTest AI</h1>
      <p className="hero-subtitle">
        Drop your backend source code. Let our DevSecOps AI extract the API contracts, 
        generate interactive OpenAPI specs, and write security test suites instantly.
      </p>
      
      <UploadZone />
    </div>
  );
}

// Placeholder for Step 15 & 16
function Dashboard() {
  const { jobId } = useParams();
  return (
    <div className="glass-panel" style={{ padding: '2rem', marginTop: '2rem' }}>
      <h2 style={{ color: '#a5b4fc', fontSize: '1.5rem', marginBottom: '1rem' }}>Dashboard Area</h2>
      <p style={{ color: '#94a3b8' }}>Viewing analysis results for Job ID: {jobId}</p>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/dashboard/:jobId" element={<Dashboard />} />
    </Routes>
  );
}

export default App;
