import { motion } from 'framer-motion'
import {
  Cloud,
  Container,
  Database,
  FileCode2,
  FlaskConical,
  Server,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { METRICS } from '../../constants/landing'
import { Reveal, SectionHeading } from './Reveal'

const metricIcons: Record<string, LucideIcon> = {
  tests: FlaskConical,
  coverage: FileCode2,
  api: Server,
  swagger: FileCode2,
  docker: Container,
  database: Database,
  cloud: Cloud,
}

export default function MetricsSection() {
  return (
    <section className="px-4 py-24 sm:px-6">
      <div className="mx-auto max-w-6xl">
        <Reveal>
          <SectionHeading
            eyebrow="Metrics"
            title="Project quality at a glance"
            subtitle="Engineering rigor backed by automated tests, documentation, and production-ready infrastructure."
          />
        </Reveal>

        <Reveal delay={0.1}>
          <div className="glass overflow-hidden p-8 sm:p-10">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {METRICS.map((metric, i) => {
                const Icon = metricIcons[metric.icon] ?? Server
                return (
                  <motion.div
                    key={metric.label}
                    className="flex items-center gap-4 rounded-2xl border border-white/5 bg-white/[0.02] p-5 transition-colors hover:border-violet-500/20 hover:bg-violet-500/5"
                    initial={{ opacity: 0, y: 16 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.06 }}
                    whileHover={{ y: -2 }}
                  >
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600/40 to-cyan-500/30">
                      <Icon className="h-5 w-5 text-white" />
                    </div>
                    <span className="font-display font-semibold text-white">
                      {metric.label}
                    </span>
                  </motion.div>
                )
              })}
            </div>

            <div className="mt-8 grid gap-4 border-t border-white/10 pt-8 sm:grid-cols-3">
              {[
                { label: 'Test suite', value: '184 passed' },
                { label: 'Code coverage', value: '94%' },
                { label: 'API style', value: 'REST + OpenAPI' },
              ].map((item) => (
                <div key={item.label} className="text-center sm:text-left">
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    {item.label}
                  </p>
                  <p className="mt-1 font-display text-2xl font-bold text-white">
                    {item.value}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  )
}
