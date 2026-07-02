import { FormEvent, useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getPhoto } from '../api/photos'
import { addComment } from '../api/comments'
import { ratePhoto } from '../api/ratings'
import { createTransform } from '../api/transforms'
import { getErrorMessage } from '../api/client'
import { useAuth } from '../context/AuthContext'
import ErrorAlert from '../components/ErrorAlert'
import LoadingSpinner from '../components/LoadingSpinner'
import type { PhotoDetail as PhotoDetailType } from '../types'

export default function PhotoDetail() {
  const { id } = useParams<{ id: string }>()
  const { isAuthenticated, user } = useAuth()
  const [photo, setPhoto] = useState<PhotoDetailType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [commentText, setCommentText] = useState('')
  const [rating, setRating] = useState(0)
  const [actionLoading, setActionLoading] = useState(false)
  const [showTransform, setShowTransform] = useState(false)
  const [transformEffect, setTransformEffect] = useState('grayscale')
  const [transformWidth, setTransformWidth] = useState(800)

  const fetchPhoto = useCallback(async () => {
    if (!id) return
    setLoading(true)
    setError('')
    try {
      const data = await getPhoto(Number(id))
      setPhoto(data)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    fetchPhoto()
  }, [fetchPhoto])

  async function handleComment(e: FormEvent) {
    e.preventDefault()
    if (!photo || !commentText.trim()) return
    setActionLoading(true)
    setError('')
    try {
      await addComment(photo.id, commentText.trim())
      setCommentText('')
      await fetchPhoto()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setActionLoading(false)
    }
  }

  async function handleRating(value: number) {
    if (!photo) return
    setActionLoading(true)
    setError('')
    try {
      await ratePhoto(photo.id, value)
      setRating(value)
      await fetchPhoto()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setActionLoading(false)
    }
  }

  async function handleTransform() {
    if (!photo) return
    setActionLoading(true)
    setError('')
    try {
      await createTransform(photo.id, {
        width: transformWidth,
        effect: transformEffect,
        format: 'webp',
      })
      setShowTransform(false)
      await fetchPhoto()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setActionLoading(false)
    }
  }

  const canTransform =
    isAuthenticated &&
    user &&
    (user.id === photo?.user_id || user.role === 'admin')

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!photo) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-20 text-center">
        <ErrorAlert message={error || 'Photo not found'} />
        <Link to="/gallery" className="btn-primary mt-6 inline-flex">
          Back to Gallery
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <Link
        to="/gallery"
        className="mb-6 inline-flex items-center gap-1 text-sm text-slate-400 hover:text-white"
      >
        ← Back to Gallery
      </Link>

      {error && (
        <div className="mb-6">
          <ErrorAlert message={error} onDismiss={() => setError('')} />
        </div>
      )}

      <div className="grid gap-8 lg:grid-cols-2">
        <div className="glass overflow-hidden">
          <img
            src={photo.image_url}
            alt={photo.description || 'Photo'}
            className="w-full object-cover"
          />
        </div>

        <div className="space-y-6">
          {photo.description && (
            <div>
              <h1 className="font-display text-2xl font-bold">Description</h1>
              <p className="mt-2 text-slate-300">{photo.description}</p>
            </div>
          )}

          {photo.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {photo.tags.map((tag) => (
                <span
                  key={tag.id}
                  className="rounded-full border border-violet-500/30 bg-violet-500/10 px-3 py-1 text-sm text-violet-300"
                >
                  #{tag.name}
                </span>
              ))}
            </div>
          )}

          {photo.rating_summary && photo.rating_summary.ratings_count > 0 && (
            <div className="glass p-4">
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-amber-400">
                  {photo.rating_summary.average_rating.toFixed(1)}
                </span>
                <span className="text-slate-400">
                  ({photo.rating_summary.ratings_count} ratings)
                </span>
              </div>
            </div>
          )}

          {isAuthenticated && (
            <div className="glass p-4">
              <h3 className="font-semibold">Rate this photo</h3>
              <div className="mt-2 flex gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    disabled={actionLoading}
                    onClick={() => handleRating(star)}
                    className={`text-2xl transition-transform hover:scale-110 ${
                      star <= (rating || photo.rating_summary?.average_rating || 0)
                        ? 'text-amber-400'
                        : 'text-slate-600 hover:text-amber-300'
                    }`}
                  >
                    ★
                  </button>
                ))}
              </div>
            </div>
          )}

          {canTransform && (
            <div>
              {!showTransform ? (
                <button
                  onClick={() => setShowTransform(true)}
                  className="btn-secondary"
                >
                  Transform Image
                </button>
              ) : (
                <div className="glass space-y-4 p-4">
                  <h3 className="font-semibold">Apply Transformation</h3>
                  <div>
                    <label className="label">Effect</label>
                    <select
                      value={transformEffect}
                      onChange={(e) => setTransformEffect(e.target.value)}
                      className="input-field"
                    >
                      <option value="grayscale">Grayscale</option>
                      <option value="sepia">Sepia</option>
                      <option value="blur">Blur</option>
                      <option value="sharpen">Sharpen</option>
                      <option value="cartoonify">Cartoonify</option>
                    </select>
                  </div>
                  <div>
                    <label className="label">Width (px)</label>
                    <input
                      type="number"
                      value={transformWidth}
                      onChange={(e) => setTransformWidth(Number(e.target.value))}
                      className="input-field"
                      min={1}
                      max={10000}
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={handleTransform}
                      disabled={actionLoading}
                      className="btn-primary"
                    >
                      {actionLoading ? <LoadingSpinner size="sm" /> : 'Apply'}
                    </button>
                    <button
                      onClick={() => setShowTransform(false)}
                      className="btn-ghost"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {photo.transformed_photos.length > 0 && (
            <div className="space-y-4">
              <h3 className="font-display text-lg font-semibold">
                Transformations
              </h3>
              {photo.transformed_photos.map((t) => (
                <div key={t.id} className="glass p-4">
                  <p className="text-sm text-slate-400">{t.transformation_type}</p>
                  <a
                    href={t.transformed_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-2 block break-all text-sm text-cyan-400 hover:text-cyan-300"
                  >
                    {t.transformed_url}
                  </a>
                  {t.qr_code_url && (
                    <div className="mt-3">
                      <p className="mb-2 text-sm text-slate-400">QR Code</p>
                      <img
                        src={t.qr_code_url}
                        alt="QR Code"
                        className="h-32 w-32 rounded-lg border border-white/10"
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="mt-12">
        <h2 className="font-display text-xl font-bold">
          Comments ({photo.comments.length})
        </h2>

        {isAuthenticated ? (
          <form onSubmit={handleComment} className="mt-4 flex gap-3">
            <input
              type="text"
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              placeholder="Write a comment..."
              className="input-field flex-1"
              required
            />
            <button
              type="submit"
              disabled={actionLoading}
              className="btn-primary shrink-0"
            >
              Post
            </button>
          </form>
        ) : (
          <p className="mt-4 text-sm text-slate-400">
            <Link to="/login" className="text-violet-400 hover:text-violet-300">
              Login
            </Link>{' '}
            to leave a comment
          </p>
        )}

        <div className="mt-6 space-y-4">
          {photo.comments.length === 0 ? (
            <p className="text-slate-500">No comments yet. Be the first!</p>
          ) : (
            photo.comments.map((comment) => (
              <div key={comment.id} className="glass p-4">
                <p className="text-slate-200">{comment.text}</p>
                <p className="mt-2 text-xs text-slate-500">
                  {new Date(comment.created_at).toLocaleString()}
                </p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
