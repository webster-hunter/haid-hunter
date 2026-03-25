export interface ApiKeyStatus {
  configured: boolean
  source: 'database' | 'env' | null
  masked?: string
}

export interface ApiKeyTestResult {
  valid: boolean
  source?: string
  error?: string
  warning?: string
}

export async function getApiKeyStatus(): Promise<ApiKeyStatus> {
  const res = await fetch('/api/settings/api-key')
  if (!res.ok) throw new Error('Failed to get API key status')
  return res.json()
}

export async function setApiKey(apiKey: string): Promise<ApiKeyStatus> {
  const res = await fetch('/api/settings/api-key', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ api_key: apiKey }),
  })
  if (!res.ok) throw new Error('Failed to set API key')
  return res.json()
}

export async function deleteApiKey(): Promise<void> {
  const res = await fetch('/api/settings/api-key', { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete API key')
}

export async function testApiKey(): Promise<ApiKeyTestResult> {
  const res = await fetch('/api/settings/api-key/test', { method: 'POST' })
  if (!res.ok) throw new Error('Failed to test API key')
  return res.json()
}
