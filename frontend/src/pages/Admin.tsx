import { FormEvent, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth, getErrorMessage } from '../context/AuthContext'
import {
  banUser,
  unbanUser,
  changeUserRole,
} from '../api/photos'
import ErrorAlert from '../components/ErrorAlert'
import LoadingSpinner from '../components/LoadingSpinner'
import type { UserBanResponse, User } from '../types'

export default function Admin() {
  const { user } = useAuth()
  const [userId, setUserId] = useState('')
  const [role, setRole] = useState('user')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<string>('')

  if (user?.role !== 'admin') {
    return <Navigate to="/" replace />
  }

  async function handleBan(e: FormEvent) {
    e.preventDefault()
    if (!userId) return
    setLoading(true)
    setError('')
    setResult('')
    try {
      const res: UserBanResponse = await banUser(Number(userId))
      setResult(res.message)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  async function handleUnban(e: FormEvent) {
    e.preventDefault()
    if (!userId) return
    setLoading(true)
    setError('')
    setResult('')
    try {
      const res: UserBanResponse = await unbanUser(Number(userId))
      setResult(res.message)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  async function handleRoleChange(e: FormEvent) {
    e.preventDefault()
    if (!userId) return
    setLoading(true)
    setError('')
    setResult('')
    try {
      const res: User = await changeUserRole(Number(userId), role)
      setResult(`Role changed to ${res.role} for user ${res.username}`)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <h1 className="font-display text-3xl font-bold">Admin Panel</h1>
      <p className="mt-1 text-slate-400">
        Manage users — ban, unban, and change roles
      </p>

      <div className="glass mt-8 space-y-6 p-8">
        {error && (
          <ErrorAlert message={error} onDismiss={() => setError('')} />
        )}
        {result && (
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">
            {result}
          </div>
        )}

        <div>
          <label htmlFor="userId" className="label">
            User ID
          </label>
          <input
            id="userId"
            type="number"
            min={1}
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="input-field"
            placeholder="Enter user ID"
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <form onSubmit={handleBan}>
            <button
              type="submit"
              disabled={loading || !userId}
              className="btn-secondary w-full border-red-500/30 text-red-300 hover:bg-red-500/10"
            >
              {loading ? <LoadingSpinner size="sm" /> : 'Ban User'}
            </button>
          </form>

          <form onSubmit={handleUnban}>
            <button
              type="submit"
              disabled={loading || !userId}
              className="btn-secondary w-full border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/10"
            >
              {loading ? <LoadingSpinner size="sm" /> : 'Unban User'}
            </button>
          </form>
        </div>

        <form onSubmit={handleRoleChange} className="space-y-4 border-t border-white/10 pt-6">
          <div>
            <label htmlFor="role" className="label">
              New Role
            </label>
            <select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="input-field"
            >
              <option value="user">User</option>
              <option value="moderator">Moderator</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <button
            type="submit"
            disabled={loading || !userId}
            className="btn-primary w-full"
          >
            {loading ? <LoadingSpinner size="sm" /> : 'Change Role'}
          </button>
        </form>
      </div>
    </div>
  )
}
