export type DashboardOverview = {
  platform: string
  generated_at: string
  stats: Record<string, { total: number; connected?: number; disconnected?: number; active?: number; enabled?: number }>
  health: { status: string; uptime_seconds: number }
  cards: { label: string; value: string; trend: string }[]
  alerts: { level: string; message: string }[]
}

export type DashboardLogs = {
  items: { timestamp: string; level: string; service: string; message: string }[]
  total: number
}

export type DashboardMetrics = {
  series: { name: string; points: { time: number; value: number }[] }[]
  summary: { requests_per_minute: number; average_latency_ms: number; error_rate: number }
}

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')
const ROOT_BASE = (import.meta.env.VITE_ROOT_BASE_URL || '').replace(/\/$/, '')
const tokenKey = 'bertele2_access_token'

export const auth = {
  getToken: () => localStorage.getItem(tokenKey),
  setToken: (token: string) => localStorage.setItem(tokenKey, token),
  clear: () => localStorage.removeItem(tokenKey),
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')
  const token = auth.getToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const response = await fetch(`${ROOT_BASE}${path}`, { ...init, headers })
  if (!response.ok) {
    if (response.status === 401) auth.clear()
    throw new Error(`${response.status} ${response.statusText}`)
  }
  return response.json() as Promise<T>
}

export async function login(username: string, password: string) {
  const response = await fetch(`${ROOT_BASE}${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!response.ok) throw new Error('Invalid username or password')
  const data = await response.json()
  auth.setToken(data.access_token)
  return data
}

export const dashboardApi = {
  overview: () => request<DashboardOverview>('/dashboard/overview'),
  logs: () => request<DashboardLogs>('/dashboard/logs'),
  metrics: () => request<DashboardMetrics>('/dashboard/metrics'),
}

export function dashboardWsUrl() {
  const base = ROOT_BASE || window.location.origin
  const url = new URL('/dashboard/ws', base)
  const token = auth.getToken()
  if (token) url.searchParams.set('token', token)
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
  return url.toString()
}
