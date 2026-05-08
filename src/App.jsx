import React, { useState, useRef } from 'react';
import { Upload, Link as LinkIcon, AlertCircle } from 'lucide-react';
import './App.css';
import ComparisonViewer from './components/ComparisonViewer';
import ResultsPanel from './components/ResultsPanel';

function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const processImage = async (formData) => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('/api/process', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setResult(data);
      } else {
        throw new Error('Processing failed');
      }
    } catch (err) {
      console.error(err);
      setError(err.message || 'An error occurred while processing the image.');
    } finally {
      setLoading(false);
    }
  };

  const handleUrlSubmit = (e) => {
    e.preventDefault();
    if (!url) return;
    const formData = new FormData();
    formData.append('url', url);
    processImage(formData);
  };

  const handleFileUpload = (file) => {
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      setError('Please upload an image file.');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    processImage(formData);
  };

  const onDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1 className="gradient-text">AuraVision</h1>
        <p>Ultimate Adaptive Low-Light Moderation</p>
      </header>

      {!result && !loading && (
        <section className="input-section glass-panel">
          <div 
            className={`upload-area ${dragActive ? 'drag-active' : ''}`}
            onDragEnter={onDrag}
            onDragLeave={onDrag}
            onDragOver={onDrag}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={48} className="upload-icon" />
            <h3>Drag & Drop to Upload</h3>
            <p className="text-secondary">or click to browse local files</p>
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              accept="image/*"
              onChange={(e) => handleFileUpload(e.target.files[0])}
            />
          </div>

          <div className="divider">OR</div>

          <form onSubmit={handleUrlSubmit} className="url-input-group">
            <input 
              type="url" 
              className="url-input" 
              placeholder="Paste image URL here..." 
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
            <button type="submit" className="btn-primary" disabled={!url}>
              Process URL
            </button>
          </form>

          {error && (
            <div className="error-message">
              <AlertCircle size={20} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
              {error}
            </div>
          )}
        </section>
      )}

      {loading && (
        <div className="loading-container glass-panel">
          <div className="spinner"></div>
          <h3 className="gradient-text">Enhancing Image & Running Inference...</h3>
          <p style={{ color: 'var(--text-secondary)' }}>This might take a few seconds.</p>
        </div>
      )}

      {result && !loading && (
        <section className="results-section">
          <button 
            className="btn-primary" 
            style={{ width: 'fit-content' }}
            onClick={() => { setResult(null); setUrl(''); }}
          >
            ← Process Another Image
          </button>
          
          <div className="results-grid">
            <ComparisonViewer 
              original={result.original_image_b64} 
              enhanced={result.enhanced_image_b64} 
            />
            <ResultsPanel result={result} />
          </div>
        </section>
      )}
    </div>
  );
}

export default App;
