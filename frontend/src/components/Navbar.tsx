import { BookOpen, Camera, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { API_DOCS_URL, GITHUB_URL } from '../constants/landing'
import { GitHubIcon } from './icons/GitHubIcon'

function scrollToSection(id: string) {
  if (window.location.pathname !== '/') {
    window.location.href = `/#${id}`
    return
  }
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
      isActive
        ? 'bg-white/10 text-white'
        : 'text-slate-400 hover:bg-white/5 hover:text-white'
    }`

  const anchorClass =
    'rounded-lg px-3 py-2 text-sm font-medium text-slate-400 transition-colors hover:bg-white/5 hover:text-white cursor-pointer'

  return (
    <header className="sticky top-0 z-50 border-b border-white/5 bg-slate-950/70 backdrop-blur-xl supports-[backdrop-filter]:bg-slate-950/60">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        <Link to="/" className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-cyan-500 shadow-lg shadow-violet-500/25">
            <Camera className="h-5 w-5 text-white" />
          </div>
          <span className="font-display text-xl font-bold tracking-tight text-white">
            PhotoShare
          </span>
        </Link>

        <div className="hidden items-center gap-1 lg:flex">
          <Link to="/" className={anchorClass}>
            Home
          </Link>
          <NavLink to="/gallery" className={linkClass}>
            Gallery
          </NavLink>
          <button
            type="button"
            onClick={() => scrollToSection('features')}
            className={anchorClass}
          >
            Features
          </button>
          <button
            type="button"
            onClick={() => scrollToSection('documentation')}
            className={anchorClass}
          >
            Documentation
          </button>
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
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className={anchorClass}
          >
            <span className="inline-flex items-center gap-1.5">
              <GitHubIcon className="h-4 w-4" />
              GitHub
            </span>
          </a>
        </div>

        <div className="hidden items-center gap-2 lg:flex">
          {isAuthenticated ? (
            <>
              <span className="text-sm text-slate-400">{user?.username}</span>
              <button onClick={() => logout()} className="btn-ghost">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-ghost">
                Login
              </Link>
              <Link to="/register" className="btn-primary">
                Register
              </Link>
            </>
          )}
          <a
            href={API_DOCS_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-ghost hidden xl:inline-flex"
            aria-label="Swagger"
          >
            <BookOpen className="h-4 w-4" />
          </a>
        </div>

        <button
          type="button"
          className="rounded-lg p-2 text-slate-400 hover:bg-white/5 hover:text-white lg:hidden"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </nav>

      {mobileOpen && (
        <div className="border-t border-white/5 bg-slate-950/95 px-4 py-4 lg:hidden">
          <div className="flex flex-col gap-1">
            <Link to="/" className={anchorClass} onClick={() => setMobileOpen(false)}>
              Home
            </Link>
            <NavLink to="/gallery" className={linkClass} onClick={() => setMobileOpen(false)}>
              Gallery
            </NavLink>
            <button
              type="button"
              className={`${anchorClass} text-left`}
              onClick={() => {
                scrollToSection('features')
                setMobileOpen(false)
              }}
            >
              Features
            </button>
            <button
              type="button"
              className={`${anchorClass} text-left`}
              onClick={() => {
                scrollToSection('documentation')
                setMobileOpen(false)
              }}
            >
              Documentation
            </button>
            {isAuthenticated && (
              <>
                <NavLink to="/upload" className={linkClass} onClick={() => setMobileOpen(false)}>
                  Upload
                </NavLink>
                <NavLink to="/profile" className={linkClass} onClick={() => setMobileOpen(false)}>
                  Profile
                </NavLink>
                {user?.role === 'admin' && (
                  <NavLink to="/admin" className={linkClass} onClick={() => setMobileOpen(false)}>
                    Admin
                  </NavLink>
                )}
              </>
            )}
            <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer" className={anchorClass}>
              GitHub
            </a>
            <div className="mt-3 flex gap-2 border-t border-white/5 pt-3">
              {isAuthenticated ? (
                <button onClick={() => logout()} className="btn-ghost w-full">
                  Logout
                </button>
              ) : (
                <>
                  <Link to="/login" className="btn-ghost flex-1" onClick={() => setMobileOpen(false)}>
                    Login
                  </Link>
                  <Link to="/register" className="btn-primary flex-1" onClick={() => setMobileOpen(false)}>
                    Register
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  )
}
