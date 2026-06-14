import api from './client'

export const getBlueprints = (projectId) => api.get(`/projects/${projectId}/blueprints`)

export const createBlueprint = (projectId, data) => api.post(`/projects/${projectId}/blueprints`, data)

export const getRevisions = (blueprintId) => api.get(`/blueprints/${blueprintId}/revisions`)

export const uploadRevision = (blueprintId, file, notes) => {
  const form = new FormData()
  form.append('file', file)
  if (notes) form.append('notes', notes)
  return api.post(`/blueprints/${blueprintId}/revisions`, form)
}

export const deleteBlueprint = (blueprintId) => api.delete(`/blueprints/${blueprintId}`)