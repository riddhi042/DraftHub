import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { register } from '../api/auth'
import './Auth.css'

export default function Register() {
  const [form, setForm] = useState({ email: '', username: '', password: '', full_name: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(form)
      navigate('/login')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-box fade-in">
        <div className="auth-logo">
          <div className="auth-logo-mark">D</div>
          <span className="auth-logo-text">DraftHub</span>
        </div>
        <h1 className="auth-title">Create account</h1>
        <p className="auth-sub">Set up your studio profile</p>
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label>Full Name</label>
            <input name="full_name" placeholder="Jane Doe" value={form.full_name} onChange={handleChange} />
          </div>
          <div className="field">
            <label>Email</label>
            <input name="email" type="email" placeholder="you@studio.com" value={form.email} onChange={handleChange} required />
          </div>
          <div className="field">
            <label>Username</label>
            <input name="username" placeholder="janedoe" value={form.username} onChange={handleChange} required />
          </div>
          <div className="field">
            <label>Password</label>
            <input name="password" type="password" placeholder="••••••••" value={form.password} onChange={handleChange} required />
          </div>
          {error && <div className="error-msg">{error}</div>}
          <button className="btn btn-primary auth-btn" type="submit" disabled={loading}>
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>
        <p className="auth-divider">Already have an account? <Link to="/login">Sign in</Link></p>
      </div>
    </div>
  )
}