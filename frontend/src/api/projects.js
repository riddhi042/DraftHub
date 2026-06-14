import api from './client'

export const getProjects = () => api.get('/projects/')
export const createProject = (data) => api.post('/projects/', data)
export const getProject = (id) => api.get(`/projects/${id}`)
export const updateProject = (id, data) => api.patch(`/projects/${id}`, data)
export const deleteProject = (id) => api.delete(`/projects/${id}`)
export const getActivity = (id) => api.get(`/projects/${id}/activity`)