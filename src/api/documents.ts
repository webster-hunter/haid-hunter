export interface DocumentMeta {
  id: string
  original_name: string
  stored_name: string
  display_name: string
  tags: string[]
  uploaded_at: string
  size_bytes: number
  mime_type: string
}

export async function fetchDocuments(tag?: string, search?: string): Promise<DocumentMeta[]> {
  const params = new URLSearchParams()
  if (tag) params.set('tag', tag)
  if (search) params.set('search', search)
  const res = await fetch(`/api/documents?${params}`)
  if (!res.ok) throw new Error('Failed to fetch documents')
  return res.json()
}

export async function fetchDocument(id: string): Promise<DocumentMeta> {
  const res = await fetch(`/api/documents/${id}`)
  if (!res.ok) throw new Error('Failed to fetch document')
  return res.json()
}

export async function uploadDocuments(files: File[], tags?: string[]): Promise<DocumentMeta[]> {
  const formData = new FormData()
  files.forEach(f => formData.append('files', f))
  if (tags?.length) formData.append('tags', tags.join(','))
  const res = await fetch('/api/documents/upload', { method: 'POST', body: formData })
  if (!res.ok) throw new Error('Failed to upload')
  return res.json()
}

export async function updateDocument(id: string, data: { display_name?: string; tags?: string[] }): Promise<DocumentMeta> {
  const res = await fetch(`/api/documents/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Failed to update document')
  return res.json()
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`/api/documents/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete document')
}

export async function syncDocuments(): Promise<{ added: string[]; removed: string[] }> {
  const res = await fetch('/api/documents/sync', { method: 'POST' })
  if (!res.ok) throw new Error('Failed to sync')
  return res.json()
}

export function getContentUrl(id: string): string {
  return `/api/documents/${id}/content`
}
