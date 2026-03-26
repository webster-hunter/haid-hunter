export default function SettingsView() {
  return (
    <div className="settings-view">
      <h1>Settings</h1>
      <div className="settings-sections">
        <div className="settings-section">
          <h3>Claude Integration</h3>
          <p className="settings-description">
            hAId-hunter uses your Claude Code subscription for AI features.
            No separate API key required.
          </p>
          <div className="api-key-status">
            <span className="api-key-configured">
              <span className="api-key-test-badge valid">Connected via Claude Code</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
