/* Shared Axios client configured from VITE_API_URL and the stored bearer token. */

import axios from 'axios'

export const TOKEN_KEY = 'library_auth_token'
export const AUTH_LOGOUT_EVENT = 'library-auth-forced-logout'

const apiBaseUrl = import.meta.env.VITE_API_URL

if (!apiBaseUrl) {
  throw new Error('VITE_API_URL is required for the frontend to reach the FastAPI backend.')
}

export const api = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)

  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)

      // Notify the auth context so the UI can return to the login page.
      window.dispatchEvent(new Event(AUTH_LOGOUT_EVENT))
    }

    return Promise.reject(error)
  },
)

export function getApiErrorMessage(error) {
  if (!error) {
    return 'Unknown error'
  }

  const detail = error.response?.data?.detail
  const message = error.response?.data?.message

  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg || item?.message || JSON.stringify(item))
      .join(', ')
  }

  if (typeof message === 'string') {
    return message
  }

  if (!error.response) {
    return 'Network error. Check the backend container and Docker network.'
  }

  return error.message || 'Request failed'
}
