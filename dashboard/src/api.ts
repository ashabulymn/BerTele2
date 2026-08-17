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

export type SessionInfo = { id: number; name: string; api_id: number; api_hash: string; session_string?: string | null; phone_number?: string | null; bot_token?: string | null; state: string; last_error?: string | null; last_connected_at?: string | null; created_at: string; updated_at?: string | null }
export type DialogInfo = { id: number; peer: { id: number; type: string; title?: string | null; username?: string | null; first_name?: string | null; last_name?: string | null; is_bot?: boolean | null }; name?: string | null; unread_count?: number | null; folder_id?: number | null; pinned?: boolean | null; archived?: boolean | null; raw?: Record<string, unknown> }
export type MessageInfo = { id: number; dialog_id: number; sender_id?: number | null; text?: string | null; date?: string | null; out?: boolean | null; grouped_id?: number | null; reply_to_msg_id?: number | null; fwd_from?: Record<string, unknown> | null; raw?: Record<string, unknown> }
export type WebhookInfo = { id: number; name: string; url: string; is_active: boolean; created_at: string; updated_at?: string | null; event_names: string[] }
export type ApiKeyInfo = { id: number; name: string; prefix: string; user_id: number; created_at?: string | null; expires_at?: string | null; last_used_at?: string | null; is_active: boolean }
export type PluginInfo = { plugin_id?: string; id?: string; name?: string; version?: string; state?: string; started?: boolean; manifest?: Record<string, unknown>; [key: string]: unknown }
export type HealthInfo = { status: string }
export type MetaInfo = { version: string; app_name: string }

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')
const ROOT_BASE = (import.meta.env.VITE_ROOT_BASE_URL || '').replace(/\/$/, '')
const tokenKey = 'bertele2_access_token'

export const auth = { getToken: () => localStorage.getItem(tokenKey), setToken: (token: string) => localStorage.setItem(tokenKey, token), clear: () => localStorage.removeItem(tokenKey) }

async function request<T>(path: string, init: RequestInit = {}, useApiBase = true): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')
  const token = auth.getToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const prefix = useApiBase ? API_BASE : ''
  const response = await fetch(`${ROOT_BASE}${prefix}${path}`, { ...init, headers })
  if (!response.ok) {
    if (response.status === 401) auth.clear()
    const text = await response.text().catch(() => '')
    throw new Error(text || `${response.status} ${response.statusText}`)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export async function login(username: string, password: string) {
  const response = await fetch(`${ROOT_BASE}${API_BASE}/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify({ username, password }) })
  if (!response.ok) throw new Error('Invalid username or password')
  const data = await response.json(); auth.setToken(data.access_token); return data
}

export const dashboardApi = { overview: () => request<DashboardOverview>('/dashboard/overview', {}, false), logs: () => request<DashboardLogs>('/dashboard/logs', {}, false), metrics: () => request<DashboardMetrics>('/dashboard/metrics', {}, false) }

export const moduleApi = {
  sessions: {
    list: () => request<{ items: SessionInfo[] }>('/sessions'),
    create: (payload: { name: string; api_id: number; api_hash: string; session_string?: string; phone_number?: string; bot_token?: string }) => request<SessionInfo>('/sessions', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
    connect: (id: number) => request<SessionInfo>(`/sessions/${id}/connect`, { method: 'POST' }),
    disconnect: (id: number) => request<SessionInfo>(`/sessions/${id}/disconnect`, { method: 'POST' }),
    reconnect: (id: number) => request<SessionInfo>(`/sessions/${id}/reconnect`, { method: 'POST' }),
    remove: (id: number) => request<void>(`/sessions/${id}`, { method: 'DELETE' }),
  },
  dialogs: { list: (limit = 50, offset = 0) => request<{ items: DialogInfo[]; total: number; limit: number; offset: number }>(`/dialogs?limit=${limit}&offset=${offset}`), messages: (id: number, limit = 50, offset = 0) => request<{ items: MessageInfo[]; total: number; limit: number; offset: number }>(`/dialogs/${id}/messages?limit=${limit}&offset=${offset}`) },
  messages: {
    send: (peer: string, message: string) => request<{ message_id: number; peer: string }>('/messages/send', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ peer, message }) }),
    forward: (from_peer: string, to_peer: string, message_ids: number[]) => request<{ message_ids: number[]; from_peer: string; to_peer: string }>('/messages/forward', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ from_peer, to_peer, message_ids }) }),
  },
  webhooks: {
    list: () => request<{ items: WebhookInfo[] }>('/webhooks'),
    create: (payload: { name: string; url: string; secret: string; is_active: boolean; event_names: string[] }) => request<WebhookInfo>('/webhooks', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
    update: (id: number, payload: Partial<{ name: string; url: string; secret: string; is_active: boolean; event_names: string[] }>) => request<WebhookInfo>(`/webhooks/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
    remove: (id: number) => request<void>(`/webhooks/${id}`, { method: 'DELETE' }),
  },
  apiKeys: {
    list: () => request<ApiKeyInfo[]>('/apikeys'),
    create: (name: string, expires_in_days?: number) => request<ApiKeyInfo & { key: string }>('/apikeys', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, expires_in_days }) }),
    remove: (id: number) => request<{ status: string; id: string }>(`/apikeys/${id}`, { method: 'DELETE' }),
  },
  plugins: { list: () => request<{ items: PluginInfo[] }>('/plugins'), start: (id: string) => request<PluginInfo>(`/plugins/${encodeURIComponent(id)}/start`, { method: 'POST' }), stop: (id: string) => request<PluginInfo>(`/plugins/${encodeURIComponent(id)}/stop`, { method: 'POST' }), reload: (id: string) => request<PluginInfo>(`/plugins/${encodeURIComponent(id)}/reload`, { method: 'POST' }) },
  health: () => request<HealthInfo>('/health'),
  meta: () => request<MetaInfo>('/meta'),
}

export function dashboardWsUrl() {
  const base = ROOT_BASE || window.location.origin
  const url = new URL('/dashboard/ws', base)
  const token = auth.getToken(); if (token) url.searchParams.set('token', token)
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
  return url.toString()
}
