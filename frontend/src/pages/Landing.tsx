import { Link } from 'react-router-dom'

const API_DOCS_URL = 'http://localhost:8000/docs'

export default function Landing() {
  return (
    <section className="relative overflow-hidden px-4 py-20 sm:px-6 sm:py-32">
      <div className="pointer-events-none absolute left-1/2 top-20 h-72 w-72 -translate-x-1/2 rounded-full bg-violet-600/20 blur-3xl" />
      <div className="pointer-events-none absolute right-10 top-40 h-48 w-48 rounded-full bg-cyan-500/15 blur-3xl" />

      <div className="relative mx-auto max-w-4xl text-center">
        <div className="animate-slide-up mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-sm text-slate-300 backdrop-blur">
          <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
          Production-ready REST API
        </div>

        <h1 className="animate-slide-up font-display text-5xl font-extrabold tracking-tight sm:text-7xl">
          <span className="bg-gradient-to-r from-white via-violet-200 to-cyan-200 bg-clip-text text-transparent">
            PhotoShare
          </span>
        </h1>

        <p className="animate-slide-up mx-auto mt-6 max-w-2xl text-lg text-slate-400 sm:text-xl">
          Share, discover, and transform photos. Upload to Cloudinary, tag your
          moments, rate and comment — all powered by a modern FastAPI backend.
        </p>

        <div className="animate-slide-up mt-10 flex flex-wrap items-center justify-center gap-4">
          <Link to="/gallery" className="btn-primary px-8 py-3 text-base">
            Open Gallery
          </Link>
          <Link to="/login" className="btn-secondary px-8 py-3 text-base">
            Login
          </Link>
          <Link to="/register" className="btn-secondary px-8 py-3 text-base">
            Register
          </Link>
          <a
            href={API_DOCS_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary px-8 py-3 text-base"
          >
            API Docs
          </a>
        </div>

        <div className="animate-slide-up mt-20 grid gap-6 sm:grid-cols-3">
          {[
            {
              title: 'Upload & Tag',
              desc: 'Cloudinary-powered uploads with up to 5 tags per photo.',
              icon: '📸',
            },
            {
              title: 'Rate & Comment',
              desc: 'Community engagement with star ratings and discussions.',
              icon: '⭐',
            },
            {
              title: 'Transform & QR',
              desc: 'Apply effects, resize, and share via QR codes.',
              icon: '✨',
            },
          ].map((feature) => (
            <div key={feature.title} className="glass glass-hover p-6 text-left">
              <span className="text-3xl">{feature.icon}</span>
              <h3 className="mt-3 font-display text-lg font-semibold">
                {feature.title}
              </h3>
              <p className="mt-2 text-sm text-slate-400">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
