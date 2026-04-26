import { getToken, signOut } from './auth'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

export function getDevUser() {
  return localStorage.getItem('dev-user') || 'free'
}

export function setDevUser(type) {
  localStorage.setItem('dev-user', type)
}

function devHeaders() {
  if (!import.meta.env.DEV) return {}
  return { 'X-Dev-User': getDevUser() }
}

export async function apiFetch(path, options = {}, { redirectOn401 = true } = {}) {
  const url = `${BASE_URL}${path}`
  const token = await getToken()

  const headers = {
    'Content-Type': 'application/json',
    ...devHeaders(),
    ...options.headers,
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(url, { ...options, headers })

  if (response.status === 401) {
    if (redirectOn401) {
      // Token expired or invalid — sign out and redirect to login
      signOut()
      window.location.href = '/login'
    }
    throw new Error('Unauthorized')
  }

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }

  return response.json()
}

export async function getExercises(sportType = null) {
  const url = sportType ? `/exercises?sportType=${sportType}` : '/exercises'
  return apiFetch(url)
}

export async function createSession(sessionData) {
  return apiFetch('/sessions', {
    method: 'POST',
    body: JSON.stringify(sessionData),
  })
}

export async function getSessions() {
  return apiFetch('/sessions', {}, { redirectOn401: false })
}

export async function getSession(sessionId, sessionDate) {
  return apiFetch('/sessions/' + sessionId + '?session_date=' + sessionDate)
}

export async function getProfile() {
  return apiFetch('/profile')
}

export async function postQuery(queryText) {
  const url = `${BASE_URL}/query`
  const token = await getToken()
  const headers = { 'Content-Type': 'application/json', ...devHeaders() }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const response = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify({ query: queryText }),
  })
  if (response.status === 429) {
    const body = await response.json()
    throw Object.assign(new Error('RATE_LIMIT_EXCEEDED'), { code: 'RATE_LIMIT_EXCEEDED', detail: body.detail })
  }
  if (!response.ok) throw new Error('AI_UNAVAILABLE')
  return response.json()
}

export async function postAnalyze(programText) {
  const url = `${BASE_URL}/analyze`
  const token = await getToken()
  const headers = { 'Content-Type': 'application/json', ...devHeaders() }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const response = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify({ program: programText }),
  })
  if (response.status === 429) {
    const body = await response.json()
    throw Object.assign(new Error('RATE_LIMIT_EXCEEDED'), { code: 'RATE_LIMIT_EXCEEDED', detail: body.detail })
  }
  if (!response.ok) throw new Error('AI_UNAVAILABLE')
  return response.json()
}
