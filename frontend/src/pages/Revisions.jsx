import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getProject } from '../api/projects'
import { getBlueprints, getRevisions } from '../api/blueprints'
import Sidebar from '../components/Sidebar'
import Topbar from '../components/Topbar'
import './Revisions.css'

export default function Revisions() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [blueprints, setBlueprints] = useState([])
  const [revisions, setRevisions] = useState([])
  const [selectedBp, setSelectedBp] = useState(null)
  const [selected, setSelected] = useState([])
  const [loading, setLoading] = useState(true)
  const user = { full_name: 'Lead Architect', username: 'architect' }

  useEffect(() => {
    const load = async () => {
      try {
        const [projRes, bpRes] = await Promise.all([getProject(id), getBlueprints(id)])
        setProject(projRes.data)
        setBlueprints(bpRes.data)
        if (bpRes.data.length > 0) {
          setSelectedBp(bpRes.data[0])
          const revRes = await getRevisions(bpRes.data[0].id)
          setRevisions(revRes.data)
        }
      } catch (e) { console.error(e) }
      finally { setLoading(false) }
    }
    load()
  }, [id])

  const loadRevisions = async (bp) => {
    setSelectedBp(bp)
    const res = await getRevisions(bp.id)
    setRevisions(res.data)
  }

  const toggleSelect = (revId) => {
    setSelected(s => s.includes(revId) ? s.filter(i => i !== revId) : [...s, revId])
  }

  const fmt = d => new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  const fmtTime = d => new Date(d).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  const shortId = id => id?.slice(0, 8) || '—'

  const groupByDate = (revs) => {
    const groups = {}
    revs.forEach(r => {
      const d = new Date(r.created_at)
      const today = new Date()
      const yesterday = new Date(today)
      yesterday.setDate(yesterday.getDate() - 1)
      let label
      if (d.toDateString() === today.toDateString()) label = `Today — ${fmt(r.created_at)}`
      else if (d.toDateString() === yesterday.toDateString()) label = `Yesterday — ${fmt(r.created_at)}`
      else label = fmt(r.created_at)
      if (!groups[label]) groups[label] = []
      groups[label].push(r)
    })
    return groups
  }

  if (loading) return <div className="page-load">Loading...</div>

  const grouped = groupByDate([...revisions].reverse())

  return (
    <div className="app-layout">
      <Sidebar user={user} />
      <div className="app-main">
        <Topbar placeholder="Search revisions..." />
        <div className="revisions-page">
          <div className="rev-header">
            <div className="rev-breadcrumb">
              <span className="badge badge-blue">ACTIVE PROJECT</span>
              <span className="rev-proj-id">{project?.name?.slice(0,12).toUpperCase() || 'PRJ-2024'}</span>
            </div>
            <div className="rev-title-row">
              <h1 className="rev-title">Revision History</h1>
              {selected.length > 0 && (
                <button className="btn btn-outline">
                  ⇄ Compare Selected ({selected.length})
                </button>
              )}
            </div>
            <p className="rev-sub">
              {project?.name} {project?.description ? `• ${project.description}` : ''}
            </p>
          </div>

          {blueprints.length > 1 && (
            <div className="bp-tabs">
              {blueprints.map(bp => (
                <button key={bp.id}
                  className={`bp-tab ${selectedBp?.id === bp.id ? 'active' : ''}`}
                  onClick={() => loadRevisions(bp)}>
                  {bp.name}
                </button>
              ))}
            </div>
          )}

          {revisions.length === 0 ? (
            <div className="rev-empty">
              <p>No revisions yet for this blueprint.</p>
              <button className="btn btn-primary" onClick={() => navigate(`/projects/${id}`)}>
                Upload first revision →
              </button>
            </div>
          ) : (
            <div className="rev-timeline">
              {Object.entries(grouped).map(([date, revs]) => (
                <div key={date} className="rev-group">
                  <div className="rev-date-label">
                    <span className="rev-date-icon">◷</span>
                    {date}
                  </div>
                  <div className="rev-cards">
                    {revs.map((r, i) => (
                      <div key={r.id}
                        className={`rev-card fade-in ${selected.includes(r.id) ? 'selected' : ''} ${i === 0 && revs === Object.values(grouped)[0] ? 'latest' : ''}`}
                        style={{ animationDelay: `${i * 0.04}s` }}>
                        <div className="rev-card-left">
                          <div className="rev-version">v{r.version_number}</div>
                        </div>
                        <div className="rev-card-body">
                          <div className="rev-card-meta">
                            <span className="rev-ref">REF: {shortId(r.id)}</span>
                            <span className="rev-dot">•</span>
                            <span className="rev-time">{fmtTime(r.created_at)}</span>
                            {i === 0 && <span className="badge badge-blue rev-latest">LATEST</span>}
                          </div>
                          <div className="rev-card-title">{r.original_filename}</div>
                          <div className="rev-card-desc">
                            {r.notes || 'No revision notes provided.'}
                          </div>
                          <div className="rev-card-author">
                            <div className="author-avatar">
                              {(r.uploaded_by || 'U').charAt(0).toUpperCase()}
                            </div>
                            <span className="author-name">{r.uploaded_by || 'Unknown'}</span>
                            {r.mime_type && (
                              <>
                                <span className="rev-dot">/</span>
                                <span className="author-layer">{r.mime_type.split('/')[1]?.toUpperCase() || 'FILE'}</span>
                              </>
                            )}
                          </div>
                        </div>
                        <div className="rev-card-right">
                          <input type="checkbox" className="rev-checkbox"
                            checked={selected.includes(r.id)}
                            onChange={() => toggleSelect(r.id)} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
