/* Loan management screen that returns books by closing existing loans. */

import { useEffect, useMemo, useState } from 'react'

import { getBooks, getMembers } from '../api/books'
import { deleteLoan, getLoans } from '../api/loans'
import { getApiErrorMessage } from '../api/axios'
import LoadingSpinner from '../components/LoadingSpinner'

export default function MyLoans() {
  const [loans, setLoans] = useState([])
  const [books, setBooks] = useState([])
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [actionLoadingId, setActionLoadingId] = useState(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const loadLoans = async () => {
    setLoading(true)
    setError('')

    try {
      const [loanList, bookList, memberList] = await Promise.all([
        getLoans(),
        getBooks(),
        getMembers(),
      ])

      setLoans(loanList)
      setBooks(bookList)
      setMembers(memberList)
    } catch (requestError) {
      setError(getApiErrorMessage(requestError))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadLoans()
  }, [])

  const bookLookup = useMemo(() => {
    return new Map(books.map((book) => [book.id, book]))
  }, [books])

  const memberLookup = useMemo(() => {
    return new Map(members.map((member) => [member.id, member]))
  }, [members])

  const handleReturn = async (loanId) => {
    setActionLoadingId(loanId)
    setError('')
    setMessage('')

    try {
      // The backend closes a loan by deleting it, so the UI uses DELETE /loans/{id} as the return action.
      await deleteLoan(loanId)
      setMessage('Book returned successfully.')
      await loadLoans()
    } catch (requestError) {
      setError(getApiErrorMessage(requestError))
    } finally {
      setActionLoadingId(null)
    }
  }

  if (loading) {
    return <LoadingSpinner message="Loading active loans..." />
  }

  return (
    <div className="page-stack">
      <section className="page-head">
        <div>
          <p className="eyebrow">Active loans</p>
          <h1>My Loans</h1>
          <p className="lede">
            This screen shows the current loan records exposed by the backend and
            lets you return a book by closing the matching loan.
          </p>
        </div>
      </section>

      {error ? <p className="error-banner">{error}</p> : null}
      {message ? <p className="success-banner">{message}</p> : null}

      <section className="loan-list">
        {loans.map((loan) => {
          const book = bookLookup.get(loan.book_id)
          const member = memberLookup.get(loan.member_id)

          return (
            <article key={loan.id} className="loan-row">
              <div>
                <h3>{book?.title || `Book #${loan.book_id}`}</h3>
                <p className="muted">Borrowed by {member?.name || `Member #${loan.member_id}`}</p>
                <p className="small-text">Loan ID {loan.id}</p>
              </div>

              <button
                type="button"
                className="button button-secondary"
                onClick={() => handleReturn(loan.id)}
                disabled={actionLoadingId === loan.id}
              >
                {actionLoadingId === loan.id ? 'Returning...' : 'Return book'}
              </button>
            </article>
          )
        })}

        {loans.length === 0 ? <p className="empty-state">No active loans found.</p> : null}
      </section>
    </div>
  )
}
