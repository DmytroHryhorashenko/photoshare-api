import { api } from './client'
import type { Token, User } from '../types'

export async function register(
  username: string,
  email: string,
  password: string,
): Promise<User> {
  const { data } = await api.post<User>('/auth/register', {
    username,
    email,
    password,
  })
  return data
}

export async function login(email: string, password: string): Promise<Token> {
  const { data } = await api.post<Token>('/auth/login', { email, password })
  return data
}

export async function logout(): Promise<void> {
  await api.post('/auth/logout')
}
