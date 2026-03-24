export interface Experience { company: string; role: string; start_date: string; end_date: string | null; accomplishments: string[] }
export interface Education { institution: string; degree: string; field?: string; start_date: string; end_date: string | null; details: string[] }
export interface Certification { name: string; issuer: string; date: string }

export interface Profile {
  summary: string
  skills: string[]
  experience: Experience[]
  education: Education[]
  certifications: Certification[]
  objectives: string[]
}

export async function fetchProfile(): Promise<Profile> {
  const res = await fetch('/api/profile')
  if (!res.ok) throw new Error('Failed to fetch profile')
  return res.json()
}

export async function putProfile(profile: Profile): Promise<Profile> {
  const res = await fetch('/api/profile', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(profile) })
  if (!res.ok) throw new Error('Failed to update profile')
  return res.json()
}

export async function patchSection(section: string, data: unknown): Promise<Profile> {
  const res = await fetch(`/api/profile/${section}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
  if (!res.ok) throw new Error('Failed to patch section')
  return res.json()
}
