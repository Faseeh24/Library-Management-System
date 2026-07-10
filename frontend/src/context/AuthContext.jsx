/* Auth context for token persistence, session hydration, and logout handling. */

import { createContext, useContext, useEffect, useState } from 'react'

import { getCurrentUser, loginUser } from '../api/auth'
import {
  AUTH_LOGOUT_EVENT,
  TOKEN_KEY,
} from '../api/axios'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const clearSession = () => {
    localStorage.removeItem(TOKEN_KEY)
    setUser(null)
  }

  const login = async (credentials) => {
    const loginResponse = await loginUser(credentials)
    localStorage.setItem(TOKEN_KEY, loginResponse.access_token)

    try {
      const currentUser = await getCurrentUser()
      setUser(currentUser)
      return currentUser
    } catch (error) {
      clearSession()
      throw error
    }
  }

  const logout = () => {
    clearSession()
  }

  useEffect(() => {
    const hydrateSession = async () => {
      const token = localStorage.getItem(TOKEN_KEY)

      if (!token) {
        setLoading(false)
        return
      }

      try {
        const currentUser = await getCurrentUser()
        setUser(currentUser)
      } catch (error) {
        clearSession()
      } finally {
        setLoading(false)
      }
    }

    const handleForcedLogout = () => {
      clearSession()
    }

    window.addEventListener(AUTH_LOGOUT_EVENT, handleForcedLogout)
    hydrateSession()

    return () => {
      window.removeEventListener(AUTH_LOGOUT_EVENT, handleForcedLogout)
    }
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: Boolean(user),
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }

  return context
}
