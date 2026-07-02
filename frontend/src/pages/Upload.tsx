import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadPhoto } from '../api/photos'
import { getErrorMessage } from '../api/client'
import ErrorAlert from '../components/ErrorAlert'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Upload() {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [description, setDescription] = useState('')
  const [tagsInput, setTagsInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0]
    if (!selected) return
    setFile(selected)
    setPreview(URL.createObjectURL(selected))
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!file) {
      setError('Please select an image file')
      return
    }

    setLoading(true)
    setError('')
    try {
      const tags = tagsInput
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean)
        .slice(0, 5)

      const photo = await uploadPhoto(file, description, tags)
      navigate(`/photos/${photo.id}`)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <h1 className="font-display text-3xl font-bold">Upload Photo</h1>
      <p className="mt-1 text-slate-400">
        Share your moment with the community
      </p>

      <form onSubmit={handleSubmit} className="glass mt-8 space-y-6 p-8">
        {error && (
          <ErrorAlert message={error} onDismiss={() => setError('')} />
        )}

        <div>
          <label className="label">Image</label>
          <div className="relative">
            {preview ? (
              <div className="relative overflow-hidden rounded-xl">
                <img
                  src={preview}
                  alt="Preview"
                  className="max-h-64 w-full object-cover"
                />
                <button
                  type="button"
                  onClick={() => {
                    setFile(null)
                    setPreview(null)
                  }}
                  className="absolute right-2 top-2 rounded-lg bg-black/50 px-3 py-1 text-sm backdrop-blur hover:bg-black/70"
                >
                  Remove
                </button>
              </div>
            ) : (
              <label className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-white/15 bg-white/5 py-12 transition-colors hover:border-violet-500/40 hover:bg-white/[0.07]">
                <svg
                  className="mb-3 h-10 w-10 text-slate-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <span className="text-sm text-slate-400">
                  Click to select an image
                </span>
                <span className="mt-1 text-xs text-slate-500">
                  JPEG, PNG, GIF, WebP
                </span>
                <input
                  type="file"
                  accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
            )}
          </div>
        </div>

        <div>
          <label htmlFor="description" className="label">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            maxLength={2000}
            className="input-field resize-none"
            placeholder="What's this photo about?"
          />
        </div>

        <div>
          <label htmlFor="tags" className="label">
            Tags (comma-separated, max 5)
          </label>
          <input
            id="tags"
            type="text"
            value={tagsInput}
            onChange={(e) => setTagsInput(e.target.value)}
            className="input-field"
            placeholder="nature, sunset, travel"
          />
        </div>

        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? <LoadingSpinner size="sm" /> : 'Upload Photo'}
        </button>
      </form>
    </div>
  )
}
