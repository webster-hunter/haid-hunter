export interface Application {
  id: number
  company: string
  position: string
  posting_url: string | null
  login_page_url: string | null
  login_email: string | null
  login_password: string | null
  status: string
  closed_reason: string | null
  has_referral: boolean
  referral_name: string | null
  notes: string | null
  created_at: string
  updated_at: string
  doc_count?: number
  documents?: LinkedDocument[]
}

export interface LinkedDocument {
  id: number
  application_id: number
  document_id: string
  role: string | null
}

export async function fetchApplications(filters?: { status?: string; search?: string; has_referral?: boolean }): Promise<Application[]> {
  const params = new URLSearchParams()
  if (filters?.status) params.set('status', filters.status)
  if (filters?.search) params.set('search', filters.search)
  if (filters?.has_referral !== undefined) params.set('has_referral', String(filters.has_referral))
  const res = await fetch(`/api/applications?${params}`)
  if (!res.ok) throw new Error('Failed to fetch applications')
  return res.json()
}

export async function fetchApplication(id: number, revealCredentials = false): Promise<Application> {
  const params = revealCredentials ? '?reveal_credentials=true' : ''
  const res = await fetch(`/api/applications/${id}${params}`)
  if (!res.ok) throw new Error('Failed to fetch application')
  return res.json()
}

export async function createApplication(data: Partial<Application>): Promise<Application> {
  const res = await fetch('/api/applications', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
  if (!res.ok) throw new Error('Failed to create application')
  return res.json()
}

export async function updateApplication(id: number, data: Partial<Application>): Promise<Application> {
  const res = await fetch(`/api/applications/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
  if (!res.ok) throw new Error('Failed to update application')
  return res.json()
}

export async function deleteApplication(id: number): Promise<void> {
  const res = await fetch(`/api/applications/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete application')
}

export async function updateApplicationStatus(id: number, status: string, closedReason?: string): Promise<Application> {
  const res = await fetch(`/api/applications/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, closed_reason: closedReason }),
  })
  if (!res.ok) throw new Error('Failed to update status')
  return res.json()
}

export async function linkDocument(appId: number, documentId: string, role?: string): Promise<LinkedDocument> {
  const res = await fetch(`/api/applications/${appId}/documents`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_id: documentId, role }),
  })
  if (!res.ok) throw new Error('Failed to link document')
  return res.json()
}

export async function fetchLinkedDocuments(appId: number): Promise<LinkedDocument[]> {
  const res = await fetch(`/api/applications/${appId}/documents`)
  if (!res.ok) throw new Error('Failed to fetch linked documents')
  return res.json()
}

export async function unlinkDocument(appId: number, linkId: number): Promise<void> {
  const res = await fetch(`/api/applications/${appId}/documents/${linkId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to unlink document')
}
