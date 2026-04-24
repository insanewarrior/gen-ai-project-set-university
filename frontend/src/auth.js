/**
 * Cognito auth helper — Story 1.3
 *
 * CRITICAL: Tokens are stored in memory (NOT localStorage) via the custom
 * inMemoryStorage below. Sessions do NOT persist across page refreshes —
 * users must sign in again after refresh. This is an intentional trade-off
 * for JWT security per the architecture spec.
 *
 * Get UserPoolId and ClientId from CDK outputs file at
 * `infra/cdk-outputs.json` after running `make deploy`.
 */

import {
  AuthenticationDetails,
  CognitoUser,
  CognitoUserPool,
} from 'amazon-cognito-identity-js'

// ---------------------------------------------------------------------------
// In-memory storage — satisfies the Storage interface without using
// localStorage. Required per architecture spec (NFR7, AC #2).
// ---------------------------------------------------------------------------
const memoryStore = new Map()
const inMemoryStorage = {
  setItem: (key, value) => memoryStore.set(key, value),
  getItem: (key) => memoryStore.get(key) ?? null,
  removeItem: (key) => memoryStore.delete(key),
  clear: () => memoryStore.clear(),
}

// ---------------------------------------------------------------------------
// Local dev bypass — mirrors AUTH_BYPASS=true on the backend.
// Set VITE_AUTH_BYPASS=true in frontend/.env.local to skip Cognito entirely.
// getToken() returns null so api.js sends no Authorization header,
// and the backend's AUTH_BYPASS injects TEST_USER_ID automatically.
// ---------------------------------------------------------------------------
const AUTH_BYPASS = import.meta.env.VITE_AUTH_BYPASS === 'true'

const BYPASS_USER = { username: 'local-dev-user', bypassMode: true }

// ---------------------------------------------------------------------------
// User pool singleton
// ---------------------------------------------------------------------------
const poolData = {
  UserPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID ?? '',
  ClientId: import.meta.env.VITE_COGNITO_CLIENT_ID ?? '',
  Storage: inMemoryStorage,
}

let userPool = null

function initUserPool() {
  if (!userPool) {
    if (!poolData.UserPoolId || !poolData.ClientId) {
      // Env vars not configured — return null so callers can fail gracefully
      return null
    }
    userPool = new CognitoUserPool(poolData)
  }
  return userPool
}

// ---------------------------------------------------------------------------
// Sign up — creates a new Cognito account
// Returns { success: true, needsVerification: true } on success
// Returns { success: false, error: string } on failure
// ---------------------------------------------------------------------------
export function signUp(email, password) {
  return new Promise((resolve) => {
    const pool = initUserPool()
    if (!pool) {
      resolve({ success: false, error: 'Cognito not configured (check VITE_COGNITO_USER_POOL_ID)' })
      return
    }
    pool.signUp(email, password, [], null, (err) => {
      if (err) {
        resolve({ success: false, error: err.message || String(err) })
      } else {
        resolve({ success: true, needsVerification: true })
      }
    })
  })
}

// ---------------------------------------------------------------------------
// Confirm sign up — submits the verification code from email
// Returns { success: true } or { success: false, error: string }
// ---------------------------------------------------------------------------
export function confirmSignUp(email, code) {
  return new Promise((resolve) => {
    const cognitoUser = new CognitoUser({
      Username: email,
      Pool: initUserPool(),
      Storage: inMemoryStorage,
    })
    cognitoUser.confirmRegistration(code, true, (err) => {
      if (err) {
        resolve({ success: false, error: err.message || String(err) })
      } else {
        resolve({ success: true })
      }
    })
  })
}

// ---------------------------------------------------------------------------
// Sign in — authenticates with email + password via SRP
// Returns { success: true, user: CognitoUser } or { success: false, error }
// ---------------------------------------------------------------------------
export function signIn(email, password) {
  if (AUTH_BYPASS) {
    memoryStore.set('__bypass_user__', BYPASS_USER)
    return Promise.resolve({ success: true, user: BYPASS_USER })
  }
  return new Promise((resolve) => {
    const pool = initUserPool()
    if (!pool) {
      resolve({ success: false, error: 'Cognito not configured — set VITE_COGNITO_USER_POOL_ID or VITE_AUTH_BYPASS=true for local dev' })
      return
    }
    const authDetails = new AuthenticationDetails({
      Username: email,
      Password: password,
    })
    const cognitoUser = new CognitoUser({
      Username: email,
      Pool: pool,
      Storage: inMemoryStorage,
    })
    cognitoUser.authenticateUser(authDetails, {
      onSuccess: () => resolve({ success: true, user: cognitoUser }),
      onFailure: (err) =>
        resolve({ success: false, error: err.message || String(err) }),
    })
  })
}

// ---------------------------------------------------------------------------
// Sign out — clears all session state from memory
// ---------------------------------------------------------------------------
export function signOut() {
  if (AUTH_BYPASS) {
    memoryStore.delete('__bypass_user__')
    return
  }
  const pool = initUserPool()
  if (pool) {
    const cognitoUser = pool.getCurrentUser()
    if (cognitoUser) {
      cognitoUser.signOut()
    }
  }
  memoryStore.clear()
}

// ---------------------------------------------------------------------------
// getToken — returns the JWT id token for the current session, or null
// This is the token the backend expects in Authorization: Bearer <token>
// ---------------------------------------------------------------------------
export function getToken() {
  if (AUTH_BYPASS) {
    // No token needed — backend AUTH_BYPASS injects TEST_USER_ID automatically
    return Promise.resolve(null)
  }
  return new Promise((resolve) => {
    const pool = initUserPool()
    if (!pool) {
      resolve(null)
      return
    }
    const cognitoUser = pool.getCurrentUser()
    if (!cognitoUser) {
      resolve(null)
      return
    }
    cognitoUser.getSession((err, session) => {
      if (err || !session || !session.isValid()) {
        resolve(null)
      } else {
        resolve(session.getIdToken().getJwtToken())
      }
    })
  })
}

// ---------------------------------------------------------------------------
// getCurrentUser — returns the CognitoUser if a session exists, else null
// NOTE: with in-memory storage, this returns null after a page refresh.
// ---------------------------------------------------------------------------
export function getCurrentUser() {
  if (AUTH_BYPASS) {
    return memoryStore.get('__bypass_user__') ?? null
  }
  const pool = initUserPool()
  return pool ? pool.getCurrentUser() : null
}

// ---------------------------------------------------------------------------
// updateSport — stores the selected sport as a Cognito custom attribute
// Called once post-signup on the SportSelect page.
// Returns { success: true } or { success: false, error: string }
// ---------------------------------------------------------------------------
export function updateSport(cognitoUser, sport) {
  return new Promise((resolve) => {
    const attributes = [{ Name: 'custom:sport', Value: sport }]
    cognitoUser.updateAttributes(attributes, (err) => {
      if (err) {
        resolve({ success: false, error: err.message || String(err) })
      } else {
        resolve({ success: true })
      }
    })
  })
}
