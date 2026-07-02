import { api } from './client'
import type { Comment } from '../types'

export async function getComments(photoId: number): Promise<Comment[]> {
  const { data } = await api.get<Comment[]>(`/photos/${photoId}/comments`)
  return data
}

export async function addComment(
  photoId: number,
  text: string,
): Promise<Comment> {
  const { data } = await api.post<Comment>(`/photos/${photoId}/comments`, {
    text,
  })
  return data
}
