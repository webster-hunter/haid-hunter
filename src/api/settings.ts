export interface Setting {
  key: string
  value: string
}

export async function getSetting(key: string): Promise<Setting> {
  const res = await fetch(`/api/settings/${key}`)
  if (!res.ok) throw new Error('Setting not found')
  return res.json()
}

export async function putSetting(key: string, value: string): Promise<Setting> {
  const res = await fetch(`/api/settings/${key}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ value }),
  })
  if (!res.ok) throw new Error('Failed to save setting')
  return res.json()
}
