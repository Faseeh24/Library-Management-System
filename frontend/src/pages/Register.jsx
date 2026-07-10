/* Registration screen for the existing FastAPI signup endpoint. */

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { registerUser } from '../api/auth'
import { getApiErrorMessage } from '../api/axios'

export default function Register() {
  const navigate = useNavigate()

  const [form, setForm] = useState({
    username: '',
    password: '',
    confirmPassword: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    setSuccess('')

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.')
      setSubmitting(false)
      return
    }

    try {
      await registerUser({
        username: form.username,
        password: form.password,
      })

      setSuccess('Account created. You can now sign in.')
      setTimeout(() => navigate('/login', { replace: true }), 900)
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
        <h1>Create your library account.</h1>
        <p className="lede">
          Sign up with the same backend the app already uses. New users are created
          as member accounts by default.
        </p>
      </section>

      <section className="auth-panel auth-card">
        <h2>Sign up</h2>
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
              autoComplete="new-password"
              required
            />
          </label>

          <label>
            <span>Confirm password</span>
            <input
              type="password"
              value={form.confirmPassword}
              onChange={(event) =>
                setForm({ ...form, confirmPassword: event.target.value })
              }
              autoComplete="new-password"
              required
            />
          </label>

          {error ? <p className="error-banner">{error}</p> : null}
          {success ? <p className="success-banner">{success}</p> : null}

          <button type="submit" className="button button-primary" disabled={submitting}>
            {submitting ? 'Creating account...' : 'Create account'}
          </button>

          <p className="small-text">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </form>
      </section>
    </div>
  )
}