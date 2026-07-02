import { Outlet, useLocation } from 'react-router-dom'
import Navbar from './Navbar'

export default function Layout() {
  const location = useLocation()
  const isLanding = location.pathname === '/'

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      {!isLanding && (
        <footer className="border-t border-white/5 py-6 text-center text-sm text-slate-500">
          PhotoShare — REST API with optional visual demo
        </footer>
      )}
    </div>
  )
}
