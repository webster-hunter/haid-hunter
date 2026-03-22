import { useState } from 'react'
import { patchSection } from '../../api/profile'
import type { Skill, Experience, Education, Certification } from '../../api/profile'

interface Props {
  section: string
  data: unknown
  onSave: () => void
  onCancel: () => void
}

export default function SectionEditor({ section, data, onSave, onCancel }: Props) {
  const [value, setValue] = useState(() => JSON.parse(JSON.stringify(data)))

  const handleSave = async () => {
    await patchSection(section, value)
    onSave()
  }

  if (section === 'summary' || section === 'objectives') {
    return (
      <div className="section-editor">
        <textarea value={value as string} onChange={e => setValue(e.target.value)} rows={4} />
        <div className="editor-actions">
          <button onClick={handleSave}>Save</button>
          <button onClick={onCancel}>Cancel</button>
        </div>
      </div>
    )
  }

  if (section === 'skills') {
    const skills = value as Skill[]
    return (
      <div className="section-editor">
        {skills.map((s, i) => (
          <div key={i} className="editor-row">
            <input value={s.name} onChange={e => { skills[i] = { ...s, name: e.target.value }; setValue([...skills]) }} placeholder="Skill name" />
            <select value={s.proficiency} onChange={e => { skills[i] = { ...s, proficiency: e.target.value }; setValue([...skills]) }}>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
              <option value="expert">Expert</option>
            </select>
            <select value={s.category} onChange={e => { skills[i] = { ...s, category: e.target.value }; setValue([...skills]) }}>
              <option value="technical">Technical</option>
              <option value="soft">Soft</option>
            </select>
            <button onClick={() => setValue(skills.filter((_, j) => j !== i))}>Remove</button>
          </div>
        ))}
        <button onClick={() => setValue([...skills, { name: '', proficiency: 'beginner', category: 'technical' }])}>+ Add Skill</button>
        <div className="editor-actions">
          <button onClick={handleSave}>Save</button>
          <button onClick={onCancel}>Cancel</button>
        </div>
      </div>
    )
  }

  if (section === 'experience') {
    const items = value as Experience[]
    return (
      <div className="section-editor">
        {items.map((item, i) => (
          <div key={i} className="editor-group">
            <input value={item.company} onChange={e => { items[i] = { ...item, company: e.target.value }; setValue([...items]) }} placeholder="Company" />
            <input value={item.role} onChange={e => { items[i] = { ...item, role: e.target.value }; setValue([...items]) }} placeholder="Role" />
            <input value={item.start_date} onChange={e => { items[i] = { ...item, start_date: e.target.value }; setValue([...items]) }} placeholder="Start (YYYY-MM)" />
            <input value={item.end_date || ''} onChange={e => { items[i] = { ...item, end_date: e.target.value || null }; setValue([...items]) }} placeholder="End (YYYY-MM or blank)" />
            {item.accomplishments.map((a, j) => (
              <div key={j} className="accomplishment-row">
                <input value={a} onChange={e => { item.accomplishments[j] = e.target.value; setValue([...items]) }} placeholder="Accomplishment" />
                <button onClick={() => { item.accomplishments.splice(j, 1); setValue([...items]) }}>x</button>
              </div>
            ))}
            <button onClick={() => { item.accomplishments.push(''); setValue([...items]) }}>+ Accomplishment</button>
            <button onClick={() => setValue(items.filter((_, j) => j !== i))}>Remove Entry</button>
          </div>
        ))}
        <button onClick={() => setValue([...items, { company: '', role: '', start_date: '', end_date: null, accomplishments: [] }])}>+ Add Experience</button>
        <div className="editor-actions">
          <button onClick={handleSave}>Save</button>
          <button onClick={onCancel}>Cancel</button>
        </div>
      </div>
    )
  }

  if (section === 'education') {
    const items = value as Education[]
    return (
      <div className="section-editor">
        {items.map((item, i) => (
          <div key={i} className="editor-group">
            <input value={item.institution} onChange={e => { items[i] = { ...item, institution: e.target.value }; setValue([...items]) }} placeholder="Institution" />
            <input value={item.degree} onChange={e => { items[i] = { ...item, degree: e.target.value }; setValue([...items]) }} placeholder="Degree" />
            <input value={item.start_date} onChange={e => { items[i] = { ...item, start_date: e.target.value }; setValue([...items]) }} placeholder="Start (YYYY-MM)" />
            <input value={item.end_date} onChange={e => { items[i] = { ...item, end_date: e.target.value }; setValue([...items]) }} placeholder="End (YYYY-MM)" />
            <button onClick={() => setValue(items.filter((_, j) => j !== i))}>Remove</button>
          </div>
        ))}
        <button onClick={() => setValue([...items, { institution: '', degree: '', start_date: '', end_date: '' }])}>+ Add Education</button>
        <div className="editor-actions">
          <button onClick={handleSave}>Save</button>
          <button onClick={onCancel}>Cancel</button>
        </div>
      </div>
    )
  }

  if (section === 'certifications') {
    const items = value as Certification[]
    return (
      <div className="section-editor">
        {items.map((item, i) => (
          <div key={i} className="editor-group">
            <input value={item.name} onChange={e => { items[i] = { ...item, name: e.target.value }; setValue([...items]) }} placeholder="Certification name" />
            <input value={item.issuer} onChange={e => { items[i] = { ...item, issuer: e.target.value }; setValue([...items]) }} placeholder="Issuer" />
            <input value={item.date} onChange={e => { items[i] = { ...item, date: e.target.value }; setValue([...items]) }} placeholder="Date (YYYY-MM)" />
            <button onClick={() => setValue(items.filter((_, j) => j !== i))}>Remove</button>
          </div>
        ))}
        <button onClick={() => setValue([...items, { name: '', issuer: '', date: '' }])}>+ Add Certification</button>
        <div className="editor-actions">
          <button onClick={handleSave}>Save</button>
          <button onClick={onCancel}>Cancel</button>
        </div>
      </div>
    )
  }

  return null
}
