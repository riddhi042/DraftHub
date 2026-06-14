import { useNavigate, useLocation } from 'react-router-dom'
import './Sidebar.css'

const NAV = [
  { label: 'Dashboard', icon: '⊞', path: '/dashboard' },
  { label: 'Blueprints', icon: '◻', path: '/blueprints' },
  { label: 'Revisions', icon: '↻', path: '/revisions' },
  { label: 'Collaboration', icon: '⊙', path: '/collaboration' },
]

export default function Sidebar({ user }) {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <aside className="sidebar">
      <div className="sidebar-logo" onClick={() => navigate('/dashboard')}>
        <div className="logo-mark">D</div>
        <span className="logo-name">DraftHub</span>
      </div>
      <nav className="sidebar-nav">
        {NAV.map(item => (
          <button key={item.path}
            className={`nav-item ${location.pathname.startsWith(item.path) ? 'active' : ''}`}
            onClick={() => navigate(item.path)}>
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <button className="btn-new-project" onClick={() => navigate('/dashboard')}>
          + New Project
        </button>
        <div className="sidebar-links">
          <button className="sidebar-link">Settings</button>
          <button className="sidebar-link">Support</button>
        </div>
        <div className="sidebar-user" onClick={() => { localStorage.removeItem('token'); navigate('/login') }} title="Sign out">
          <div className="user-avatar">{(user?.full_name || user?.username || 'U').charAt(0).toUpperCase()}</div>
          <div className="user-info">
            <div className="user-name">{user?.full_name || user?.username || 'Architect'}</div>
            <div className="user-role">Studio Lead</div>
          </div>
        </div>
      </div>
    </aside>
  )
}