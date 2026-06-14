import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Blueprints from './pages/Blueprints'
import Revisions from './pages/Revisions'
import Collaboration from './pages/Collaboration'

function PrivateRoute({ children }) {
  const token = localStorage.getItem('token')
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/blueprints" element={<PrivateRoute><Blueprints /></PrivateRoute>} />
        <Route path="/revisions/:id" element={<PrivateRoute><Revisions /></PrivateRoute>} />
        <Route path="/revisions" element={<PrivateRoute><Revisions /></PrivateRoute>} />
        <Route path="/collaboration" element={<PrivateRoute><Collaboration /></PrivateRoute>} />
        <Route path="/projects/:id" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  )
}