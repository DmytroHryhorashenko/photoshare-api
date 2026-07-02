import { ArrowRight, BookOpen, Play } from 'lucide-react'
import { Link } from 'react-router-dom'
import { API_DOCS_URL, GITHUB_URL } from '../../constants/landing'
import { GitHubIcon } from '../icons/GitHubIcon'
import HeroDashboard from './HeroDashboard'
import { Reveal } from './Reveal'

export default function HeroSection() {
  return (
    <section
      id="home"
      className="relative overflow-hidden px-4 pb-24 pt-12 sm:px-6 lg:pb-32 lg:pt-20"
    >
      <div className="pointer-events-none absolute left-1/2 top-0 h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-violet-600/15 blur-[120px]" />
      <div className="pointer-events-none absolute -right-20 top-40 h-72 w-72 rounded-full bg-cyan-500/10 blur-[100px]" />

      <div className="relative mx-auto grid max-w-7xl items-center gap-16 lg:grid-cols-2 lg:gap-12">
        <div>
          <Reveal>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-sm text-slate-300 backdrop-blur">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
              </span>
              Production-ready REST API
            </div>
          </Reveal>

          <Reveal delay={0.05}>
            <h1 className="font-display text-5xl font-extrabold leading-[1.05] tracking-tight sm:text-6xl lg:text-7xl">
              <span className="bg-gradient-to-r from-white via-violet-100 to-cyan-200 bg-clip-text text-transparent">
                PhotoShare
              </span>
            </h1>
          </Reveal>

          <Reveal delay={0.1}>
            <p className="mt-4 font-display text-xl font-semibold text-slate-300 sm:text-2xl">
              Modern REST API Platform
              <br />
              <span className="text-slate-400">for Photo Management</span>
            </p>
          </Reveal>

          <Reveal delay={0.15}>
            <p className="mt-6 max-w-xl text-base leading-relaxed text-slate-400 sm:text-lg">
              Upload, transform, organize and share your photos through a secure
              FastAPI backend powered by PostgreSQL, Cloudinary and Docker.
            </p>
          </Reveal>

          <Reveal delay={0.2}>
            <div className="mt-10 flex flex-wrap gap-3">
              <Link to="/register" className="btn-primary px-6 py-3">
                Get Started
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link to="/gallery" className="btn-secondary px-6 py-3">
                <Play className="h-4 w-4" />
                Explore Gallery
              </Link>
              <a
                href={API_DOCS_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary px-6 py-3"
              >
                <BookOpen className="h-4 w-4" />
                Swagger API
              </a>
              <a
                href={GITHUB_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary px-6 py-3"
              >
                <GitHubIcon className="h-4 w-4" />
                GitHub
              </a>
            </div>
          </Reveal>
        </div>

        <Reveal delay={0.25} className="lg:pl-8">
          <HeroDashboard />
        </Reveal>
      </div>
    </section>
  )
}
