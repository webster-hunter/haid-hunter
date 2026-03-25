import { useState, useEffect } from 'react'
import type { Application, LinkedDocument } from '../../api/applications'
import {
  createApplication,
  updateApplication,
  deleteApplication,
  fetchLinkedDocuments,
} from '../../api/applications'
import DocumentLinker from './DocumentLinker'

interface Props {
  application: Application | null
  onClose: () => void
}

const DEFAULT_STATUS = 'bookmarked'

export default function ApplicationModal({ application, onClose }: Props) {
  const isEdit = application !== null

  const [company, setCompany] = useState(application?.company ?? '')
  const [position, setPosition] = useState(application?.position ?? '')
  const [postingUrl, setPostingUrl] = useState(application?.posting_url ?? '')
  const [loginPageUrl, setLoginPageUrl] = useState(application?.login_page_url ?? '')
  const [loginEmail, setLoginEmail] = useState(application?.login_email ?? '')
  const [loginPassword, setLoginPassword] = useState(application?.login_password ?? '')
  const [showPassword, setShowPassword] = useState(false)
  const [status, setStatus] = useState(application?.status ?? DEFAULT_STATUS)
  const [closedReason, setClosedReason] = useState(application?.closed_reason ?? '')
  const [hasReferral, setHasReferral] = useState(application?.has_referral ?? false)
  const [referralName, setReferralName] = useState(application?.referral_name ?? '')
  const [notes, setNotes] = useState(application?.notes ?? '')
  const [linkedDocs, setLinkedDocs] = useState<LinkedDocument[]>([])
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isEdit && application.id) {
      fetchLinkedDocuments(application.id)
        .then(setLinkedDocs)
        .catch(err => console.error('Failed to load linked docs:', err))
    }
  }, [isEdit, application?.id])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    const data: Partial<Application> = {
      company,
      position,
      posting_url: postingUrl || null,
      login_page_url: loginPageUrl || null,
      login_email: loginEmail || null,
      login_password: loginPassword || null,
      status,
      closed_reason: status === 'closed' ? closedReason || null : null,
      has_referral: hasReferral,
      referral_name: hasReferral ? referralName || null : null,
      notes: notes || null,
    }
    try {
      if (isEdit) {
        await updateApplication(application.id, data)
      } else {
        await createApplication(data)
      }
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!isEdit) return
    if (!window.confirm(`Delete application for ${application.company}?`)) return
    setDeleting(true)
    try {
      await deleteApplication(application.id)
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete')
    } finally {
      setDeleting(false)
    }
  }

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) onClose()
  }

  return (
    <div className="modal-overlay" onClick={handleOverlayClick} role="dialog" aria-modal="true">
      <div className="modal-content">
        <div className="modal-header">
          <h2>{isEdit ? 'Edit Application' : 'Add Application'}</h2>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Close">×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && <div className="modal-error">{error}</div>}

            <div className="modal-section">
              <div className="form-row">
                <div className="form-field">
                  <label className="form-label" htmlFor="company">Company *</label>
                  <input
                    id="company"
                    type="text"
                    className="form-input"
                    value={company}
                    onChange={e => setCompany(e.target.value)}
                    required
                    placeholder="Acme Corp"
                  />
                </div>
                <div className="form-field">
                  <label className="form-label" htmlFor="position">Position *</label>
                  <input
                    id="position"
                    type="text"
                    className="form-input"
                    value={position}
                    onChange={e => setPosition(e.target.value)}
                    required
                    placeholder="Software Engineer"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-field">
                  <label className="form-label" htmlFor="status">Status</label>
                  <select
                    id="status"
                    className="form-input"
                    value={status}
                    onChange={e => setStatus(e.target.value)}
                  >
                    <option value="bookmarked">Bookmarked</option>
                    <option value="applied">Applied</option>
                    <option value="in_progress">In Progress</option>
                    <option value="interviewing">Interviewing</option>
                    <option value="offer">Offer</option>
                    <option value="rejected">Rejected</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>
                {status === 'closed' && (
                  <div className="form-field">
                    <label className="form-label" htmlFor="closed-reason">Closed Reason</label>
                    <input
                      id="closed-reason"
                      type="text"
                      className="form-input"
                      value={closedReason}
                      onChange={e => setClosedReason(e.target.value)}
                      placeholder="Rejected, withdrew, ghosted..."
                    />
                  </div>
                )}
              </div>
            </div>

            <div className="modal-section">
              <div className="form-field">
                <label className="form-label" htmlFor="posting-url">Job Posting URL</label>
                <input
                  id="posting-url"
                  type="url"
                  className="form-input"
                  value={postingUrl}
                  onChange={e => setPostingUrl(e.target.value)}
                  placeholder="https://..."
                />
              </div>
            </div>

            <div className="modal-section">
              <div className="modal-section-title">Applicant Portal</div>
              <div className="form-field">
                <label className="form-label" htmlFor="login-page">Login Page URL</label>
                <input
                  id="login-page"
                  type="url"
                  className="form-input"
                  value={loginPageUrl}
                  onChange={e => setLoginPageUrl(e.target.value)}
                  placeholder="https://..."
                />
              </div>
              <div className="form-row">
                <div className="form-field">
                  <label className="form-label" htmlFor="login-email">Email / Username</label>
                  <input
                    id="login-email"
                    type="text"
                    className="form-input"
                    value={loginEmail}
                    onChange={e => setLoginEmail(e.target.value)}
                    placeholder="you@example.com"
                    autoComplete="off"
                  />
                </div>
                <div className="form-field">
                  <label className="form-label" htmlFor="login-password">Password</label>
                  <div className="password-field">
                    <input
                      id="login-password"
                      type={showPassword ? 'text' : 'password'}
                      className="form-input"
                      value={loginPassword}
                      onChange={e => setLoginPassword(e.target.value)}
                      autoComplete="new-password"
                    />
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm password-toggle"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? 'Hide' : 'Show'}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-section">
              <div className="form-field referral-toggle">
                <label className="referral-label">
                  <input
                    type="checkbox"
                    checked={hasReferral}
                    onChange={e => setHasReferral(e.target.checked)}
                  />
                  <span>Has Referral</span>
                </label>
              </div>
              {hasReferral && (
                <div className="form-field">
                  <label className="form-label" htmlFor="referral-name">Referral Name</label>
                  <input
                    id="referral-name"
                    type="text"
                    className="form-input"
                    value={referralName}
                    onChange={e => setReferralName(e.target.value)}
                    placeholder="Jane Doe"
                  />
                </div>
              )}
            </div>

            <div className="modal-section">
              <div className="form-field">
                <label className="form-label" htmlFor="notes">Notes</label>
                <textarea
                  id="notes"
                  className="form-input modal-textarea"
                  value={notes}
                  onChange={e => setNotes(e.target.value)}
                  rows={4}
                  placeholder="Interview notes, contacts, deadlines..."
                />
              </div>
            </div>

            {isEdit && (
              <div className="modal-section">
                <DocumentLinker
                  appId={application.id}
                  linkedDocs={linkedDocs}
                  onUpdate={setLinkedDocs}
                />
              </div>
            )}
          </div>

          <div className="modal-footer">
            {isEdit && (
              <button
                type="button"
                className="btn btn-danger"
                onClick={handleDelete}
                disabled={deleting || saving}
              >
                {deleting ? 'Deleting...' : 'Delete'}
              </button>
            )}
            <div className="modal-footer-right">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={onClose}
                disabled={saving}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={saving || !company || !position}
              >
                {saving ? 'Saving...' : isEdit ? 'Save Changes' : 'Add Application'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
