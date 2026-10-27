import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { AtmosphericBackground } from './components/AtmosphericBackground';
import { Dashboard } from './pages/Dashboard';
import { VerifyAnswer } from './pages/VerifyAnswer';
import { DocumentLibrary } from './pages/DocumentLibrary';
import { VerificationHistory } from './pages/VerificationHistory';
import { EvaluationLab } from './pages/EvaluationLab';
import { Settings } from './pages/Settings';

import { api } from './services/api';
import { 
  SystemHealth, 
  VerificationReport, 
  DocumentItem, 
  EvaluationExperiment 
} from './types';

export function App() {
  const [activeTab, setActiveTab] = useState('verify');
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [availableModels, setAvailableModels] = useState<any[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [reports, setReports] = useState<VerificationReport[]>([]);
  const [experiments, setExperiments] = useState<EvaluationExperiment[]>([]);
  
  // Selected report to inspect in VerifyAnswer view
  const [activeReport, setActiveReport] = useState<VerificationReport | null>(null);

  const fetchHealth = async () => {
    try {
      const data = await api.getHealth();
      setHealth(data);
    } catch (e) {
      console.error('Failed to fetch health status:', e);
    }
  };

  const fetchModels = async () => {
    try {
      const data = await api.getModels();
      setAvailableModels(data.models || []);
    } catch (e) {
      console.error('Failed to fetch models:', e);
    }
  };

  const fetchDocuments = async () => {
    try {
      const data = await api.getDocuments();
      setDocuments(data.documents || []);
    } catch (e) {
      console.error('Failed to fetch documents:', e);
    }
  };

  const fetchReports = async () => {
    try {
      const data = await api.getVerifications();
      setReports(data || []);
    } catch (e) {
      console.error('Failed to fetch verification reports:', e);
    }
  };

  const fetchExperiments = async () => {
    try {
      const data = await api.getEvaluations();
      setExperiments(data || []);
    } catch (e) {
      console.error('Failed to fetch evaluation experiments:', e);
    }
  };

  useEffect(() => {
    fetchHealth();
    fetchModels();
    fetchDocuments();
    fetchReports();
    fetchExperiments();

    // Poll health status periodically
    const timer = setInterval(fetchHealth, 30000);
    return () => clearInterval(timer);
  }, []);

  const handleSelectReport = (report: VerificationReport) => {
    setActiveReport(report);
    setActiveTab('verify');
  };

  return (
    <div className="min-h-screen bg-[#080910] text-[#F4F4FA] flex flex-col font-sans relative selection:bg-violet-500/30 selection:text-white">
      {/* Cinematic Atmospheric Background Layer */}
      <AtmosphericBackground />

      {/* Main App Container */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <Navbar 
          activeTab={activeTab} 
          setActiveTab={setActiveTab} 
          health={health} 
        />

        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
          {activeTab === 'dashboard' && (
            <Dashboard 
              reports={reports} 
              setActiveTab={setActiveTab} 
              onSelectReport={handleSelectReport} 
            />
          )}

          {activeTab === 'verify' && (
            <VerifyAnswer
              documents={documents}
              availableModels={availableModels}
              activeReport={activeReport}
              setActiveReport={setActiveReport}
              onRefreshHistory={fetchReports}
            />
          )}

          {activeTab === 'documents' && (
            <DocumentLibrary 
              documents={documents} 
              onRefresh={fetchDocuments} 
            />
          )}

          {activeTab === 'history' && (
            <VerificationHistory 
              reports={reports} 
              onSelectReport={handleSelectReport}
              setActiveTab={setActiveTab}
            />
          )}

          {activeTab === 'evaluation' && (
            <EvaluationLab 
              experiments={experiments} 
              onRefresh={fetchExperiments} 
            />
          )}

          {activeTab === 'settings' && (
            <Settings 
              health={health} 
              onRefreshHealth={fetchHealth} 
            />
          )}
        </main>

        <footer className="border-t border-white/[0.06] bg-[#080910]/80 backdrop-blur-md py-6 text-center text-xs text-[#94A3B8]">
          <p>TruthGuard — Explainable NLP Framework for Hallucination Detection & Automatic Evidence Correction</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
