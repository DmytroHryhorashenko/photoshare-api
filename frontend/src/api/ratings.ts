import { api } from './client'
import type { RatingAverage } from '../types'

export async function getRatingSummary(
  photoId: number,
): Promise<RatingAverage> {
  const { data } = await api.get<RatingAverage>(`/photos/${photoId}/ratings`)
  return data
}

export async function ratePhoto(
  photoId: number,
  value: number,
): Promise<void> {
  await api.post(`/photos/${photoId}/ratings`, { value })
}
