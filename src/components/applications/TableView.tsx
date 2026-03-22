import { useState } from 'react'
import type { Application } from '../../api/applications'
import StatusBadge from './StatusBadge'

interface Props {
  applications: Application[]
  onRowClick: (app: Application) => void
}

type SortKey = 'company' | 'position' | 'status' | 'created_at'

export default function TableView({ applications, onRowClick }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>('created_at')
  const [sortAsc, setSortAsc] = useState(false)

  const handleSort = (key: SortKey) => {
    if (sortKey === key) setSortAsc(!sortAsc)
    else { setSortKey(key); setSortAsc(true) }
  }

  const sorted = [...applications].sort((a, b) => {
    const av = a[sortKey] ?? ''
    const bv = b[sortKey] ?? ''
    const cmp = String(av).localeCompare(String(bv))
    return sortAsc ? cmp : -cmp
  })

  const sortIndicator = (key: SortKey) => {
    if (sortKey !== key) return null
    return sortAsc ? ' ↑' : ' ↓'
  }

  return (
    <div className="table-wrapper">
      {sorted.length === 0 ? (
        <div className="empty-state">No applications found. Add one to get started.</div>
      ) : (
        <table className="application-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('company')} className="sortable">
                Company{sortIndicator('company')}
              </th>
              <th onClick={() => handleSort('position')} className="sortable">
                Position{sortIndicator('position')}
              </th>
              <th onClick={() => handleSort('status')} className="sortable">
                Status{sortIndicator('status')}
              </th>
              <th>Referral</th>
              <th>Docs</th>
              <th onClick={() => handleSort('created_at')} className="sortable">
                Applied{sortIndicator('created_at')}
              </th>
            </tr>
          </thead>
          <tbody>
            {sorted.map(app => (
              <tr key={app.id} onClick={() => onRowClick(app)} className="table-row">
                <td>{app.company}</td>
                <td>{app.position}</td>
                <td><StatusBadge status={app.status} /></td>
                <td>{app.referral_name || '—'}</td>
                <td>{app.doc_count ?? 0}</td>
                <td>{new Date(app.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
