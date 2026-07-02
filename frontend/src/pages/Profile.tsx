import { FormEvent, useState } from 'react'
import { useAuth, getErrorMessage } from '../context/AuthContext'
import { updateMe } from '../api/photos'
import ErrorAlert from '../components/ErrorAlert'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Profile() {
  const { user, refreshUser } = useAuth()
  const [username, setUsername] = useState(user?.username || '')
  const [email, setEmail] = useState(user?.email || '')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')
    try {
      const payload: { username?: string; email?: string; password?: string } =
        {}
      if (username !== user?.username) payload.username = username
      if (email !== user?.email) payload.email = email
      if (password) payload.password = password

      if (Object.keys(payload).length === 0) {
        setSuccess('No changes to save')
        return
      }

      await updateMe(payload)
      await refreshUser()
      setPassword('')
      setSuccess('Profile updated successfully')
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  if (!user) return null

  const roleBadgeColor = {
    admin: 'bg-red-500/20 text-red-300 border-red-500/30',
    moderator: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    user: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <h1 className="font-display text-3xl font-bold">Profile</h1>
      <p className="mt-1 text-slate-400">Manage your account settings</p>

      <div className="glass mt-8 p-8">
        <div className="mb-8 flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600 to-cyan-500 text-2xl font-bold">
            {user.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 className="text-xl font-semibold">{user.username}</h2>
            <p className="text-slate-400">{user.email}</p>
            <span
              className={`mt-2 inline-block rounded-full border px-3 py-0.5 text-xs font-medium capitalize ${roleBadgeColor[user.role]}`}
            >
              {user.role}
            </span>
          </div>
        </div>

        <div className="mb-6 grid grid-cols-2 gap-4 text-sm">
          <div className="rounded-xl bg-white/5 p-3">
            <span className="text-slate-500">Status</span>
            <p className="font-medium">
              {user.is_active ? 'Active' : 'Banned'}
            </p>
          </div>
          <div className="rounded-xl bg-white/5 p-3">
            <span className="text-slate-500">Member since</span>
            <p className="font-medium">
              {new Date(user.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {error && (
            <ErrorAlert message={error} onDismiss={() => setError('')} />
          )}
          {success && (
            <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">
              {success}
            </div>
          )}

          <div>
            <label htmlFor="username" className="label">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input-field"
            />
          </div>

          <div>
            <label htmlFor="email" className="label">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-field"
            />
          </div>

          <div>
            <label htmlFor="password" className="label">
              New Password (leave blank to keep current)
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              placeholder="••••••••"
              minLength={8}
            />
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? <LoadingSpinner size="sm" /> : 'Save Changes'}
          </button>
        </form>
      </div>
    </div>
  )
}
