const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'
let accessToken = localStorage.getItem('bertele2_access_token') || ''
let refreshToken = localStorage.getItem('bertele2_refresh_token') || ''
export function setTokens(access: string, refresh: string) { accessToken = access; refreshToken = refresh; localStorage.setItem('bertele2_access_token', access); localStorage.setItem('bertele2_refresh_token', refresh) }
export function clearTokens() { accessToken = ''; refreshToken = ''; localStorage.removeItem('bertele2_access_token'); localStorage.removeItem('bertele2_refresh_token') }
export function hasToken() { return Boolean(accessToken) }
async function refresh() { if (!refreshToken) return false; const response = await fetch(`${API_BASE}/auth/refresh`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ refresh_token: refreshToken }) }); if (!response.ok) return false; const data = await response.json(); setTokens(data.access_token, data.refresh_token); return true }
export async function api<T>(path: string, options: RequestInit = {}, retry = true): Promise<T> { const headers = new Headers(options.headers); headers.set('Accept', 'application/json'); if (options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json'); if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`); const response = await fetch(`${API_BASE}${path}`, { ...options, headers }); if (response.status === 401 && retry && await refresh()) return api<T>(path, options, false); if (!response.ok) { let message = `Request failed (${response.status})`; try { const body = await response.json(); message = body.detail || message } catch { /* non-json */ } throw new Error(message) } if (response.status === 204) return undefined as T; return response.json() as Promise<T> }
export async function login(username: string, password: string) { const data = await api<{ access_token: string; refresh_token: string; user: User }>('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }, false); setTokens(data.access_token, data.refresh_token); return data.user }
export type User = { id: number; username: string; email?: string; full_name?: string; roles: string[]; is_active: boolean; is_superuser: boolean }
export type DialogPeer = { id: number; type: string; title?: string; username?: string; first_name?: string; last_name?: string; is_bot?: boolean }
export type Dialog = { id: number; peer: DialogPeer; name?: string; unread_count?: number; folder_id?: number; pinned?: boolean; archived?: boolean; raw: Record<string, unknown> }
export type Message = { id: number; dialog_id: number; sender_id?: number; text?: string; date?: string; out?: boolean; grouped_id?: number; reply_to_msg_id?: number; fwd_from?: Record<string, unknown>; raw: Record<string, unknown> }
export type Webhook = { id: number; name: string; url: string; is_active: boolean; created_at: string; updated_at?: string; event_names: string[] }
export type Session = { id: number; name: string; api_id: number; api_hash: string; session_string?: string; phone_number?: string; bot_token?: string; state: string; last_error?: string; last_connected_at?: string; created_at: string; updated_at?: string }
export type ApiKey = { id: number; name: string; prefix: string; user_id: number; created_at?: string; expires_at?: string; last_used_at?: string; is_active: boolean }
export const getDialogs = (limit = 50) => api<{ items: Dialog[]; total: number; limit: number; offset: number }>(`/dialogs?limit=${limit}`)
export const getMessages = (dialogId: number, limit = 100) => api<{ items: Message[]; total: number; limit: number; offset: number }>(`/dialogs/${dialogId}/messages?limit=${limit}`)
export const sendMessage = (peer: string, message: string) => api<{ message_id: number; peer: string }>('/messages/send', { method: 'POST', body: JSON.stringify({ peer, message }) })
export const forwardMessages = (from_peer: string, to_peer: string, message_ids: number[]) => api<{ message_ids: number[]; from_peer: string; to_peer: string }>('/messages/forward', { method: 'POST', body: JSON.stringify({ from_peer, to_peer, message_ids }) })
export const getWebhooks = () => api<{ items: Webhook[] }>('/webhooks')
export const createWebhook = (payload: Omit<Webhook, 'id' | 'created_at' | 'updated_at'>) => api<Webhook>('/webhooks', { method: 'POST', body: JSON.stringify(payload) })
export const updateWebhook = (id: number, payload: Partial<Omit<Webhook, 'id' | 'created_at' | 'updated_at'>>) => api<Webhook>(`/webhooks/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
export const deleteWebhook = (id: number) => api<void>(`/webhooks/${id}`, { method: 'DELETE' })
export const getSessions = () => api<{ items: Session[] }>('/sessions')
export const createSession = (payload: { name: string; api_id: number; api_hash: string; session_string?: string; phone_number?: string; bot_token?: string }) => api<Session>('/sessions', { method: 'POST', body: JSON.stringify(payload) })
export const sessionAction = (id: number, action: 'connect' | 'disconnect' | 'reconnect') => api<Session>(`/sessions/${id}/${action}`, { method: 'POST' })
export const deleteSession = (id: number) => api<void>(`/sessions/${id}`, { method: 'DELETE' })
export const getApiKeys = () => api<ApiKey[]>('/apikeys')
export const createApiKey = (name: string, expires_in_days?: number) => api<ApiKey & { key: string }>('/apikeys', { method: 'POST', body: JSON.stringify({ name, expires_in_days }) })
export const deleteApiKey = (id: number) => api<{ status: string; id: string }>(`/apikeys/${id}`, { method: 'DELETE' })
