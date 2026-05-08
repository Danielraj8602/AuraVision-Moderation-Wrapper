import React from 'react';
import { Activity, Clock, Zap, ShieldCheck } from 'lucide-react';
import './ResultsPanel.css';

const ResultsPanel = ({ result }) => {
  const formatConf = (conf) => `${(conf * 100).toFixed(2)}%`;

  return (
    <div className="results-panel glass-panel">
      <h3 className="panel-title">Analysis Results</h3>
      
      <div className="stat-card highlight">
        <div className="stat-icon"><ShieldCheck size={24} /></div>
        <div className="stat-info">
          <span className="stat-label">Final Confidence</span>
          <span className="stat-value gradient-text">{formatConf(result.final_confidence)}</span>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon"><Clock size={20} /></div>
          <div className="stat-info">
            <span className="stat-label">Processing Time</span>
            <span className="stat-value">{result.processing_time}s</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon"><Activity size={20} /></div>
          <div className="stat-info">
            <span className="stat-label">Original Conf.</span>
            <span className="stat-value">{formatConf(result.original_confidence)}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon"><Zap size={20} /></div>
          <div className="stat-info">
            <span className="stat-label">Enhanced Conf.</span>
            <span className="stat-value">{formatConf(result.enhanced_confidence)}</span>
          </div>
        </div>
      </div>

      <div className="json-container">
        <div className="json-header">Raw API Data</div>
        <pre className="json-body">
          {JSON.stringify({
            original_response: result.original_response,
            enhanced_response: result.enhanced_response
          }, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default ResultsPanel;
