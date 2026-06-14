import './Topbar.css'

export default function Topbar({ placeholder = 'Search projects, assets, or revisions...' }) {
  return (
    <header className="topbar">
      <div className="topbar-search">
        <span className="search-icon">⌕</span>
        <input type="text" placeholder={placeholder} className="topbar-input" />
      </div>
      <nav className="topbar-nav">
        <button className="topbar-link active">Projects</button>
        <button className="topbar-link">Assets</button>
        <button className="topbar-link">Standards</button>
      </nav>
      <div className="topbar-actions">
        <button className="topbar-icon-btn">🔔</button>
        <button className="topbar-icon-btn">⇄</button>
        <button className="btn btn-ghost" style={{fontSize:'12px',padding:'5px 12px'}}>Share</button>
        <button className="btn btn-primary" style={{fontSize:'12px',padding:'5px 12px'}}>Export</button>
      </div>
    </header>
  )
}