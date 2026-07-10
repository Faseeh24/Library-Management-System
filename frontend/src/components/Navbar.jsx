/* Top navigation for the authenticated area. */

import { NavLink } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'

const navItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/books', label: 'Books' },
  { to: '/loans', label: 'My Loans' },
]

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Library Management System</p>
        <h1 className="topbar-title">Reader workspace</h1>
      </div>

      <nav className="nav-links" aria-label="Primary">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              isActive ? 'nav-link active' : 'nav-link'
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="user-chip-row">
        <div className="user-chip">
          <span className="user-chip-label">Signed in as</span>
          <strong>{user?.username}</strong>
          <span className="user-chip-role">{user?.role}</span>
        </div>

        <button type="button" className="button button-ghost" onClick={logout}>
          Logout
        </button>
      </div>
    </header>
  )
}
