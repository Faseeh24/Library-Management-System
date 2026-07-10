/* Simple loading indicator used across protected pages. */

export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="loading-shell" role="status" aria-live="polite">
      <div className="spinner" aria-hidden="true" />
      <p>{message}</p>
    </div>
  )
}
