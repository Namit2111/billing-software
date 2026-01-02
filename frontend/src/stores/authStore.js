import { create } from 'zustand'
import { authAPI } from '../lib/api'

export const useAuthStore = create((set, get) => ({
  user: null,
  organization: null,
  isAuthenticated: false,
  isLoading: true,

  // Initialize auth state from localStorage
  initialize: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      set({ isLoading: false, isAuthenticated: false })
      return
    }

    try {
      const response = await authAPI.me()
      const user = response.data.data
      set({
        user,
        organization: user.organization,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      set({ isLoading: false, isAuthenticated: false })
    }
  },

  // Login
  login: async (email, password) => {
    const response = await authAPI.login({ email, password })
    const { user, access_token, refresh_token } = response.data.data

    localStorage.setItem('access_token', access_token)
    if (refresh_token) {
      localStorage.setItem('refresh_token', refresh_token)
    }

    set({
      user,
      organization: user.organization,
      isAuthenticated: true,
    })

    return user
  },

  // Register
  register: async (data) => {
    const response = await authAPI.register(data)
    const { user, access_token, refresh_token } = response.data.data

    localStorage.setItem('access_token', access_token)
    if (refresh_token) {
      localStorage.setItem('refresh_token', refresh_token)
    }

    set({
      user,
      organization: user.organization,
      isAuthenticated: true,
    })

    return user
  },

  // Logout
  logout: async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      // Ignore errors during logout
    }
    
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    
    set({
      user: null,
      organization: null,
      isAuthenticated: false,
    })
  },

  // Update user profile
  updateProfile: async (data) => {
    const response = await authAPI.updateProfile(data)
    const user = response.data.data
    set({ user })
    return user
  },

  // Refresh user data
  refreshUser: async () => {
    const response = await authAPI.me()
    const user = response.data.data
    set({
      user,
      organization: user.organization,
    })
    return user
  },
}))

// Initialize on load
if (typeof window !== 'undefined') {
  useAuthStore.getState().initialize()
}

