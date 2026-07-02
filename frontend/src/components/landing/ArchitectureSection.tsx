import { motion } from 'framer-motion'
import { ArrowDown } from 'lucide-react'
import { ARCHITECTURE } from '../../constants/landing'
import { Reveal, SectionHeading } from './Reveal'

export default function ArchitectureSection() {
  return (
    <section className="px-4 py-24 sm:px-6">
      <div className="mx-auto max-w-5xl">
        <Reveal>
          <SectionHeading
            eyebrow="Architecture"
            title="Layered, scalable system design"
            subtitle="A clean separation between presentation, API, persistence, and external services."
          />
        </Reveal>

        <Reveal delay={0.1}>
          <div className="glass relative overflow-hidden p-8 sm:p-12">
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-r from-violet-600/5 via-transparent to-cyan-500/5" />

            <div className="relative flex flex-col items-center gap-2">
              {ARCHITECTURE.map((layer, i) => (
                <div key={layer} className="flex w-full max-w-md flex-col items-center">
                  <motion.div
                    className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-8 py-5 text-center backdrop-blur transition-colors hover:border-violet-500/30 hover:bg-violet-500/10"
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1, duration: 0.5 }}
                    whileHover={{ scale: 1.02 }}
                  >
                    <span className="font-display text-lg font-semibold text-white">
                      {layer}
                    </span>
                  </motion.div>
                  {i < ARCHITECTURE.length - 1 && (
                    <ArrowDown className="my-1 h-5 w-5 text-violet-500/50" />
                  )}
                </div>
              ))}
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  )
}
