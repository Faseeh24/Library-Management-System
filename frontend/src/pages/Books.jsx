/* Catalog page that lists books, filters locally, and creates loans. */

import { useEffect, useMemo, useState } from 'react'

import { getBooks, getMembers } from '../api/books'
import { createLoan, getLoans } from '../api/loans'
import { getApiErrorMessage } from '../api/axios'
import BookCard from '../components/BookCard'
import LoadingSpinner from '../components/LoadingSpinner'
import SearchBar from '../components/SearchBar'

export default function Books() {
  const [books, setBooks] = useState([])
  const [members, setMembers] = useState([])
  const [loans, setLoans] = useState([])
  const [query, setQuery] = useState('')
  const [selectedBookId, setSelectedBookId] = useState('')
  const [selectedMemberId, setSelectedMemberId] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const loadCatalog = async () => {
    setLoading(true)
    setError('')

    try {
      const [bookList, memberList, loanList] = await Promise.all([
        getBooks(),
        getMembers(),
        getLoans(),
      ])

      setBooks(bookList)
      setMembers(memberList)
      setLoans(loanList)

      if (!selectedBookId && bookList.length > 0) {
        setSelectedBookId(String(bookList[0].id))
      }

      if (!selectedMemberId && memberList.length > 0) {
        setSelectedMemberId(String(memberList[0].id))
      }
    } catch (requestError) {
      setError(getApiErrorMessage(requestError))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCatalog()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const loanedBookIds = useMemo(() => new Set(loans.map((loan) => loan.book_id)), [loans])

  const filteredBooks = useMemo(() => {
    const term = query.trim().toLowerCase()

    const visibleBooks = term
      ? books.filter(
          (book) =>
            book.title.toLowerCase().includes(term) ||
            book.author.toLowerCase().includes(term),
        )
      : books

    return [...visibleBooks].sort((left, right) => {
      const leftAvailable = !loanedBookIds.has(left.id)
      const rightAvailable = !loanedBookIds.has(right.id)

      if (leftAvailable === rightAvailable) {
        return left.title.localeCompare(right.title)
      }

      return leftAvailable ? -1 : 1
    })
  }, [books, loanedBookIds, query])

  const handleLoan = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    setMessage('')

    try {
      await createLoan({
        book_id: Number(selectedBookId),
        member_id: Number(selectedMemberId),
      })

      setMessage('Loan created successfully.')
      await loadCatalog()
    } catch (requestError) {
      setError(getApiErrorMessage(requestError))
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return <LoadingSpinner message="Loading book catalog..." />
  }

  return (
    <div className="page-stack">
      <section className="page-head">
        <div>
          <p className="eyebrow">Book catalog</p>
          <h1>Browse titles and place loans</h1>
          <p className="lede">
            Search by title or author, see which books are already borrowed, and
            create a loan from the existing FastAPI endpoint.
          </p>
        </div>
      </section>

      <SearchBar
        value={query}
        onChange={setQuery}
        placeholder="Search by title or author"
      />

      {error ? <p className="error-banner">{error}</p> : null}
      {message ? <p className="success-banner">{message}</p> : null}

      <section className="content-grid">
        <div className="cards-grid">
          {filteredBooks.map((book) => {
            const available = !loanedBookIds.has(book.id)

            return (
              <BookCard
                key={book.id}
                book={book}
                available={available}
                selected={Number(selectedBookId) === book.id}
                onSelect={(bookId) => setSelectedBookId(String(bookId))}
              />
            )
          })}
        </div>

        <aside className="sidebar-panel">
          <h2>Loan Book</h2>
          <form className="stack" onSubmit={handleLoan}>
            <label>
              <span>Book</span>
              <select
                value={selectedBookId}
                onChange={(event) => setSelectedBookId(event.target.value)}
                required
              >
                {books.map((book) => (
                  <option key={book.id} value={book.id}>
                    {book.title}
                  </option>
                ))}
              </select>
            </label>

            <label>
              <span>Member</span>
              <select
                value={selectedMemberId}
                onChange={(event) => setSelectedMemberId(event.target.value)}
                required
              >
                {members.map((member) => (
                  <option key={member.id} value={member.id}>
                    {member.name}
                  </option>
                ))}
              </select>
            </label>

            <button type="submit" className="button button-primary" disabled={submitting}>
              {submitting ? 'Saving...' : 'Create loan'}
            </button>
          </form>
        </aside>
      </section>
    </div>
  )
}
