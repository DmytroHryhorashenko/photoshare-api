import { Link } from 'react-router-dom'
import type { Photo } from '../types'

interface PhotoCardProps {
  photo: Photo
}

export default function PhotoCard({ photo }: PhotoCardProps) {
  return (
    <Link
      to={`/photos/${photo.id}`}
      className="group glass glass-hover animate-fade-in overflow-hidden"
    >
      <div className="relative aspect-square overflow-hidden">
        <img
          src={photo.image_url}
          alt={photo.description || 'Photo'}
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
        {photo.tags.length > 0 && (
          <div className="absolute bottom-0 left-0 right-0 flex flex-wrap gap-1 p-3 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
            {photo.tags.slice(0, 3).map((tag) => (
              <span
                key={tag.id}
                className="rounded-full bg-white/20 px-2 py-0.5 text-xs font-medium backdrop-blur"
              >
                #{tag.name}
              </span>
            ))}
          </div>
        )}
      </div>
      {photo.description && (
        <div className="p-4">
          <p className="line-clamp-2 text-sm text-slate-300">
            {photo.description}
          </p>
        </div>
      )}
    </Link>
  )
}
