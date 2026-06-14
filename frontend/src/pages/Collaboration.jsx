import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getProjects } from '../api/projects'
import Sidebar from '../components/Sidebar'
import Topbar from '../components/Topbar'
import './Collaboration.css'

const ROLES = { owner: 'Lead Architect', editor: 'Structural Engineer', viewer: 'BIM Coordinator' }
const STATUS = ['ONLINE', 'ONLINE', 'AWAY', 'DNC']
const STATUS_CLASS = { ONLINE: 'badge-green', AWAY: 'badge-yellow', DNC: 'badge-red' }

export default function Collaboration() {
  const [projects, setProjects] = useState([])
  const [selectedProject, setSelectedProject] = useState(null)
  const [members, setMembers] = useState([])
  const [activity, setActivity] = useState([])
  const [message, setMessage] = useState('')
  const user = { full_name: 'M. Sterling', username: 'msterling' }

  useEffect(() => {
    getProjects().then(res => {
      setProjects(res.data)
      if (res.data.length > 0) setSelectedProject(res.data[0])
    }).catch(console.error)
  }, [])

  const fmt = d => {
    const diff = Math.floor((Date.now() - new Date(d)) / 60000)
    if (diff < 60) return `${diff}m ago`
    if (diff < 1440) return `${Math.floor(diff/60)}h ago`
    return new Date(d).toLocaleDateString()
  }

  return (
    <div className="app-layout">
      <Sidebar user={user} />
      <div className="app-main">
        <Topbar placeholder="Search stakeholders..." />
        <div className="collab-layout">
          <div className="collab-main">
            <div className="collab-header">
              <h1 className="collab-title">Team Collaboration</h1>
              {selectedProject && (
                <p className="collab-sub">PROJECT: {selectedProject.name.toUpperCase()}</p>
              )}
            </div>

            {!selectedProject ? (
              <div className="collab-empty">No projects found. Create a project first.</div>
            ) : (
              <div className="members-grid">
                {[
                  { name: selectedProject.name.split(' ')[0] || 'Sarah', username: 'Lead', role: 'owner', status: 'ONLINE', contributions: ['Created project', 'Added blueprints'] },
                  { name: 'Marcus', username: 'Engineer', role: 'editor', status: 'AWAY', contributions: ['Updated revisions', 'Exported load report'] },
                  { name: 'Elena', username: 'BIM', role: 'editor', status: 'ONLINE', contributions: ['Resolved clash detection', 'Plumbing vs Electrical'] },
                  { name: 'David', username: 'MEP', role: 'viewer', status: 'DNC', contributions: ['Flagged ventilation clearance'] },
                ].map((m, i) => (
                  <div key={i} className="member-card fade-in" style={{ animationDelay: `${i * 0.06}s` }}>
                    <div className="member-card-header">
                      <div className="member-avatar-wrap">
                        <div className="member-avatar">{m.name.charAt(0)}</div>
                        <span className={`badge ${STATUS_CLASS[m.status]} member-status`}>{m.status}</span>
                      </div>
                      <div className="member-info">
                        <div className="member-name">{m.name} {m.username}</div>
                        <div className="member-role">{ROLES[m.role]}</div>
                        <div className="member-email">{m.name.toLowerCase()}.{m.username.toLowerCase()}@drafthub.com</div>
                      </div>
                    </div>
                    <div className="member-contributions">
                      <div className="contrib-label">Recent Contributions</div>
                      {m.contributions.map((c, j) => (
                        <div key={j} className="contrib-item">
                          <span className="contrib-dot">•</span>
                          <span>{c}</span>
                        </div>
                      ))}
                    </div>
                    <div className="member-actions">
                      <button className="btn btn-ghost member-btn">View Profile</button>
                      <button className="btn btn-primary member-btn">Message</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Activity sidebar */}
          <aside className="collab-sidebar">
            <div className="activity-panel">
              <div className="activity-panel-header">
                <span>Real-time Activity</span>
                <button className="refresh-btn">⇄</button>
              </div>
              <div className="activity-feed">
                <div className="activity-section-label">DISCUSSION</div>
                <div className="chat-msg">
                  <div className="chat-msg-header">
                    <div className="chat-avatar">SC</div>
                    <span className="chat-name">Sarah Chen</span>
                    <span className="chat-time">2m ago</span>
                  </div>
                  <div className="chat-bubble">
                    "Can someone check the updated MEP clearances on Floor 4? The new HVAC routing seems tight."
                  </div>
                  <div className="chat-typing">David Park is typing...</div>
                </div>
                <div className="activity-section-label" style={{ marginTop: '12px' }}>AUTOMATED BUILD</div>
                <div className="auto-build">
                  <div className="build-title">Automated Build</div>
                  <div className="build-msg">Model conflict detected in <span className="build-ref">STR-09-REV-B</span>. Overlap with electrical tray 42.</div>
                  <button className="build-link">View Clash Report</button>
                </div>
                <div className="activity-section-label" style={{ marginTop: '12px' }}>REVISION PUSH</div>
                <div className="rev-push">
                  <div className="push-author">Elena Rodriguez</div>
                  <div className="push-msg">Pushed 4 new sheets to the <strong>Permit Set</strong>. All compliance headers updated.</div>
                  <div className="push-verified">✓ Verified by Lead Arch</div>
                </div>
              </div>
              <div className="chat-input-wrap">
                <input type="text" placeholder="Send a message..." value={message}
                  onChange={e => setMessage(e.target.value)}
                  className="chat-input" />
                <button className="send-btn">→</button>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  )
}
