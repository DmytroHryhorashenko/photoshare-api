import { Link, NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const API_DOCS_URL = 'http://localhost:8000/docs'

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
      isActive
        ? 'bg-white/10 text-white'
        : 'text-slate-400 hover:bg-white/5 hover:text-white'
    }`

  return (
    <header className="sticky top-0 z-50 border-b border-white/5 bg-slate-950/80 backdrop-blur-xl">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-cyan-500 shadow-lg shadow-violet-500/30">
            <svg
              className="h-5 w-5 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
          </div>
          <span className="font-display text-xl font-bold tracking-tight">
            PhotoShare
          </span>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          <NavLink to="/gallery" className={linkClass}>
            Gallery
          </NavLink>
          {isAuthenticated && (
            <>
              <NavLink to="/upload" className={linkClass}>
                Upload
              </NavLink>
              <NavLink to="/profile" className={linkClass}>
                Profile
              </NavLink>
              {user?.role === 'admin' && (
                <NavLink to="/admin" className={linkClass}>
                  Admin
                </NavLink>
              )}
            </>
          )}
          <a
            href={API_DOCS_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg px-3 py-2 text-sm font-medium text-slate-400 transition-colors hover:bg-white/5 hover:text-white"
          >
            API Docs
          </a>
        </div>

        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <>
              <span className="hidden text-sm text-slate-400 sm:inline">
                {user?.username}
              </span>
              <button onClick={() => logout()} className="btn-ghost">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-ghost">
                Login
              </Link>
              <Link to="/register" className="btn-primary hidden sm:inline-flex">
                Register
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  )
}
