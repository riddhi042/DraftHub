import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getProjects, createProject, deleteProject } from '../api/projects'
import Sidebar from '../components/Sidebar'
import Topbar from '../components/Topbar'
import './Dashboard.css'

export default function Dashboard() {
  const [projects, setProjects] = useState([])
  const [activity, setActivity] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ name: '', description: '' })
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const user = { full_name: 'Architect', username: 'architect' }

  const fetchProjects = async () => {
    try {
      const res = await getProjects()
      setProjects(res.data)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchProjects() }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    setCreating(true)
    setError('')
    try {
      await createProject(form)
      setShowModal(false)
      setForm({ name: '', description: '' })
      fetchProjects()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create project.')
    } finally { setCreating(false) }
  }

  const handleDelete = async (e, id) => {
    e.stopPropagation()
    if (!confirm('Delete this project?')) return
    try {
      await deleteProject(id)
      setProjects(projects.filter(p => p.id !== id))
    } catch (e) { console.error(e) }
  }

  const fmt = d => new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })

  const STATUS_LABELS = { false: 'DRAFTING', true: 'ARCHIVED' }
  const STATUS_CLASSES = { false: 'badge-blue', true: 'badge-gray' }

  return (
    <div className="app-layout">
      <Sidebar user={user} />
      <div className="app-main">
        <Topbar />
        <div className="dashboard-content">
          <div className="dashboard-left">
            <div className="section-header">
              <div>
                <h2 className="section-title">Studio Dashboard</h2>
                <p className="section-sub">
                  {projects.length > 0
                    ? `${projects.length} active project${projects.length !== 1 ? 's' : ''} in your studio`
                    : 'No projects yet — create your first one'}
                </p>
              </div>
            </div>

            {/* Recent Projects */}
            <div className="subsection">
              <div className="subsection-header">
                <span className="subsection-label">RECENT PROJECTS</span>
                <button className="view-all" onClick={() => {}}>View all</button>
              </div>

              {loading ? (
                <div className="loading-text">Loading projects...</div>
              ) : projects.length === 0 ? (
                <div className="empty-state">
                  <p>No projects yet.</p>
                  <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ New Project</button>
                </div>
              ) : (
                <div className="projects-grid">
                  {/* Featured project */}
                  {projects[0] && (
                    <div className="project-featured fade-in" onClick={() => navigate(`/projects/${projects[0].id}`)}>
                      <div className="project-featured-bg" />
                      <div className="project-featured-content">
                        <span className={`badge ${STATUS_CLASSES[projects[0].is_archived]} featured-badge`}>
                          {projects[0].is_archived ? 'ARCHIVED' : 'ACTIVE'}
                        </span>
                        <div className="featured-name">{projects[0].name}</div>
                        <div className="featured-desc">{projects[0].description || 'No description'}</div>
                        <div className="featured-meta">{fmt(projects[0].created_at)}</div>
                      </div>
                      <button className="project-delete" onClick={e => handleDelete(e, projects[0].id)}>✕</button>
                    </div>
                  )}
                  {/* Other projects */}
                  <div className="projects-list">
                    {projects.slice(1).map((p, i) => (
                      <div key={p.id} className="project-row fade-in"
                        style={{ animationDelay: `${i * 0.04}s` }}
                        onClick={() => navigate(`/projects/${p.id}`)}>
                        <div className="project-row-thumb" />
                        <div className="project-row-info">
                          <div className="project-row-name">{p.name}</div>
                          <div className="project-row-desc">{p.description || '—'}</div>
                          <span className={`badge ${STATUS_CLASSES[p.is_archived]}`}>
                            {STATUS_LABELS[p.is_archived]}
                          </span>
                        </div>
                        <div className="project-row-actions">
                          <button className="row-link" onClick={e => { e.stopPropagation(); navigate(`/projects/${p.id}`) }}>→</button>
                          <button className="project-delete small" onClick={e => handleDelete(e, p.id)}>✕</button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Approval Queue placeholder */}
            <div className="subsection">
              <div className="subsection-header">
                <span className="subsection-label">APPROVAL QUEUE</span>
                <span className="badge badge-red">0 URGENT</span>
              </div>
              <div className="queue-empty">No pending approvals.</div>
            </div>
          </div>

          {/* Right panel — Activity Timeline */}
          <div className="dashboard-right">
            <div className="panel">
              <div className="panel-header">ACTIVITY TIMELINE</div>
              {projects.length === 0 ? (
                <div className="panel-empty">Activity will appear here once you start working on projects.</div>
              ) : (
                <div className="timeline">
                  {projects.slice(0, 5).map((p, i) => (
                    <div key={p.id} className="timeline-item fade-in" style={{ animationDelay: `${i * 0.05}s` }}>
                      <div className="timeline-dot" />
                      <div className="timeline-content">
                        <div className="timeline-title">{p.name}</div>
                        <div className="timeline-meta">{fmt(p.created_at)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="panel" style={{ marginTop: '16px' }}>
              <div className="panel-header">SYSTEM METRICS</div>
              <div className="metric-row">
                <span className="metric-label">Vault Storage</span>
                <div className="metric-bar"><div className="metric-fill" style={{ width: '74%' }} /></div>
                <span className="metric-val">74%</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Processing Load</span>
                <div className="metric-bar"><div className="metric-fill blue" style={{ width: '12%' }} /></div>
                <span className="metric-val">12%</span>
              </div>
              <div className="metric-status">
                <span className="status-dot active" /> Cloud Sync Active · v24.1.0 stable
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Create Project Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal fade-in" onClick={e => e.stopPropagation()}>
            <h2 className="modal-title">New Project</h2>
            <form onSubmit={handleCreate}>
              <div className="field">
                <label>Project Name</label>
                <input placeholder="e.g. Metropolitan Library Annex" value={form.name}
                  onChange={e => setForm({ ...form, name: e.target.value })} required autoFocus />
              </div>
              <div className="field">
                <label>Description</label>
                <textarea placeholder="Brief project description" value={form.description}
                  onChange={e => setForm({ ...form, description: e.target.value })} rows={3} />
              </div>
              {error && <div className="error-msg">{error}</div>}
              <div className="modal-actions">
                <button type="button" className="btn btn-ghost" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={creating}>
                  {creating ? 'Creating...' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
