/* Route guard that blocks unauthenticated access to the app shell. */

import { Navigate, Outlet, useLocation } from 'react-router-dom'

import LoadingSpinner from './LoadingSpinner'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute() {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return <LoadingSpinner message="Checking session..." />
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <Outlet />
}
