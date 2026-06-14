import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getProjects } from '../api/projects'
import { getBlueprints, createBlueprint, uploadRevision } from '../api/blueprints'
import Sidebar from '../components/Sidebar'
import Topbar from '../components/Topbar'
import './Blueprints.css'

export default function Blueprints() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [selectedProject, setSelectedProject] = useState(null)
  const [blueprints, setBlueprints] = useState([])
  const [selectedBp, setSelectedBp] = useState(null)
  const [uploadFile, setUploadFile] = useState(null)
  const [notes, setNotes] = useState('')
  const [uploading, setUploading] = useState(false)
  const [showUpload, setShowUpload] = useState(false)
  const [zoom, setZoom] = useState(100)
  const user = { full_name: 'John Architect', username: 'jarchitect' }

  const ANNOTATIONS = [
    { id: '#ANN-012', text: 'Verify bearing wall thickness in Section B-B. Seems insufficient for load-bearing requirements.', tags: ['STRUCTURAL', 'URGENT'], time: '2m ago', color: 'red' },
    { id: '#ANN-011', text: 'Electrical conduit pathing adjusted to avoid HVAC main trunk.', tags: ['MEP'], time: '2m ago', color: 'blue' },
    { id: '#ANN-010', text: 'Staircase tread width confirmed at 300mm to comply with local codes.', tags: ['COMPLIANCE'], time: '4m ago', color: 'green' },
  ]

  useEffect(() => {
    getProjects().then(res => {
      setProjects(res.data)
      if (res.data.length > 0) {
        setSelectedProject(res.data[0])
        return getBlueprints(res.data[0].id)
      }
    }).then(res => {
      if (res) {
        setBlueprints(res.data)
        if (res.data.length > 0) setSelectedBp(res.data[0])
      }
    }).catch(console.error)
  }, [])

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!uploadFile || !selectedBp) return
    setUploading(true)
    try {
      await uploadRevision(selectedBp.id, uploadFile, notes)
      setShowUpload(false)
      setUploadFile(null)
      setNotes('')
      const res = await getBlueprints(selectedProject.id)
      setBlueprints(res.data)
      const updated = res.data.find(b => b.id === selectedBp.id)
      if (updated) setSelectedBp(updated)
    } catch (e) { console.error(e) }
    finally { setUploading(false) }
  }

  const fmt = d => new Date(d).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })

  return (
    <div className="app-layout">
      <Sidebar user={user} />
      <div className="app-main">
        <Topbar placeholder="Search blueprints..." />
        <div className="blueprints-layout">
          {/* Canvas area */}
          <div className="canvas-area">
            <div className="canvas-toolbar">
              <button className="tool-btn active" title="Select">↖</button>
              <button className="tool-btn" title="Pan">✋</button>
              <button className="tool-btn" title="Zoom out" onClick={() => setZoom(z => Math.max(25, z - 25))}>−</button>
              <span className="zoom-level">{zoom}%</span>
              <button className="tool-btn" title="Zoom in" onClick={() => setZoom(z => Math.min(200, z + 25))}>+</button>
              <button className="tool-btn" title="Measure">⊢</button>
              <button className="tool-btn" title="Comment">💬</button>
              <button className="tool-btn" title="Layers">⊞</button>
            </div>
            <div className="canvas-body">
              {selectedBp ? (
                <div className="canvas-placeholder">
                  <div className="blueprint-grid" />
                  <div className="canvas-label">
                    {selectedBp.name}
                    <span className="canvas-version">v{selectedBp.current_version}</span>
                  </div>
                  <div className="canvas-hint">Blueprint canvas — file preview coming soon</div>
                  <button className="btn btn-primary upload-trigger" onClick={() => setShowUpload(true)}>
                    ↑ Upload Revision
                  </button>
                </div>
              ) : (
                <div className="canvas-empty">
                  <p>Select a blueprint to view</p>
                </div>
              )}
            </div>
            <div className="canvas-statusbar">
              <span>X: 142.02</span>
              <span>Y: 893.44</span>
              <span className="status-sep">|</span>
              <span>MM (Metric)</span>
              <span className="status-sep">|</span>
              <span className="drafting-mode">Drafting Mode: ACTIVE</span>
            </div>
          </div>

          {/* Right panel */}
          <aside className="bp-right-panel">
            <div className="detail-section">
              <div className="detail-section-title">TECHNICAL DETAILS</div>
              {selectedProject && selectedBp ? (
                <table className="detail-table">
                  <tbody>
                    <tr><td>PROJECT ID</td><td className="mono">{selectedProject.name.slice(0,8).toUpperCase()}-X{selectedProject.id}</td></tr>
                    <tr><td>SCALE</td><td className="mono">1:50 @ A1</td></tr>
                    <tr><td>LAST REVISION</td><td className="mono">{selectedBp.updated_at ? fmt(selectedBp.updated_at) : '—'}</td></tr>
                    <tr><td>STATUS</td><td><span className="status-review">● REVIEW</span></td></tr>
                  </tbody>
                </table>
              ) : <div className="detail-empty">No blueprint selected</div>}
            </div>

            {selectedBp && (
              <div className="detail-section">
                <div className="detail-section-title">ARCHITECT IN CHARGE</div>
                <div className="architect-row">
                  <div className="arch-avatar">A</div>
                  <div>
                    <div className="arch-name">Lead Architect</div>
                    <div className="arch-role">Structural Engineer</div>
                  </div>
                </div>
              </div>
            )}

            <div className="detail-section" style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
              <div className="detail-section-title" style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>ANNOTATIONS</span>
                <span className="badge badge-blue">04</span>
              </div>
              <div className="annotations-list">
                {ANNOTATIONS.map(a => (
                  <div key={a.id} className={`annotation-item ann-${a.color}`}>
                    <div className="ann-meta">
                      <span className="ann-id">{a.id}</span>
                      <span className="ann-time">{a.time}</span>
                    </div>
                    <div className="ann-text">{a.text}</div>
                    <div className="ann-tags">
                      {a.tags.map(t => (
                        <span key={t} className={`ann-tag ${t === 'URGENT' ? 'tag-urgent' : 'tag-default'}`}>{t}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              <div className="ann-input-wrap">
                <input type="text" placeholder="Add technical note..." className="ann-input" />
                <button className="send-btn">→</button>
              </div>
            </div>
          </aside>
        </div>
      </div>

      {/* Upload modal */}
      {showUpload && (
        <div className="modal-overlay" onClick={() => setShowUpload(false)}>
          <div className="modal fade-in" onClick={e => e.stopPropagation()}>
            <h2 className="modal-title">Upload Revision</h2>
            <p style={{fontSize:'12px', color:'var(--text2)', marginBottom:'16px'}}>
              {selectedBp?.name} · Currently v{selectedBp?.current_version}
            </p>
            <form onSubmit={handleUpload}>
              <div className="field">
                <label>File</label>
                <div className="upload-zone" onClick={() => document.getElementById('bpFile').click()}>
                  {uploadFile ? <span className="upload-name">📄 {uploadFile.name}</span>
                    : <span className="upload-hint">Click to choose file</span>}
                  <input id="bpFile" type="file" hidden onChange={e => setUploadFile(e.target.files[0])} />
                </div>
              </div>
              <div className="field">
                <label>Revision Notes</label>
                <textarea placeholder="Describe what changed..." value={notes}
                  onChange={e => setNotes(e.target.value)} rows={3} />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-ghost" onClick={() => setShowUpload(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={!uploadFile || uploading}>
                  {uploading ? 'Uploading...' : 'Upload Revision'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
