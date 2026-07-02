export type UserRole = 'user' | 'moderator' | 'admin'

export interface User {
  id: number
  username: string
  email: string
  role: UserRole
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface Tag {
  id: number
  name: string
}

export interface Photo {
  id: number
  user_id: number
  description: string | null
  image_url: string
  public_id: string
  created_at: string
  updated_at: string
  tags: Tag[]
}

export interface Comment {
  id: number
  photo_id: number
  user_id: number
  text: string
  created_at: string
  updated_at: string
}

export interface RatingAverage {
  photo_id: number
  average_rating: number
  ratings_count: number
}

export interface TransformedPhoto {
  id: number
  photo_id: number
  transformation_type: string
  transformed_url: string
  qr_code_url: string | null
  created_at: string
}

export interface PhotoDetail extends Photo {
  comments: Comment[]
  rating_summary: RatingAverage | null
  transformed_photos: TransformedPhoto[]
}

export interface UserBanResponse {
  id: number
  username: string
  is_active: boolean
  message: string
}

export interface TransformRequest {
  width?: number | null
  height?: number | null
  crop?: string | null
  angle?: number | null
  effect?: string | null
  format?: string | null
}

export interface ApiError {
  detail: string | { msg: string }[]
}
