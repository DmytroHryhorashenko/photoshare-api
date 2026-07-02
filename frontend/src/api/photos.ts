import { api } from './client'
import type { Photo, PhotoDetail, User, UserBanResponse } from '../types'

export interface SearchParams {
  keyword?: string
  tag?: string
  min_rating?: number
  sort_by?: 'date' | 'rating'
  order?: 'asc' | 'desc'
}

export async function searchPhotos(params: SearchParams = {}): Promise<Photo[]> {
  const { data } = await api.get<Photo[]>('/photos/search', { params })
  return data
}

export async function getPhoto(id: number): Promise<PhotoDetail> {
  const { data } = await api.get<PhotoDetail>(`/photos/${id}`)
  return data
}

export async function uploadPhoto(
  file: File,
  description: string,
  tags: string[],
): Promise<Photo> {
  const form = new FormData()
  form.append('file', file)
  if (description) form.append('description', description)
  tags.forEach((tag) => form.append('tags', tag))

  const { data } = await api.post<Photo>('/photos', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<User>('/users/me')
  return data
}

export async function updateMe(payload: {
  username?: string
  email?: string
  password?: string
}): Promise<User> {
  const { data } = await api.put<User>('/users/me', payload)
  return data
}

export async function banUser(userId: number): Promise<UserBanResponse> {
  const { data } = await api.patch<UserBanResponse>(`/users/${userId}/ban`)
  return data
}

export async function unbanUser(userId: number): Promise<UserBanResponse> {
  const { data } = await api.patch<UserBanResponse>(`/users/${userId}/unban`)
  return data
}

export async function changeUserRole(
  userId: number,
  role: string,
): Promise<User> {
  const { data } = await api.patch<User>(`/users/${userId}/role`, { role })
  return data
}
