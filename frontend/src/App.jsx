/* Application routes for the FastAPI-powered library frontend. */

import { Navigate, Outlet, Route, Routes } from 'react-router-dom'

import ProtectedRoute from './components/ProtectedRoute'
import LoadingSpinner from './components/LoadingSpinner'
import Navbar from './components/Navbar'
import { useAuth } from './context/AuthContext'
import Books from './pages/Books'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import MyLoans from './pages/MyLoans'
import Register from './pages/Register'

function AppShell() {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

function RootRedirect() {
  const { user, loading } = useAuth()

  if (loading) {
    return <LoadingSpinner message="Loading session..." />
  }

  return <Navigate to={user ? '/dashboard' : '/login'} replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<RootRedirect />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Register />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="books" element={<Books />} />
          <Route path="loans" element={<MyLoans />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
