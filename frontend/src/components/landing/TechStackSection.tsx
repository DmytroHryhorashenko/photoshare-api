import { motion } from 'framer-motion'
import { TECH_STACK } from '../../constants/landing'
import { Reveal, SectionHeading } from './Reveal'

export default function TechStackSection() {
  return (
    <section className="px-4 py-24 sm:px-6">
      <div className="mx-auto max-w-5xl">
        <Reveal>
          <SectionHeading
            eyebrow="Technology"
            title="Built with modern tools"
            subtitle="Industry-standard technologies chosen for performance, maintainability, and developer experience."
          />
        </Reveal>

        <Reveal delay={0.1}>
          <div className="flex flex-wrap justify-center gap-3">
            {TECH_STACK.map((tech, i) => (
              <motion.span
                key={tech}
                className="rounded-full border border-white/10 bg-white/[0.04] px-5 py-2.5 text-sm font-medium text-slate-300 backdrop-blur transition-colors hover:border-violet-500/40 hover:bg-violet-500/10 hover:text-white"
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                whileHover={{ y: -2 }}
              >
                {tech}
              </motion.span>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  )
}
