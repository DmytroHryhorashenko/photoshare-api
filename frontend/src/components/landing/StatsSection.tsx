import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { STATS } from '../../constants/landing'
import { useCountUp } from '../../hooks/useCountUp'
import { Reveal } from './Reveal'

function StatCard({
  stat,
  enabled,
}: {
  stat: (typeof STATS)[number]
  enabled: boolean
}) {
  const count = useCountUp('value' in stat ? stat.value : 0, enabled)
  const display =
    'display' in stat && stat.display
      ? stat.display
      : `${count}${'suffix' in stat ? stat.suffix : ''}`

  return (
    <motion.div
      className="glass glass-hover group relative overflow-hidden p-8 text-center"
      whileHover={{ y: -4 }}
      transition={{ type: 'spring', stiffness: 300 }}
    >
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-violet-600/0 to-cyan-500/0 opacity-0 transition-opacity duration-500 group-hover:from-violet-600/10 group-hover:to-cyan-500/5 group-hover:opacity-100" />
      <p className="font-display text-4xl font-bold text-white sm:text-5xl">
        {display}
      </p>
      <p className="mt-2 text-sm font-medium text-slate-400">{stat.label}</p>
    </motion.div>
  )
}

export default function StatsSection() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section className="px-4 py-20 sm:px-6">
      <div ref={ref} className="mx-auto max-w-7xl">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-5">
          {STATS.map((stat, i) => (
            <Reveal key={stat.label} delay={i * 0.08}>
              <StatCard stat={stat} enabled={inView} />
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
