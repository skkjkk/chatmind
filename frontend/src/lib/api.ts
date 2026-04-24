import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = '/api'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
      const token = localStorage.getItem('token')
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth
  async login(username: string, password: string) {
    const res = await this.client.post('/auth/login', { username, password })
    return res.data
  }

  async register(username: string, password: string) {
    const res = await this.client.post('/auth/register', { username, password })
    return res.data
  }

  async getMe() {
    const res = await this.client.get('/auth/me')
    return res.data
  }

  // Records
  async getRecords() {
    const res = await this.client.get('/records')
    return res.data
  }

  async getRecord(id: string) {
    const res = await this.client.get(`/records/${id}`)
    return res.data
  }

  async uploadRecord(file: File, contactName: string) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('contact_name', contactName)
    const res = await this.client.post('/records/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  }

  async deleteRecord(id: string) {
    await this.client.delete(`/records/${id}`)
  }

  async updateRecord(id: string, contactName: string) {
    const res = await this.client.put(`/records/${id}`, { contact_name: contactName })
    return res.data
  }

  // Analysis
  async runAnalysis(recordId: string) {
    const res = await this.client.post(`/analysis/${recordId}`)
    return res.data
  }

  async getStats(recordId: string) {
    const res = await this.client.get(`/analysis/${recordId}/stats`)
    return res.data
  }

  async getPersonality(recordId: string) {
    const res = await this.client.get(`/analysis/${recordId}/personality`)
    return res.data
  }

  async getRelation(recordId: string) {
    const res = await this.client.get(`/analysis/${recordId}/relation`)
    return res.data
  }

  // Reply
  async suggestReply(draft: string, context: string, style: string) {
    const res = await this.client.post('/reply/suggest', { draft, context, style })
    return res.data
  }

  async quickReply(scenario: string, style: string) {
    const res = await this.client.post('/reply/quick', { scenario, style })
    return res.data
  }

  async improveDraft(draft: string, targetStyle: string) {
    const res = await this.client.post('/reply/improve', { draft, target_style: targetStyle })
    return res.data
  }

  // User
  async changePassword(oldPassword: string, newPassword: string) {
    const res = await this.client.put('/user/password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
    return res.data
  }
}

export const api = new ApiClient()