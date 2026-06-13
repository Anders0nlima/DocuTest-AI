import { Routes, Route } from "react-router-dom";
import { UploadZone } from "./components/UploadZone";
import { Dashboard } from "./components/Dashboard";
import { Sidebar } from "./components/Sidebar";
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

function App() {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard/:jobId" element={<Dashboard />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
