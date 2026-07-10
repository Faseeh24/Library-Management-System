/* Login screen that uses the existing FastAPI auth endpoint. */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'

import LoadingSpinner from '../components/LoadingSpinner'
import { getApiErrorMessage } from '../api/axios'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login, user, loading } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const fromPath = location.state?.from?.pathname || '/dashboard'

  const [form, setForm] = useState({ username: '', password: '' })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  if (loading) {
    return <LoadingSpinner message="Preparing login..." />
  }

  if (user) {
    return <Navigate to={fromPath} replace />
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')

    try {
      await login(form)
      navigate(fromPath, { replace: true })
    } catch (requestError) {
      setError(getApiErrorMessage(requestError))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-layout">
      <section className="auth-panel auth-panel-copy">
        <p className="eyebrow">FastAPI + React</p>
        <h1>Library operations, in one place.</h1>
        <p className="lede">
          Sign in to manage the catalog, create loans, and close returns using the
          exact backend routes already implemented in the API.
        </p>
      </section>

      <section className="auth-panel auth-card">
        <h2>Login</h2>
        <form className="stack" onSubmit={handleSubmit}>
          <label>
            <span>Username</span>
            <input
              type="text"
              value={form.username}
              onChange={(event) => setForm({ ...form, username: event.target.value })}
              autoComplete="username"
              required
            />
          </label>

          <label>
            <span>Password</span>
            <input
              type="password"
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
              autoComplete="current-password"
              required
            />
          </label>

          {error ? <p className="error-banner">{error}</p> : null}

          <button type="submit" className="button button-primary" disabled={submitting}>
            {submitting ? 'Signing in...' : 'Sign in'}
          </button>

          <p className="small-text">
            New here? <Link to="/signup">Create an account</Link>
          </p>
        </form>
      </section>
    </div>
  )
}
