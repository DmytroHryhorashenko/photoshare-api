import { motion } from 'framer-motion'
import {
  BarChart3,
  ImageIcon,
  QrCode,
  Sparkles,
  TrendingUp,
} from 'lucide-react'

const floatingCards = [
  {
    icon: ImageIcon,
    title: 'Gallery',
    value: '2.4k photos',
    position: 'left-[4%] top-[8%]',
    delay: 0,
  },
  {
    icon: QrCode,
    title: 'QR Transform',
    value: 'Live preview',
    position: 'right-[2%] top-[18%]',
    delay: 0.15,
  },
  {
    icon: TrendingUp,
    title: 'Avg. Rating',
    value: '4.8 ★',
    position: 'left-[8%] bottom-[12%]',
    delay: 0.3,
  },
  {
    icon: BarChart3,
    title: 'API Health',
    value: '99.9% uptime',
    position: 'right-[6%] bottom-[8%]',
    delay: 0.45,
  },
]

export default function HeroDashboard() {
  return (
    <div className="relative mx-auto aspect-[4/3] w-full max-w-xl">
      <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-violet-600/20 via-transparent to-cyan-500/20 blur-3xl" />

      <motion.div
        className="glass relative h-full overflow-hidden rounded-3xl border border-white/10 p-6 shadow-2xl shadow-violet-500/10"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
      >
        <div className="flex items-center justify-between border-b border-white/10 pb-4">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-rose-400/80" />
            <div className="h-3 w-3 rounded-full bg-amber-400/80" />
            <div className="h-3 w-3 rounded-full bg-emerald-400/80" />
          </div>
          <span className="text-xs font-medium text-slate-500">dashboard.photoshare</span>
        </div>

        <div className="mt-6 grid grid-cols-3 gap-3">
          {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day, i) => (
            <div
              key={day}
              className="rounded-xl border border-white/5 bg-white/[0.03] p-3"
              style={{ gridColumn: i < 3 ? 'span 1' : undefined }}
            >
              <div
                className="mb-2 h-16 rounded-lg bg-gradient-to-br from-violet-500/30 to-cyan-500/20"
                style={{ opacity: 0.4 + i * 0.1 }}
              />
              <p className="text-[10px] text-slate-500">{day}</p>
            </div>
          ))}
        </div>

        <div className="mt-4 flex items-center gap-3 rounded-2xl border border-violet-500/20 bg-violet-500/10 p-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-cyan-500">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Transform ready</p>
            <p className="text-xs text-slate-400">w800 · grayscale · QR generated</p>
          </div>
        </div>
      </motion.div>

      {floatingCards.map((card) => (
        <motion.div
          key={card.title}
          className={`glass absolute ${card.position} z-10 flex items-center gap-3 rounded-2xl px-4 py-3 shadow-xl`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 + card.delay }}
        >
          <motion.div
            className="flex items-center gap-3"
            animate={{ y: [0, -6, 0] }}
            transition={{
              duration: 4 + card.delay * 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          >
            <card.icon className="h-5 w-5 shrink-0 text-violet-400" />
            <div>
              <p className="text-xs font-semibold text-white">{card.title}</p>
              <p className="text-[10px] text-slate-400">{card.value}</p>
            </div>
          </motion.div>
        </motion.div>
      ))}
    </div>
  )
}
