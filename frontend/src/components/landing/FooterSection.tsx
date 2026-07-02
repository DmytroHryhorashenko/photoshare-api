import { BookOpen, Camera } from 'lucide-react'
import { Link } from 'react-router-dom'
import { API_DOCS_URL, GITHUB_URL } from '../../constants/landing'
import { GitHubIcon } from '../icons/GitHubIcon'

const footerLinks = {
  Product: [
    { label: 'Gallery', to: '/gallery' },
    { label: 'Upload', to: '/upload' },
    { label: 'Features', to: '/#features' },
  ],
  API: [
    { label: 'Swagger', href: API_DOCS_URL },
    { label: 'Documentation', href: API_DOCS_URL },
    { label: 'GitHub', href: GITHUB_URL },
  ],
  Account: [
    { label: 'Login', to: '/login' },
    { label: 'Register', to: '/register' },
  ],
}

export default function FooterSection() {
  return (
    <footer className="border-t border-white/5 bg-slate-950/50">
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6">
        <div className="grid gap-12 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <Link to="/" className="flex items-center gap-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-cyan-500">
                <Camera className="h-5 w-5 text-white" />
              </div>
              <span className="font-display text-xl font-bold text-white">
                PhotoShare
              </span>
            </Link>
            <p className="mt-4 max-w-sm text-sm leading-relaxed text-slate-400">
              A modern REST API platform for photo management. Built with FastAPI,
              PostgreSQL, Cloudinary, and Docker.
            </p>
            <div className="mt-6 flex gap-3">
              <a
                href={GITHUB_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 text-slate-400 transition-colors hover:border-white/20 hover:text-white"
                aria-label="GitHub"
              >
                <GitHubIcon className="h-5 w-5" />
              </a>
              <a
                href={API_DOCS_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 text-slate-400 transition-colors hover:border-white/20 hover:text-white"
                aria-label="API Documentation"
              >
                <BookOpen className="h-5 w-5" />
              </a>
            </div>
          </div>

          {Object.entries(footerLinks).map(([group, links]) => (
            <div key={group}>
              <h4 className="font-display text-sm font-semibold uppercase tracking-wider text-slate-300">
                {group}
              </h4>
              <ul className="mt-4 space-y-3">
                {links.map((link) => (
                  <li key={link.label}>
                    {'href' in link ? (
                      <a
                        href={link.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-slate-400 transition-colors hover:text-white"
                      >
                        {link.label}
                      </a>
                    ) : (
                      <Link
                        to={link.to}
                        className="text-sm text-slate-400 transition-colors hover:text-white"
                      >
                        {link.label}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-white/5 pt-8 sm:flex-row">
          <p className="text-sm text-slate-500">
            © {new Date().getFullYear()} PhotoShare. REST API diploma project.
          </p>
          <p className="text-sm text-slate-500">
            Author — FastAPI · Swagger · Docker
          </p>
        </div>
      </div>
    </footer>
  )
}
