import { useState } from 'react'
import { patchSection } from '../../api/profile'
import type { Experience, Education, Certification } from '../../api/profile'

interface Props {
  section: string
  data: unknown
  onSave: () => void
  onCancel: () => void
}

const DATE_PATTERN = /^\d{4}-(0[1-9]|1[0-2])$/

function sortByDate<T extends { start_date: string; end_date: string | null }>(items: T[]): T[] {
  return [...items].sort((a, b) => {
    const endA = a.end_date ?? '9999-99'
    const endB = b.end_date ?? '9999-99'
    if (endA !== endB) return endB.localeCompare(endA)
    return b.start_date.localeCompare(a.start_date)
  })
}

function sortCertsByDate(items: Certification[]): Certification[] {
  return [...items].sort((a, b) => b.date.localeCompare(a.date))
}

function Field({ label, children, error }: { label: string; children: React.ReactNode; error?: string }) {
  return (
    <div className="editor-field">
      <span className="editor-field-label">{label}</span>
      {children}
      {error && <span className="editor-field-error">{error}</span>}
    </div>
  )
}

export default function SectionEditor({ section, data, onSave, onCancel }: Props) {
  const [value, setValue] = useState(() => JSON.parse(JSON.stringify(data)))
  const [saving, setSaving] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validate = (): boolean => {
    const errs: Record<string, string> = {}

    if (section === 'experience') {
      const items = value as Experience[]
      items.forEach((item, i) => {
        if (!item.company.trim()) errs[`exp-${i}-company`] = 'Required'
        if (!item.role.trim()) errs[`exp-${i}-role`] = 'Required'
        if (item.start_date && !DATE_PATTERN.test(item.start_date)) errs[`exp-${i}-start`] = 'Use YYYY-MM'
        if (item.end_date !== null && item.end_date && !DATE_PATTERN.test(item.end_date)) errs[`exp-${i}-end`] = 'Use YYYY-MM'
      })
    }

    if (section === 'education') {
      const items = value as Education[]
      items.forEach((item, i) => {
        if (!item.institution.trim()) errs[`edu-${i}-institution`] = 'Required'
        if (!item.degree.trim()) errs[`edu-${i}-degree`] = 'Required'
        if (item.start_date && !DATE_PATTERN.test(item.start_date)) errs[`edu-${i}-start`] = 'Use YYYY-MM'
        if (item.end_date !== null && item.end_date && !DATE_PATTERN.test(item.end_date)) errs[`edu-${i}-end`] = 'Use YYYY-MM'
      })
    }

    if (section === 'certifications') {
      const items = value as Certification[]
      items.forEach((item, i) => {
        if (!item.name.trim()) errs[`cert-${i}-name`] = 'Required'
        if (item.date && !DATE_PATTERN.test(item.date)) errs[`cert-${i}-date`] = 'Use YYYY-MM'
      })
    }

    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSave = async () => {
    if (!validate()) return
    setSaving(true)
    try {
      let sorted = value
      if (section === 'experience') sorted = sortByDate(value as Experience[])
      else if (section === 'education') sorted = sortByDate(value as Education[])
      else if (section === 'certifications') sorted = sortCertsByDate(value as Certification[])
      await patchSection(section, sorted)
      onSave()
    } finally {
      setSaving(false)
    }
  }

  const actions = (
    <div className="editor-actions">
      <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
        {saving ? 'Saving...' : 'Save'}
      </button>
      <button className="btn btn-secondary" onClick={onCancel}>Cancel</button>
    </div>
  )

  if (section === 'summary') {
    return (
      <div className="section-editor">
        <Field label="Summary">
          <textarea
            value={value as string}
            onChange={e => setValue(e.target.value)}
            rows={6}
            placeholder="Write a brief summary about yourself..."
          />
        </Field>
        {actions}
      </div>
    )
  }

  if (section === 'skills') {
    const skills = value as string[]
    return (
      <div className="section-editor">
        <div className="editor-chips">
          {skills.map((s, i) => (
            <div key={i} className="editor-chip-row">
              <input
                value={s}
                onChange={e => { const next = [...skills]; next[i] = e.target.value; setValue(next) }}
                placeholder="Skill name"
                className="editor-chip-input"
              />
              <button className="editor-remove" onClick={() => setValue(skills.filter((_, j) => j !== i))}>x</button>
            </div>
          ))}
        </div>
        <button className="btn btn-secondary btn-sm" onClick={() => setValue([...skills, ''])}>+ Add Skill</button>
        {actions}
      </div>
    )
  }

  if (section === 'experience') {
    const items = value as Experience[]
    return (
      <div className="section-editor">
        {items.map((item, i) => (
          <div key={i} className="editor-group">
            <button className="editor-group-remove" onClick={() => setValue(items.filter((_, j) => j !== i))}>x</button>
            <div className="editor-row">
              <Field label="Company" error={errors[`exp-${i}-company`]}>
                <input value={item.company} onChange={e => { items[i] = { ...item, company: e.target.value }; setValue([...items]) }} placeholder="Company" />
              </Field>
              <Field label="Title / Role" error={errors[`exp-${i}-role`]}>
                <input value={item.role} onChange={e => { items[i] = { ...item, role: e.target.value }; setValue([...items]) }} placeholder="Title / Role" />
              </Field>
            </div>
            <div className="editor-row">
              <Field label="Start Date" error={errors[`exp-${i}-start`]}>
                <input value={item.start_date} onChange={e => { items[i] = { ...item, start_date: e.target.value }; setValue([...items]) }} placeholder="YYYY-MM" />
              </Field>
              {item.end_date !== null ? (
                <Field label="End Date" error={errors[`exp-${i}-end`]}>
                  <input value={item.end_date || ''} onChange={e => { items[i] = { ...item, end_date: e.target.value || null }; setValue([...items]) }} placeholder="YYYY-MM" />
                </Field>
              ) : (
                <Field label="End Date">
                  <span className="editor-current-label">Present</span>
                </Field>
              )}
              <label className="editor-checkbox">
                <input
                  type="checkbox"
                  checked={item.end_date === null}
                  onChange={e => {
                    items[i] = { ...item, end_date: e.target.checked ? null : '' }
                    setValue([...items])
                  }}
                />
                Currently working here
              </label>
            </div>
            <div className="editor-sub-section">
              <span className="editor-sub-label">Accomplishments</span>
              {item.accomplishments.map((a, j) => (
                <div key={j} className="accomplishment-row">
                  <input value={a} onChange={e => { item.accomplishments[j] = e.target.value; setValue([...items]) }} placeholder="Accomplishment" />
                  <button className="editor-remove" onClick={() => { item.accomplishments.splice(j, 1); setValue([...items]) }}>x</button>
                </div>
              ))}
              <button className="btn btn-secondary btn-sm" onClick={() => { item.accomplishments.push(''); setValue([...items]) }}>+ Accomplishment</button>
            </div>
          </div>
        ))}
        <button className="btn btn-secondary btn-sm" onClick={() => setValue([...items, { company: '', role: '', start_date: '', end_date: '', accomplishments: [] }])}>+ Add Experience</button>
        {actions}
      </div>
    )
  }

  if (section === 'education') {
    const items = value as Education[]
    return (
      <div className="section-editor">
        {items.map((item, i) => (
          <div key={i} className="editor-group">
            <button className="editor-group-remove" onClick={() => setValue(items.filter((_, j) => j !== i))}>x</button>
            <div className="editor-row">
              <Field label="Institution" error={errors[`edu-${i}-institution`]}>
                <input value={item.institution} onChange={e => { items[i] = { ...item, institution: e.target.value }; setValue([...items]) }} placeholder="Institution" />
              </Field>
              <Field label="Degree" error={errors[`edu-${i}-degree`]}>
                <input value={item.degree} onChange={e => { items[i] = { ...item, degree: e.target.value }; setValue([...items]) }} placeholder="Degree" />
              </Field>
            </div>
            <div className="editor-row">
              <Field label="Field of Study">
                <input value={item.field || ''} onChange={e => { items[i] = { ...item, field: e.target.value || undefined }; setValue([...items]) }} placeholder="Field of study" />
              </Field>
            </div>
            <div className="editor-row">
              <Field label="Start Date" error={errors[`edu-${i}-start`]}>
                <input value={item.start_date} onChange={e => { items[i] = { ...item, start_date: e.target.value }; setValue([...items]) }} placeholder="YYYY-MM" />
              </Field>
              {item.end_date !== null ? (
                <Field label="End Date" error={errors[`edu-${i}-end`]}>
                  <input value={item.end_date || ''} onChange={e => { items[i] = { ...item, end_date: e.target.value || null }; setValue([...items]) }} placeholder="YYYY-MM" />
                </Field>
              ) : (
                <Field label="End Date">
                  <span className="editor-current-label">Present</span>
                </Field>
              )}
              <label className="editor-checkbox">
                <input
                  type="checkbox"
                  checked={item.end_date === null}
                  onChange={e => {
                    items[i] = { ...item, end_date: e.target.checked ? null : '' }
                    setValue([...items])
                  }}
                />
                Currently enrolled
              </label>
            </div>
            <div className="editor-sub-section">
              <span className="editor-sub-label">Details</span>
              {(item.details || []).map((d, j) => (
                <div key={j} className="accomplishment-row">
                  <input value={d} onChange={e => { const details = [...(item.details || [])]; details[j] = e.target.value; items[i] = { ...item, details }; setValue([...items]) }} placeholder="Detail" />
                  <button className="editor-remove" onClick={() => { const details = [...(item.details || [])]; details.splice(j, 1); items[i] = { ...item, details }; setValue([...items]) }}>x</button>
                </div>
              ))}
              <button className="btn btn-secondary btn-sm" onClick={() => { items[i] = { ...item, details: [...(item.details || []), ''] }; setValue([...items]) }}>+ Detail</button>
            </div>
          </div>
        ))}
        <button className="btn btn-secondary btn-sm" onClick={() => setValue([...items, { institution: '', degree: '', field: '', start_date: '', end_date: '', details: [] }])}>+ Add Education</button>
        {actions}
      </div>
    )
  }

  if (section === 'certifications') {
    const items = value as Certification[]
    return (
      <div className="section-editor">
        {items.map((item, i) => (
          <div key={i} className="editor-group">
            <button className="editor-group-remove" onClick={() => setValue(items.filter((_, j) => j !== i))}>x</button>
            <div className="editor-row">
              <Field label="Certification Name" error={errors[`cert-${i}-name`]}>
                <input value={item.name} onChange={e => { items[i] = { ...item, name: e.target.value }; setValue([...items]) }} placeholder="Certification name" />
              </Field>
              <Field label="Issuer">
                <input value={item.issuer} onChange={e => { items[i] = { ...item, issuer: e.target.value }; setValue([...items]) }} placeholder="Issuer" />
              </Field>
              <Field label="Date" error={errors[`cert-${i}-date`]}>
                <input value={item.date} onChange={e => { items[i] = { ...item, date: e.target.value }; setValue([...items]) }} placeholder="YYYY-MM" />
              </Field>
            </div>
          </div>
        ))}
        <button className="btn btn-secondary btn-sm" onClick={() => setValue([...items, { name: '', issuer: '', date: '' }])}>+ Add Certification</button>
        {actions}
      </div>
    )
  }

  if (section === 'objectives') {
    const objectives = value as string[]
    return (
      <div className="section-editor">
        {objectives.map((obj, i) => (
          <div key={i} className="editor-chip-row">
            <input
              value={obj}
              onChange={e => { const next = [...objectives]; next[i] = e.target.value; setValue(next) }}
              placeholder="Objective statement"
              className="editor-objective-input"
            />
            <button className="editor-remove" onClick={() => setValue(objectives.filter((_, j) => j !== i))}>x</button>
          </div>
        ))}
        <button className="btn btn-secondary btn-sm" onClick={() => setValue([...objectives, ''])}>+ Add Objective</button>
        {actions}
      </div>
    )
  }

  return null
}
