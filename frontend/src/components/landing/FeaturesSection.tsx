import { motion } from 'framer-motion'
import {
  Cloud,
  Container,
  Lock,
  MessageSquare,
  QrCode,
  Search,
  Shield,
  Sparkles,
  Star,
  Tag,
  Upload,
  User,
  type LucideIcon,
} from 'lucide-react'
import { FEATURES } from '../../constants/landing'
import { Reveal, SectionHeading } from './Reveal'

const iconMap: Record<string, LucideIcon> = {
  upload: Upload,
  cloud: Cloud,
  tag: Tag,
  message: MessageSquare,
  star: Star,
  qr: QrCode,
  wand: Sparkles,
  search: Search,
  user: User,
  shield: Shield,
  lock: Lock,
  container: Container,
}

export default function FeaturesSection() {
  return (
    <section id="features" className="px-4 py-24 sm:px-6">
      <div className="mx-auto max-w-7xl">
        <Reveal>
          <SectionHeading
            eyebrow="Features"
            title="Everything you need to build a photo platform"
            subtitle="A complete backend feature set with authentication, media processing, community tools, and admin controls."
          />
        </Reveal>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {FEATURES.map((feature, i) => {
            const Icon = iconMap[feature.icon]
            return (
              <Reveal key={feature.title} delay={i * 0.04}>
                <motion.div
                  className="glass glass-hover group h-full p-6"
                  whileHover={{ y: -6 }}
                  transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                >
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600/30 to-cyan-500/20 ring-1 ring-white/10 transition-all duration-300 group-hover:from-violet-600/50 group-hover:to-cyan-500/30 group-hover:shadow-lg group-hover:shadow-violet-500/20">
                    <Icon className="h-6 w-6 text-violet-300" />
                  </div>
                  <h3 className="font-display text-lg font-semibold text-white">
                    {feature.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-400">
                    {feature.description}
                  </p>
                </motion.div>
              </Reveal>
            )
          })}
        </div>
      </div>
    </section>
  )
}
