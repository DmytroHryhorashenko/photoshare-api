import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { searchPhotos } from '../api/photos'
import { getErrorMessage } from '../api/client'
import PhotoCard from '../components/PhotoCard'
import ErrorAlert from '../components/ErrorAlert'
import LoadingSpinner from '../components/LoadingSpinner'
import type { Photo } from '../types'

export default function Gallery() {
  const [photos, setPhotos] = useState<Photo[]>([])
  const [keyword, setKeyword] = useState('')
  const [tag, setTag] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchPhotos = useCallback(async (keyword = '', tag = '') => {
    setLoading(true)
    setError('')
    try {
      const params: { keyword?: string; tag?: string } = {}
      if (keyword.trim()) params.keyword = keyword.trim()
      if (tag.trim()) params.tag = tag.trim()
      const data = await searchPhotos(params)
      setPhotos(data)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchPhotos()
  }, [fetchPhotos])

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    fetchPhotos(keyword, tag)
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold">Gallery</h1>
          <p className="mt-1 text-slate-400">
            Discover photos from the community
          </p>
        </div>

        <form onSubmit={handleSearch} className="flex flex-wrap gap-3">
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="Search keyword..."
            className="input-field w-full sm:w-48"
          />
          <input
            type="text"
            value={tag}
            onChange={(e) => setTag(e.target.value)}
            placeholder="Filter by tag..."
            className="input-field w-full sm:w-40"
          />
          <button type="submit" className="btn-primary">
            Search
          </button>
        </form>
      </div>

      {error && (
        <div className="mb-6">
          <ErrorAlert message={error} onDismiss={() => setError('')} />
        </div>
      )}

      {loading ? (
        <div className="flex min-h-[40vh] items-center justify-center">
          <LoadingSpinner size="lg" />
        </div>
      ) : photos.length === 0 ? (
        <div className="glass flex min-h-[40vh] flex-col items-center justify-center p-12 text-center">
          <div className="mb-4 text-6xl opacity-50">📷</div>
          <h2 className="font-display text-xl font-semibold">No photos yet</h2>
          <p className="mt-2 max-w-md text-slate-400">
            The gallery is empty. Be the first to share a photo!
          </p>
          <Link to="/upload" className="btn-primary mt-6">
            Upload Photo
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {photos.map((photo) => (
            <PhotoCard key={photo.id} photo={photo} />
          ))}
        </div>
      )}
    </div>
  )
}
