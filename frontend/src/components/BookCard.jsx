/* Reusable catalog card with availability and selection state. */

export default function BookCard({ book, available, selected, onSelect }) {
  return (
    <article className={selected ? 'book-card selected' : 'book-card'}>
      <div className="book-card-header">
        <div>
          <span className={available ? 'badge badge-success' : 'badge badge-warning'}>
            {available ? 'Available' : 'Borrowed'}
          </span>
          <h3>{book.title}</h3>
        </div>
      </div>

      <p className="muted">by {book.author}</p>
      <p className="small-text">Book ID {book.id}</p>

      <button
        type="button"
        className="button button-secondary"
        onClick={() => onSelect?.(book.id)}
        disabled={!available}
      >
        {selected ? 'Selected for loan' : 'Loan this book'}
      </button>
    </article>
  )
}
