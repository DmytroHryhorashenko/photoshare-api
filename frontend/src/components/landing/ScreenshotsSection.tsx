import { motion } from 'framer-motion'
import { ImageIcon } from 'lucide-react'
import { SCREENSHOTS } from '../../constants/landing'
import { Reveal, SectionHeading } from './Reveal'

export default function ScreenshotsSection() {
  return (
    <section className="px-4 py-24 sm:px-6">
      <div className="mx-auto max-w-7xl">
        <Reveal>
          <SectionHeading
            eyebrow="Preview"
            title="Product screenshots"
            subtitle="A glimpse of the API documentation, gallery, and admin experience."
          />
        </Reveal>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {SCREENSHOTS.map((shot, i) => (
            <Reveal key={shot.title} delay={i * 0.08}>
              <motion.div
                className="group overflow-hidden rounded-2xl border border-white/10 bg-white/[0.02]"
                whileHover={{ y: -6 }}
                transition={{ type: 'spring', stiffness: 300 }}
              >
                <div
                  className={`relative flex aspect-video items-center justify-center bg-gradient-to-br ${shot.gradient}`}
                >
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(255,255,255,0.08),transparent)]" />
                  <div className="flex flex-col items-center gap-3 text-slate-400 transition-colors group-hover:text-slate-300">
                    <ImageIcon className="h-10 w-10 opacity-50" />
                    <span className="text-xs font-medium uppercase tracking-wider">
                      Screenshot placeholder
                    </span>
                  </div>
                </div>
                <div className="border-t border-white/5 px-5 py-4">
                  <p className="font-display font-semibold text-white">{shot.title}</p>
                </div>
              </motion.div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
