import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const codeApi = {
  upload: (file: File, language: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('language', language)
    return apiClient.post('/api/code/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  analyze: (fileId: number) => {
    return apiClient.post(`/api/code/analyze/${fileId}`)
  },

  batchAnalyze: (fileIds: number[]) => {
    return apiClient.post('/api/code/batch-analyze', { file_ids: fileIds })
  },

  getLanguages: () => {
    return apiClient.get('/api/code/languages')
  }
}

export const analysisApi = {
  start: (fileId: number) => {
    return apiClient.post('/api/analysis/start', { file_id: fileId })
  },

  getStatus: (taskId: string) => {
    return apiClient.get(`/api/analysis/status/${taskId}`)
  },

  batchStart: (fileIds: number[]) => {
    return apiClient.post('/api/analysis/batch', { file_ids: fileIds })
  },

  getResults: (fileId: number) => {
    return apiClient.get(`/api/analysis/results/${fileId}`)
  },

  getStatistics: () => {
    return apiClient.get('/api/analysis/statistics')
  },

  getHistory: () => {
    return apiClient.get('/api/analysis/history')
  }
}

export const collaborationApi = {
  getSessions: () => {
    return apiClient.get('/api/collaboration/sessions')
  },

  createSession: (name: string, owner: string) => {
    return apiClient.post('/api/collaboration/sessions', { name, owner })
  },

  getSession: (sessionId: number) => {
    return apiClient.get(`/api/collaboration/sessions/${sessionId}`)
  },

  joinSession: (sessionId: number, user: string) => {
    return apiClient.post(`/api/collaboration/sessions/${sessionId}/join`, { user })
  },

  addComment: (sessionId: number, author: string, content: string, lineNumber?: number) => {
    return apiClient.post(`/api/collaboration/sessions/${sessionId}/comments`, {
      author,
      content,
      line_number: lineNumber
    })
  },

  deleteComment: (sessionId: number, commentId: number) => {
    return apiClient.delete(`/api/collaboration/sessions/${sessionId}/comments/${commentId}`)
  }
}

export const analyzeApi = {
  analyze: (code: string, language: string) => {
    return apiClient.post('/api/analyze', { code, language })
  },

  batchAnalyze: (codes: string[], language: string) => {
    return apiClient.post('/api/analyze/batch', { codes, language })
  },

  getMetrics: (code: string, language: string) => {
    return apiClient.post('/api/analyze/metrics', { code, language })
  }
}

export default apiClient
