import api from './client'

export const register = (data) => api.post('/auth/register', data)

export const login = async (email, password) => {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  const res = await api.post('/auth/login', form)
  return res.data
}