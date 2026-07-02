import { ExternalLink } from 'lucide-react'
import { API_DOCS_URL, API_ENDPOINTS } from '../../constants/landing'
import { Reveal, SectionHeading } from './Reveal'

export default function ApiPreviewSection() {
  return (
    <section id="documentation" className="px-4 py-24 sm:px-6">
      <div className="mx-auto max-w-4xl">
        <Reveal>
          <SectionHeading
            eyebrow="API"
            title="Explore the REST API"
            subtitle="Fully documented endpoints with interactive Swagger UI. Test every route without writing a single line of frontend code."
          />
        </Reveal>

        <Reveal delay={0.1}>
          <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-900/80 shadow-2xl shadow-violet-500/5">
            <div className="flex items-center gap-2 border-b border-white/10 bg-white/[0.03] px-4 py-3">
              <div className="h-3 w-3 rounded-full bg-rose-400/80" />
              <div className="h-3 w-3 rounded-full bg-amber-400/80" />
              <div className="h-3 w-3 rounded-full bg-emerald-400/80" />
              <span className="ml-2 text-xs text-slate-500">photoshare-api</span>
            </div>

            <div className="space-y-1 p-6 font-mono text-sm">
              {API_ENDPOINTS.map((endpoint) => (
                <div
                  key={endpoint.path}
                  className="flex flex-wrap items-center gap-3 rounded-lg px-3 py-2 transition-colors hover:bg-white/[0.03]"
                >
                  <span
                    className={`min-w-[3.5rem] font-semibold ${endpoint.color}`}
                  >
                    {endpoint.method}
                  </span>
                  <span className="text-slate-300">{endpoint.path}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-8 text-center">
            <a
              href={API_DOCS_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary inline-flex px-8 py-3"
            >
              Open Swagger
              <ExternalLink className="h-4 w-4" />
            </a>
          </div>
        </Reveal>
      </div>
    </section>
  )
}
