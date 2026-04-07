import { useState, useRef } from 'react'
import './index.css'

function App() {
  const [inputText, setInputText] = useState('')
  const [logs, setLogs] = useState([{ type: 'info', text: 'ANTIGRAVITY CORE v1.0.0 INITIALIZED.' }, { type: 'info', text: 'Awaiting payload...' }])
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef(null)

  const addLog = (text, type = 'info') => {
    setLogs(prev => [...prev, { text, type }])
  }

  const handleTextSubmit = async () => {
    if (!inputText) return
    setLoading(true)
    addLog(`> POST /api/process_text payload="${inputText}"`, 'cmd')
    
    try {
      const response = await fetch('http://localhost:8000/api/process_text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: inputText })
      })
      
      const data = await response.json()
      addLog(`[HTTP 200] ${JSON.stringify(data, null, 2)}`, 'success')
      setInputText('')
    } catch (err) {
      addLog(`[ERROR] Connection refused: ${err.message}`, 'err')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    setLoading(true)
    addLog(`> POST /api/process_file filename="${file.name}"`, 'cmd')
    
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      const response = await fetch('http://localhost:8000/api/process_file', {
        method: 'POST',
        body: formData
      })
      const data = await response.json()
      addLog(`[HTTP 200] ${JSON.stringify(data, null, 2)}`, 'success')
    } catch (err) {
      addLog(`[ERROR] Processing failed: ${err.message}`, 'err')
    } finally {
      setLoading(false)
      if(fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  return (
    <>
      <h1>Multimodal Sandbox</h1>
      <div className="subtitle">Antigravity Core Testing Environment</div>
      
      <div className="grid">
        <div className="glass-panel">
          <div className="form-group">
            <label>Text & URL Extraction</label>
            <input 
              type="text" 
              placeholder="Enter context URL or raw text here..." 
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleTextSubmit()}
            />
          </div>
          
          <button onClick={handleTextSubmit} disabled={loading || !inputText}>
            {loading ? 'Processing...' : 'Engage Text Parser'}
          </button>
          
          <div style={{ marginTop: '3rem' }}>
            <label style={{ display: 'block', marginBottom: '0.75rem' }}>Asset Ingestion (PDF/XLS/Media)</label>
            <div className="dropzone" onClick={() => fileInputRef.current.click()}>
               <div style={{ fontSize: '2rem', marginBottom: '10px' }}>📁</div>
               <div>Click or Drop File Here</div>
               <div style={{ fontSize: '0.8rem', color: '#9ca3af' }}>JPG, MP3, PDF, XLS supported</div>
            </div>
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }}
              onChange={handleFileUpload} 
            />
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '0', display: 'flex', flexDirection: 'column' }}>
          <div className="terminal-container">
            <div className="terminal-header">
              <div className="dot r"></div><div className="dot y"></div><div className="dot g"></div>
              <span style={{ fontSize: '0.8rem', marginLeft: '10px', color: '#9ca3af', fontFamily: 'monospace' }}>terminal ~ api-response</span>
            </div>
            <div className="terminal">
              {logs.map((log, i) => (
                <div key={i} className={`console-line ${log.type}`}>
                  {log.text}
                </div>
              ))}
              {loading && <div className="console-line pulse">_</div>}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default App
