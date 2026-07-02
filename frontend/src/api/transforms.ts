import { api } from './client'
import type { TransformRequest, TransformedPhoto } from '../types'

export async function createTransform(
  photoId: number,
  payload: TransformRequest,
): Promise<TransformedPhoto> {
  const { data } = await api.post<TransformedPhoto>(
    `/photos/${photoId}/transform`,
    payload,
  )
  return data
}

export async function getTransforms(
  photoId: number,
): Promise<TransformedPhoto[]> {
  const { data } = await api.get<TransformedPhoto[]>(
    `/photos/${photoId}/transforms`,
  )
  return data
}
