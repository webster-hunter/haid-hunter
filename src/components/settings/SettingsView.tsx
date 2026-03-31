import { useState, useEffect } from 'react'
import {
  getApiKeyStatus,
  setApiKey,
  deleteApiKey,
  testApiKey,
  type ApiKeyStatus,
} from '../../api/settings'

export default function SettingsView() {
  const [status, setStatus] = useState<ApiKeyStatus | null>(null)
  const [keyInput, setKeyInput] = useState('')
  const [testResult, setTestResult] = useState<'valid' | 'invalid' | 'warning' | null>(null)
  const [testMessage, setTestMessage] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)

  const loadStatus = async () => {
    const s = await getApiKeyStatus()
    setStatus(s)
  }

  useEffect(() => {
    loadStatus()
  }, [])

  const handleSave = async () => {
    if (!keyInput.trim()) return
    setSaving(true)
    try {
      await setApiKey(keyInput.trim())
      setKeyInput('')
      setTestResult(null)
      await loadStatus()
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    await deleteApiKey()
    setTestResult(null)
    await loadStatus()
  }

  const handleTest = async () => {
    setTesting(true)
    try {
      const result = await testApiKey()
      if (result.warning) {
        setTestResult('warning')
        setTestMessage(result.warning)
      } else if (result.valid) {
        setTestResult('valid')
        setTestMessage(null)
      } else {
        setTestResult('invalid')
        setTestMessage(result.error || null)
      }
    } finally {
      setTesting(false)
    }
  }

  return (
    <div className="settings-view">
      <h1>Settings</h1>
      <div className="settings-sections">
        <div className="settings-section">
          <h3>Claude API Key</h3>
          <p className="settings-description">
            Required for document analysis. Your key is encrypted and stored locally.
          </p>

          <div className="api-key-status">
            {status?.configured ? (
              <div className="api-key-configured">
                <span className="api-key-masked">{status.masked}</span>
                <span className="api-key-source-badge">{status.source}</span>
                {testResult === 'valid' && <span className="api-key-test-badge valid">Valid</span>}
                {testResult === 'warning' && <span className="api-key-test-badge warning">Valid (see below)</span>}
                {testResult === 'invalid' && <span className="api-key-test-badge invalid">Invalid</span>}
              </div>
            ) : (
              <span className="api-key-not-configured">Not configured</span>
            )}
          </div>

          <div className="api-key-form">
            <input
              type="password"
              placeholder="sk-ant-..."
              value={keyInput}
              onChange={e => setKeyInput(e.target.value)}
              className="api-key-input"
            />
            <button
              className="btn btn-primary"
              onClick={handleSave}
              disabled={!keyInput.trim() || saving}
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>

          <div className="api-key-actions">
            {status?.configured && (
              <>
                <button
                  className="btn btn-secondary"
                  onClick={handleTest}
                  disabled={testing}
                >
                  {testing ? 'Testing...' : 'Test Connection'}
                </button>
                {status.source === 'database' && (
                  <button className="btn btn-danger" onClick={handleDelete}>
                    Remove Key
                  </button>
                )}
              </>
            )}
          </div>

          {testMessage && (
            <p className={`api-key-message ${testResult === 'invalid' ? 'error' : 'warn'}`}>
              {testMessage}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
