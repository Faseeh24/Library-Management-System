/* Dashboard with quick stats from the books and loan endpoints. */

import { useEffect, useState } from 'react'

import { getBooks } from '../api/books'
import { getLoans } from '../api/loans'
import LoadingSpinner from '../components/LoadingSpinner'
import { getApiErrorMessage } from '../api/axios'
import { useAuth } from '../context/AuthContext'

export default function Dashboard() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [summary, setSummary] = useState({ books: 0, availableBooks: 0, loans: 0 })

  useEffect(() => {
    const loadSummary = async () => {
      setLoading(true)
      setError('')

      try {
        const [books, loans] = await Promise.all([getBooks(), getLoans()])
        const loanedBookIds = new Set(loans.map((loan) => loan.book_id))
        const availableBooks = books.filter((book) => !loanedBookIds.has(book.id)).length

        setSummary({
          books: books.length,
          availableBooks,
          loans: loans.length,
        })
      } catch (requestError) {
        setError(getApiErrorMessage(requestError))
      } finally {
        setLoading(false)
      }
    }

    loadSummary()
  }, [])

  if (loading) {
    return <LoadingSpinner message="Loading dashboard..." />
  }

  return (
    <div className="page-stack">
      <section className="hero-panel">
        <div>
          <p className="eyebrow">Dashboard</p>
          <h1>Welcome back, {user?.username}</h1>
          <p className="lede">
            Monitor catalog health, track loan activity, and move quickly into the
            books or loans screens.
          </p>
        </div>
      </section>

      {error ? <p className="error-banner">{error}</p> : null}

      <section className="stats-grid">
        <article className="stat-card">
          <span>Total books</span>
          <strong>{summary.books}</strong>
        </article>
        <article className="stat-card">
          <span>Available books</span>
          <strong>{summary.availableBooks}</strong>
        </article>
        <article className="stat-card">
          <span>Open loans</span>
          <strong>{summary.loans}</strong>
        </article>
      </section>
    </div>
  )
}
