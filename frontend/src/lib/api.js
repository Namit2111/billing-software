import axios from 'axios'
import toast from 'react-hot-toast'

const API_BASE_URL = '/api/v1'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.error?.message || error.message || 'An error occurred'
    
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    } else if (error.response?.status === 403) {
      toast.error('You do not have permission to perform this action')
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.')
    }
    
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
  updateProfile: (data) => api.patch('/auth/me', data),
  requestPasswordReset: (email) => api.post('/auth/password-reset', { email }),
  changePassword: (data) => api.post('/auth/change-password', data),
}

// Dashboard API
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getActivity: (limit = 10) => api.get(`/dashboard/activity?limit=${limit}`),
  getOverdue: () => api.get('/dashboard/overdue'),
}

// Clients API
export const clientsAPI = {
  list: (params) => api.get('/clients', { params }),
  get: (id) => api.get(`/clients/${id}`),
  create: (data) => api.post('/clients', data),
  update: (id, data) => api.patch(`/clients/${id}`, data),
  delete: (id) => api.delete(`/clients/${id}`),
  search: (q, limit = 10) => api.get('/clients/search', { params: { q, limit } }),
}

// Products API
export const productsAPI = {
  list: (params) => api.get('/products', { params }),
  get: (id) => api.get(`/products/${id}`),
  create: (data) => api.post('/products', data),
  update: (id, data) => api.patch(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
  search: (q, limit = 10) => api.get('/products/search', { params: { q, limit } }),
}

// Invoices API
export const invoicesAPI = {
  list: (params) => api.get('/invoices', { params }),
  get: (id) => api.get(`/invoices/${id}`),
  create: (data) => api.post('/invoices', data),
  update: (id, data) => api.patch(`/invoices/${id}`, data),
  delete: (id) => api.delete(`/invoices/${id}`),
  addItem: (invoiceId, data) => api.post(`/invoices/${invoiceId}/items`, data),
  updateItem: (invoiceId, itemId, data) => api.patch(`/invoices/${invoiceId}/items/${itemId}`, data),
  deleteItem: (invoiceId, itemId) => api.delete(`/invoices/${invoiceId}/items/${itemId}`),
  send: (id, data) => api.post(`/invoices/${id}/send`, data),
  markPaid: (id, data) => api.post(`/invoices/${id}/mark-paid`, data),
  downloadPdf: (id) => api.get(`/invoices/${id}/pdf`, { responseType: 'blob' }),
  getEmails: (id) => api.get(`/invoices/${id}/emails`),
}

// Reports API
export const reportsAPI = {
  revenue: (startDate, endDate) => 
    api.get('/reports/revenue', { params: { start_date: startDate, end_date: endDate } }),
  outstanding: () => api.get('/reports/outstanding'),
  exportCsv: (startDate, endDate) => 
    api.get('/reports/export/invoices', { 
      params: { start_date: startDate, end_date: endDate },
      responseType: 'blob'
    }),
  monthlySummary: (year, month) => 
    api.get('/reports/summary', { params: { year, month } }),
}

// Settings API
export const settingsAPI = {
  getOrganization: () => api.get('/settings/organization'),
  updateOrganization: (data) => api.patch('/settings/organization', data),
  uploadLogo: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/settings/organization/logo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  updateInvoiceSettings: (data) => api.patch('/settings/invoice', data),
  getTaxes: () => api.get('/settings/taxes'),
  createTax: (data) => api.post('/settings/taxes', data),
  updateTax: (id, data) => api.patch(`/settings/taxes/${id}`, data),
  deleteTax: (id) => api.delete(`/settings/taxes/${id}`),
  getMembers: () => api.get('/settings/members'),
}

export default api

