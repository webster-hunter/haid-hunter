2# hAId-hunter Phase I Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the three core features of hAId-hunter — Document Manager, Profile View, and Application Manager — as a React SPA with a FastAPI backend.

**Architecture:** Single React SPA (Vite + TypeScript + React Router) with lazy-loaded routes. FastAPI Python backend serving REST endpoints. Documents stored on local filesystem with JSON metadata. Profile stored as JSON. Applications stored in SQLite. All features share one backend server with CORS for the Vite dev server.

**Tech Stack:** React 19, TypeScript 5.9, Vite 8, React Router, Vitest + React Testing Library (frontend tests), FastAPI, pytest + httpx (backend tests), SQLite (via sqlite3), cryptography (Fernet encryption), python-multipart (file uploads), Anthropic Python SDK (Claude API).

**Specs:**
- `docs/superpowers/specs/2026-03-21-document-manager-design.md`
- `docs/superpowers/specs/2026-03-21-profile-view-design.md`
- `docs/superpowers/specs/2026-03-21-application-manager-design.md`

**Design system:** `docs/style/style-guide.md`

---

## File Structure

### Backend (`backend/`)

```
backend/
├── requirements.txt
├── main.py                    # FastAPI app entry point, CORS, startup events
├── config.py                  # Settings (paths, encryption key, allowed MIME types)
├── services/
│   ├── metadata.py            # Document metadata read/write/sync
│   ├── profile.py             # Profile JSON read/write/patch
│   ├── interview.py           # Interview session management + Claude API
│   ├── encryption.py          # Fernet encrypt/decrypt for credentials
│   └── database.py            # SQLite connection + schema init
├── routers/
│   ├── documents.py           # /api/documents/* endpoints
│   ├── tags.py                # /api/tags/* endpoints
│   ├── profile.py             # /api/profile/* endpoints
│   ├── interview.py           # /api/interview/* endpoints
│   └── applications.py        # /api/applications/* endpoints
└── tests/
    ├── conftest.py            # Shared fixtures (tmp dirs, test client)
    ├── test_metadata.py       # Metadata service unit tests
    ├── test_documents_api.py  # Document endpoint integration tests
    ├── test_tags_api.py       # Tag endpoint integration tests
    ├── test_profile_service.py # Profile service unit tests
    ├── test_profile_api.py    # Profile endpoint integration tests
    ├── test_interview_api.py  # Interview endpoint integration tests
    ├── test_encryption.py     # Encryption service unit tests
    ├── test_database.py       # Database service unit tests
    └── test_applications_api.py # Application endpoint integration tests
```

### Frontend (`src/`)

```
src/
├── main.tsx                   # Entry point (existing, modify for Router)
├── App.tsx                    # Root with RouterProvider (replace existing)
├── index.css                  # Global styles with design system tokens (replace)
├── api/
│   ├── documents.ts           # Document API client functions
│   ├── tags.ts                # Tag API client functions
│   ├── profile.ts             # Profile API client functions
│   ├── interview.ts           # Interview API client functions
│   └── applications.ts        # Application API client functions
├── components/
│   ├── shared/
│   │   ├── TagBadge.tsx       # Reusable tag pill
│   │   ├── StatusBadge.tsx    # Reusable status pill (app manager)
│   │   └── NavBar.tsx         # Top navigation bar
│   ├── documents/
│   │   ├── DocumentManager.tsx # Top-level layout
│   │   ├── TagSidebar.tsx     # Tag filter sidebar
│   │   ├── DocumentToolbar.tsx # Search + upload + sync
│   │   ├── DropZone.tsx       # Drag-and-drop upload area
│   │   ├── DocumentList.tsx   # Scrollable file list
│   │   ├── DocumentItem.tsx   # Single file row
│   │   └── DocumentPreview.tsx # Right panel preview
│   ├── profile/
│   │   ├── ProfileView.tsx    # Top-level split-pane layout
│   │   ├── ProfilePanel.tsx   # Scrollable profile sections
│   │   ├── ProfileSection.tsx # Section wrapper with edit toggle
│   │   ├── SkillChips.tsx     # Skills display
│   │   ├── ExperienceList.tsx # Experience display
│   │   ├── EducationList.tsx  # Education display
│   │   ├── CertificationList.tsx # Certifications display
│   │   ├── SectionEditor.tsx  # Inline section editor
│   │   ├── InterviewChat.tsx  # Chat panel
│   │   ├── ChatMessage.tsx    # Message bubble
│   │   └── SuggestionCard.tsx # Suggestion with accept/reject
│   └── applications/
│       ├── ApplicationManager.tsx # Top-level with view toggle
│       ├── ApplicationToolbar.tsx # Search + filter + add
│       ├── TableView.tsx      # Table rendering
│       ├── KanbanView.tsx     # Kanban board
│       ├── KanbanColumn.tsx   # Single status column
│       ├── KanbanCard.tsx     # Draggable application card
│       ├── ApplicationModal.tsx # Add/edit form modal
│       ├── DocumentLinker.tsx # Linked docs in modal
│       ├── DocumentPicker.tsx # Document selection dropdown
│       └── StatusBadge.tsx    # Status-specific badge colors
└── __tests__/
    ├── documents/
    │   ├── DocumentManager.test.tsx
    │   ├── TagSidebar.test.tsx
    │   ├── DocumentToolbar.test.tsx
    │   ├── DropZone.test.tsx
    │   ├── DocumentList.test.tsx
    │   └── DocumentPreview.test.tsx
    ├── profile/
    │   ├── ProfileView.test.tsx
    │   ├── ProfilePanel.test.tsx
    │   ├── SectionEditor.test.tsx
    │   └── InterviewChat.test.tsx
    └── applications/
        ├── ApplicationManager.test.tsx
        ├── TableView.test.tsx
        ├── KanbanView.test.tsx
        └── ApplicationModal.test.tsx
```

---

## Phase 1: Foundation

### Task 1: Initialize Git and Configure Ignores

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Initialize git repo**

Run: `git init`

- [ ] **Step 2: Create .gitignore**

```gitignore
node_modules/
dist/
documents/
data/
.env
*.pyc
__pycache__/
backend/.venv/
.vite/
```

- [ ] **Step 3: Commit**

```bash
git add .gitignore CLAUDE.md package.json tsconfig.json tsconfig.app.json tsconfig.node.json vite.config.ts eslint.config.js index.html src/ public/ docs/
git commit -m "chore: initial project structure with Vite + React scaffold"
```

---

### Task 2: Set Up Python Backend

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `backend/config.py`

- [ ] **Step 1: Create virtual environment**

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
```

- [ ] **Step 2: Create requirements.txt**

```txt
fastapi==0.115.12
uvicorn[standard]==0.34.3
python-multipart==0.0.20
httpx==0.28.1
pytest==8.3.5
pytest-asyncio==0.25.3
anthropic==0.52.0
cryptography==44.0.3
python-dotenv==1.1.0
```

- [ ] **Step 3: Install dependencies**

Run: `pip install -r requirements.txt`

- [ ] **Step 4: Create config.py**

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
DATA_DIR = PROJECT_ROOT / "data"
PROFILE_PATH = DOCUMENTS_DIR / ".profile.json"
METADATA_PATH = DOCUMENTS_DIR / ".metadata.json"
DATABASE_PATH = DATA_DIR / "applications.db"

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".xlsx", ".csv", ".pptx"}

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
```

- [ ] **Step 5: Create main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import DOCUMENTS_DIR, DATA_DIR

app = FastAPI(title="hAId-hunter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    DOCUMENTS_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 6: Verify server starts**

Run: `cd backend && uvicorn backend.main:app --reload --port 8000`
Verify: `curl http://localhost:8000/api/health` returns `{"status":"ok"}`

- [ ] **Step 7: Commit**

```bash
git add backend/requirements.txt backend/main.py backend/config.py
git commit -m "feat: add FastAPI backend with health endpoint and config"
```

---

### Task 3: Set Up Frontend Testing (Vitest + RTL)

**Files:**
- Modify: `package.json`
- Create: `vitest.config.ts`
- Create: `src/test-setup.ts`

- [ ] **Step 1: Install test dependencies**

```bash
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

- [ ] **Step 2: Create vitest.config.ts**

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test-setup.ts',
    include: ['src/**/*.test.{ts,tsx}'],
  },
})
```

- [ ] **Step 3: Create src/test-setup.ts**

```typescript
import '@testing-library/jest-dom/vitest'
```

- [ ] **Step 4: Add test script to package.json**

Add to `"scripts"`:
```json
"test": "vitest run",
"test:watch": "vitest"
```

- [ ] **Step 5: Write a smoke test to verify setup**

Create `src/__tests__/setup.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'

describe('test setup', () => {
  it('renders a component', () => {
    render(<div>Hello</div>)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
```

- [ ] **Step 6: Run test to verify it passes**

Run: `npm test`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add package.json package-lock.json vitest.config.ts src/test-setup.ts src/__tests__/setup.test.tsx
git commit -m "chore: add Vitest + React Testing Library setup"
```

---

### Task 4: Set Up Backend Testing (pytest)

**Files:**
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/pytest.ini`

- [ ] **Step 1: Create pytest.ini**

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
```

- [ ] **Step 2: Create backend/tests/__init__.py** (empty file)

- [ ] **Step 3: Create conftest.py with shared fixtures**

```python
import pytest
from pathlib import Path
from fastapi.testclient import TestClient


@pytest.fixture
def tmp_documents(tmp_path):
    """Temporary documents directory for testing."""
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    return docs_dir


@pytest.fixture
def tmp_data(tmp_path):
    """Temporary data directory for testing."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir
```

- [ ] **Step 4: Write a smoke test**

Create `backend/tests/test_health.py`:

```python
from fastapi.testclient import TestClient
from backend.main import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_health.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/tests/ backend/pytest.ini
git commit -m "chore: add pytest setup with health endpoint test"
```

---

### Task 5: React Router with Lazy Routes

**Files:**
- Modify: `src/main.tsx`
- Modify: `src/App.tsx`
- Create: `src/components/shared/NavBar.tsx`

- [ ] **Step 1: Install React Router**

Run: `npm install react-router-dom`

- [ ] **Step 2: Write failing test for router setup**

Create `src/__tests__/App.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import App from '../App'

describe('App routing', () => {
  it('renders navigation bar', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    )
    expect(screen.getByRole('navigation')).toBeInTheDocument()
  })

  it('has links to all sections', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    )
    expect(screen.getByRole('link', { name: /documents/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /profile/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /applications/i })).toBeInTheDocument()
  })
})
```

- [ ] **Step 3: Run test to verify it fails**

Run: `npm test -- src/__tests__/App.test.tsx`
Expected: FAIL — no navigation element

- [ ] **Step 4: Create NavBar component**

```typescript
// src/components/shared/NavBar.tsx
import { NavLink } from 'react-router-dom'

export function NavBar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">hAId-hunter</div>
      <div className="navbar-links">
        <NavLink to="/documents" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          Documents
        </NavLink>
        <NavLink to="/profile" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          Profile
        </NavLink>
        <NavLink to="/applications" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          Applications
        </NavLink>
      </div>
    </nav>
  )
}
```

- [ ] **Step 5: Replace App.tsx with router setup**

```typescript
// src/App.tsx
import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { NavBar } from './components/shared/NavBar'

const DocumentManager = lazy(() => import('./components/documents/DocumentManager'))
const ProfileView = lazy(() => import('./components/profile/ProfileView'))
const ApplicationManager = lazy(() => import('./components/applications/ApplicationManager'))

function App() {
  return (
    <div className="app">
      <NavBar />
      <main className="main-content">
        <Suspense fallback={<div className="loading">Loading...</div>}>
          <Routes>
            <Route path="/" element={<Navigate to="/documents" replace />} />
            <Route path="/documents" element={<DocumentManager />} />
            <Route path="/profile" element={<ProfileView />} />
            <Route path="/applications" element={<ApplicationManager />} />
          </Routes>
        </Suspense>
      </main>
    </div>
  )
}

export default App
```

- [ ] **Step 6: Update main.tsx to use BrowserRouter**

```typescript
// src/main.tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
```

- [ ] **Step 7: Create placeholder lazy components**

Create stub components that will be replaced later:

`src/components/documents/DocumentManager.tsx`:
```typescript
export default function DocumentManager() {
  return <div>Document Manager</div>
}
```

`src/components/profile/ProfileView.tsx`:
```typescript
export default function ProfileView() {
  return <div>Profile View</div>
}
```

`src/components/applications/ApplicationManager.tsx`:
```typescript
export default function ApplicationManager() {
  return <div>Application Manager</div>
}
```

- [ ] **Step 8: Run test to verify it passes**

Run: `npm test -- src/__tests__/App.test.tsx`
Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add src/main.tsx src/App.tsx src/components/ src/__tests__/App.test.tsx package.json package-lock.json
git commit -m "feat: add React Router with lazy-loaded routes and navbar"
```

---

### Task 6: Design System CSS Tokens

**Files:**
- Modify: `src/index.css`
- Delete: `src/App.css`

- [ ] **Step 1: Replace index.css with design system tokens**

Replace the entire file with CSS variables from `docs/style/style-guide.md`:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400&display=swap');

:root {
  /* Colors */
  --color-bg: #0D1117;
  --color-surface: #161B2E;
  --color-elevated: #1E2A45;
  --color-border: #2E3F5C;
  --color-muted: #6B7FA3;
  --color-text: #C8D3E8;
  --color-primary: #4A6FA5;
  --color-secondary: #7B93D4;
  --color-accent: #F59E0B;
  --color-success: #10B981;
  --color-error: #EF4444;

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  --space-3xl: 64px;

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.4);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.5);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.6);
  --shadow-glow: 0 0 16px rgba(74,111,165,0.4);

  /* Motion */
  --transition-fast: 100ms ease;
  --transition-base: 200ms ease;
  --transition-slow: 300ms ease-in-out;

  /* Typography */
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 16px;
  line-height: 1.6;
  color: var(--color-text);
  background: var(--color-bg);
  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  min-height: 100vh;
}

#root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Typography */
h1 { font-size: 32px; font-weight: 700; line-height: 1.2; }
h2 { font-size: 24px; font-weight: 600; line-height: 1.2; }
h3 { font-size: 18px; font-weight: 600; line-height: 1.2; }

/* App layout */
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: var(--space-lg);
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 50vh;
  color: var(--color-muted);
}

/* Navbar */
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) var(--space-lg);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.navbar-brand {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text);
}

.navbar-links {
  display: flex;
  gap: var(--space-sm);
}

.nav-link {
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-muted);
  transition: all var(--transition-base);
}

.nav-link:hover {
  color: var(--color-text);
  background: var(--color-elevated);
}

.nav-link.active {
  color: white;
  background: var(--color-primary);
}

/* Shared component styles */
.btn {
  padding: 10px 20px;
  border-radius: var(--radius-md);
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  font-family: inherit;
  transition: all var(--transition-base);
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background: #5a82b8;
}

.btn-secondary {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.btn-secondary:hover {
  border-color: var(--color-primary);
}

.btn-danger {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-error);
}

.btn-danger:hover {
  border-color: var(--color-error);
}

/* Form elements */
.form-input {
  background: var(--color-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  color: var(--color-text);
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: border-color var(--transition-base);
}

.form-input::placeholder {
  color: var(--color-muted);
}

.form-input:focus {
  border-color: var(--color-primary);
}

.form-label {
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-muted);
}

/* Cards */
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
}

/* Tag badge */
.tag-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  background: rgba(123, 147, 212, 0.15);
  color: var(--color-secondary);
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-muted);
}
```

- [ ] **Step 2: Delete src/App.css**

Run: `rm src/App.css`

- [ ] **Step 3: Verify dev server runs**

Run: `npm run dev`
Verify: Opens in browser, dark theme with navbar visible, no console errors.

- [ ] **Step 4: Commit**

```bash
git add src/index.css
git rm src/App.css
git commit -m "feat: replace default styles with Slate Blue design system tokens"
```

---

### Task 7: Vite Proxy Config

**Files:**
- Modify: `vite.config.ts`

- [ ] **Step 1: Add proxy for /api to backend**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 2: Commit**

```bash
git add vite.config.ts
git commit -m "chore: add Vite proxy for /api to FastAPI backend"
```

---

## Phase 2: Document Manager — Backend

### Task 8: Metadata Service

**Files:**
- Create: `backend/services/__init__.py`
- Create: `backend/services/metadata.py`
- Create: `backend/tests/test_metadata.py`

- [ ] **Step 1: Create backend/services/__init__.py** (empty file)

- [ ] **Step 2: Write failing test for metadata initialization**

```python
# backend/tests/test_metadata.py
import json
from pathlib import Path
from backend.services.metadata import MetadataService


def test_init_creates_default_metadata(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    data = service.read()
    assert data["files"] == {}
    assert set(data["tags"]) == {"resume", "cover-letter", "cv"}


def test_init_loads_existing_metadata(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    meta_path = docs_dir / ".metadata.json"
    meta_path.write_text(json.dumps({
        "files": {"abc123": {"original_name": "test.pdf", "stored_name": "abc123_test.pdf",
                             "display_name": "test.pdf", "tags": ["resume"],
                             "uploaded_at": "2026-01-01T00:00:00Z",
                             "size_bytes": 100, "mime_type": "application/pdf"}},
        "tags": ["resume", "cover-letter", "cv", "custom"]
    }))
    service = MetadataService(docs_dir)
    data = service.read()
    assert "abc123" in data["files"]
    assert "custom" in data["tags"]
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_metadata.py -v`
Expected: FAIL — module not found

- [ ] **Step 4: Implement MetadataService**

```python
# backend/services/metadata.py
import json
import uuid
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from backend.config import ALLOWED_EXTENSIONS

DEFAULT_TAGS = ["resume", "cover-letter", "cv"]


class MetadataService:
    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir
        self.meta_path = docs_dir / ".metadata.json"
        self._lock = Lock()
        self._ensure_metadata()

    def _ensure_metadata(self):
        if not self.meta_path.exists():
            self._write({"files": {}, "tags": list(DEFAULT_TAGS)})

    def read(self) -> dict:
        with self._lock:
            return json.loads(self.meta_path.read_text())

    def _write(self, data: dict):
        self.meta_path.write_text(json.dumps(data, indent=2))

    def save(self, data: dict):
        with self._lock:
            self._write(data)

    def add_file(self, original_name: str, file_bytes: bytes, tags: list[str] | None = None) -> dict:
        file_id = uuid.uuid4().hex[:8]
        stored_name = f"{file_id}_{original_name}"
        file_path = self.docs_dir / stored_name
        file_path.write_bytes(file_bytes)

        mime_type, _ = mimetypes.guess_type(original_name)

        entry = {
            "original_name": original_name,
            "stored_name": stored_name,
            "display_name": original_name,
            "tags": tags or [],
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "size_bytes": len(file_bytes),
            "mime_type": mime_type or "application/octet-stream",
        }

        with self._lock:
            data = json.loads(self.meta_path.read_text())
            data["files"][file_id] = entry
            self._write(data)

        return {"id": file_id, **entry}

    def update_file(self, file_id: str, display_name: str | None = None, tags: list[str] | None = None) -> dict:
        with self._lock:
            data = json.loads(self.meta_path.read_text())
            if file_id not in data["files"]:
                raise KeyError(f"File {file_id} not found")
            if display_name is not None:
                data["files"][file_id]["display_name"] = display_name
            if tags is not None:
                data["files"][file_id]["tags"] = tags
            self._write(data)
            return data["files"][file_id]

    def delete_file(self, file_id: str):
        with self._lock:
            data = json.loads(self.meta_path.read_text())
            if file_id not in data["files"]:
                raise KeyError(f"File {file_id} not found")
            stored_name = data["files"][file_id]["stored_name"]
            file_path = self.docs_dir / stored_name
            if file_path.exists():
                file_path.unlink()
            del data["files"][file_id]
            self._write(data)

    def get_file(self, file_id: str) -> dict:
        data = self.read()
        if file_id not in data["files"]:
            raise KeyError(f"File {file_id} not found")
        return data["files"][file_id]

    def sync(self) -> dict:
        with self._lock:
            data = json.loads(self.meta_path.read_text())
            on_disk = set()
            added = []
            removed = []

            for f in self.docs_dir.iterdir():
                if f.name.startswith(".") or f.is_dir():
                    continue
                ext = f.suffix.lower()
                if ext not in ALLOWED_EXTENSIONS:
                    continue
                on_disk.add(f.name)

                # Check if this file is already tracked
                found = False
                for fid, meta in data["files"].items():
                    if meta["stored_name"] == f.name:
                        found = True
                        break
                if not found:
                    # Try to extract ID from filename
                    parts = f.name.split("_", 1)
                    if len(parts) == 2:
                        file_id = parts[0]
                        original = parts[1]
                    else:
                        file_id = uuid.uuid4().hex[:8]
                        original = f.name

                    mime_type, _ = mimetypes.guess_type(f.name)
                    data["files"][file_id] = {
                        "original_name": original,
                        "stored_name": f.name,
                        "display_name": original,
                        "tags": [],
                        "uploaded_at": datetime.now(timezone.utc).isoformat(),
                        "size_bytes": f.stat().st_size,
                        "mime_type": mime_type or "application/octet-stream",
                    }
                    added.append(file_id)

            # Remove entries for files no longer on disk
            to_remove = []
            for fid, meta in data["files"].items():
                if meta["stored_name"] not in on_disk:
                    to_remove.append(fid)
            for fid in to_remove:
                del data["files"][fid]
                removed.append(fid)

            self._write(data)
            return {"added": added, "removed": removed}

    def add_tag(self, tag: str):
        with self._lock:
            data = json.loads(self.meta_path.read_text())
            if tag not in data["tags"]:
                data["tags"].append(tag)
                self._write(data)

    def delete_tag(self, tag: str):
        with self._lock:
            data = json.loads(self.meta_path.read_text())
            if tag in data["tags"]:
                data["tags"].remove(tag)
            for fid in data["files"]:
                if tag in data["files"][fid]["tags"]:
                    data["files"][fid]["tags"].remove(tag)
            self._write(data)

    def get_tags(self) -> list[str]:
        return self.read()["tags"]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_metadata.py -v`
Expected: PASS

- [ ] **Step 6: Write additional metadata tests**

Add to `backend/tests/test_metadata.py`:

```python
def test_add_file(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    result = service.add_file("test.txt", b"hello world", tags=["resume"])
    assert result["original_name"] == "test.txt"
    assert result["tags"] == ["resume"]
    assert result["size_bytes"] == 11
    assert (docs_dir / result["stored_name"]).exists()


def test_delete_file(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    result = service.add_file("test.txt", b"hello")
    file_id = result["id"]
    service.delete_file(file_id)
    data = service.read()
    assert file_id not in data["files"]


def test_update_file(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    result = service.add_file("test.txt", b"hello")
    file_id = result["id"]
    updated = service.update_file(file_id, display_name="My Resume", tags=["resume", "engineering"])
    assert updated["display_name"] == "My Resume"
    assert updated["tags"] == ["resume", "engineering"]


def test_sync_discovers_new_files(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    # Drop a file manually
    (docs_dir / "manual_file.txt").write_text("manual content")
    result = service.sync()
    assert len(result["added"]) == 1
    data = service.read()
    assert any(f["original_name"] == "manual_file.txt" for f in data["files"].values())


def test_sync_removes_stale_entries(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    result = service.add_file("test.txt", b"hello")
    # Delete file from disk manually
    stored = docs_dir / result["stored_name"]
    stored.unlink()
    sync_result = service.sync()
    assert len(sync_result["removed"]) == 1


def test_add_and_delete_tag(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    service.add_tag("engineering")
    assert "engineering" in service.get_tags()
    service.delete_tag("engineering")
    assert "engineering" not in service.get_tags()


def test_delete_tag_removes_from_files(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    service = MetadataService(docs_dir)
    service.add_tag("engineering")
    result = service.add_file("test.txt", b"hello", tags=["engineering"])
    service.delete_tag("engineering")
    data = service.read()
    assert "engineering" not in data["files"][result["id"]]["tags"]
```

- [ ] **Step 7: Run all metadata tests**

Run: `cd backend && python -m pytest tests/test_metadata.py -v`
Expected: All PASS

- [ ] **Step 8: Commit**

```bash
git add backend/services/ backend/tests/test_metadata.py
git commit -m "feat: add MetadataService for document metadata CRUD and sync"
```

---

### Task 9: Document API Endpoints

**Files:**
- Create: `backend/routers/__init__.py`
- Create: `backend/routers/documents.py`
- Create: `backend/tests/test_documents_api.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Create backend/routers/__init__.py** (empty file)

- [ ] **Step 2: Write failing test for document list endpoint**

```python
# backend/tests/test_documents_api.py
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.metadata import MetadataService
from backend.config import DOCUMENTS_DIR
import backend.config as config


def setup_test_env(tmp_path):
    """Override config to use temp directory."""
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    config.DOCUMENTS_DIR = docs_dir
    # Re-initialize the metadata service on the app
    from backend.routers import documents
    documents._metadata_service = MetadataService(docs_dir)
    return docs_dir


def test_list_documents_empty(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/documents")
    assert response.status_code == 200
    assert response.json() == []


def test_upload_document(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post(
        "/api/documents/upload",
        files={"files": ("test.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["original_name"] == "test.txt"


def test_list_documents_after_upload(tmp_path):
    docs_dir = setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/documents/upload", files={"files": ("test.txt", b"hello", "text/plain")})
    response = client.get("/api/documents")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_document_content(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    upload = client.post("/api/documents/upload", files={"files": ("test.txt", b"hello world", "text/plain")})
    file_id = upload.json()[0]["id"]
    response = client.get(f"/api/documents/{file_id}/content")
    assert response.status_code == 200
    assert response.content == b"hello world"


def test_delete_document(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    upload = client.post("/api/documents/upload", files={"files": ("test.txt", b"hello", "text/plain")})
    file_id = upload.json()[0]["id"]
    response = client.delete(f"/api/documents/{file_id}")
    assert response.status_code == 200
    listing = client.get("/api/documents")
    assert len(listing.json()) == 0


def test_update_document_metadata(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    upload = client.post("/api/documents/upload", files={"files": ("test.txt", b"hello", "text/plain")})
    file_id = upload.json()[0]["id"]
    response = client.put(f"/api/documents/{file_id}", json={"display_name": "My Doc", "tags": ["resume"]})
    assert response.status_code == 200
    assert response.json()["display_name"] == "My Doc"


def test_sync_documents(tmp_path):
    docs_dir = setup_test_env(tmp_path)
    client = TestClient(app)
    (docs_dir / "dropped_file.txt").write_text("dropped in")
    response = client.post("/api/documents/sync")
    assert response.status_code == 200
    assert len(response.json()["added"]) == 1


def test_filter_by_tag(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/documents/upload", files={"files": ("a.txt", b"a", "text/plain")})
    client.post("/api/documents/upload", files={"files": ("b.txt", b"b", "text/plain")})
    docs = client.get("/api/documents").json()
    client.put(f"/api/documents/{docs[0]['id']}", json={"tags": ["resume"]})
    filtered = client.get("/api/documents?tag=resume")
    assert len(filtered.json()) == 1


def test_search_documents(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/documents/upload", files={"files": ("resume.txt", b"a", "text/plain")})
    client.post("/api/documents/upload", files={"files": ("cover.txt", b"b", "text/plain")})
    result = client.get("/api/documents?search=resume")
    assert len(result.json()) == 1


def test_upload_rejected_for_unsupported_type(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/documents/upload", files={"files": ("photo.png", b"img", "image/png")})
    assert response.status_code == 400
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_documents_api.py -v`
Expected: FAIL — router not defined

- [ ] **Step 4: Implement documents router**

```python
# backend/routers/documents.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.config import DOCUMENTS_DIR, ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE
from backend.services.metadata import MetadataService
from pathlib import Path

router = APIRouter(prefix="/api/documents", tags=["documents"])

_metadata_service: MetadataService | None = None


def get_service() -> MetadataService:
    global _metadata_service
    if _metadata_service is None:
        _metadata_service = MetadataService(DOCUMENTS_DIR)
    return _metadata_service


class UpdateDocumentRequest(BaseModel):
    display_name: str | None = None
    tags: list[str] | None = None


@router.get("")
async def list_documents(tag: str | None = None, search: str | None = None):
    service = get_service()
    data = service.read()
    files = []
    for file_id, meta in data["files"].items():
        if tag and tag not in meta["tags"]:
            continue
        if search and search.lower() not in meta["display_name"].lower():
            continue
        files.append({"id": file_id, **meta})
    return files


@router.get("/{file_id}")
async def get_document(file_id: str):
    service = get_service()
    try:
        meta = service.get_file(file_id)
        return {"id": file_id, **meta}
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")


@router.get("/{file_id}/content")
async def get_document_content(file_id: str):
    service = get_service()
    try:
        meta = service.get_file(file_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")
    file_path = service.docs_dir / meta["stored_name"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(
        file_path,
        media_type=meta["mime_type"],
        filename=meta["original_name"],
    )


@router.post("/upload")
async def upload_documents(files: list[UploadFile] = File(...), tags: str | None = None):
    service = get_service()
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    results = []

    for file in files:
        ext = Path(file.filename or "").suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

        content = await file.read()
        if len(content) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail=f"File too large: {file.filename}")

        result = service.add_file(file.filename or "unnamed", content, tags=tag_list)
        results.append(result)

    return results


@router.put("/{file_id}")
async def update_document(file_id: str, body: UpdateDocumentRequest):
    service = get_service()
    try:
        updated = service.update_file(file_id, display_name=body.display_name, tags=body.tags)
        return {"id": file_id, **updated}
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")


@router.delete("/{file_id}")
async def delete_document(file_id: str):
    service = get_service()
    try:
        service.delete_file(file_id)
        return {"status": "deleted"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")


@router.post("/sync")
async def sync_documents():
    service = get_service()
    return service.sync()
```

- [ ] **Step 5: Register router in main.py**

Add to `backend/main.py`:
```python
from backend.routers.documents import router as documents_router
app.include_router(documents_router)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_documents_api.py -v`
Expected: All PASS

- [ ] **Step 7: Commit**

```bash
git add backend/routers/ backend/tests/test_documents_api.py backend/main.py
git commit -m "feat: add document API endpoints with upload, CRUD, sync, and filtering"
```

---

### Task 10: Tag API Endpoints

**Files:**
- Create: `backend/routers/tags.py`
- Create: `backend/tests/test_tags_api.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_tags_api.py
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.metadata import MetadataService
import backend.config as config


def setup_test_env(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    config.DOCUMENTS_DIR = docs_dir
    from backend.routers import documents, tags
    documents._metadata_service = MetadataService(docs_dir)
    tags._metadata_service = documents._metadata_service
    return docs_dir


def test_list_tags(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/tags")
    assert response.status_code == 200
    assert set(response.json()) == {"resume", "cover-letter", "cv"}


def test_create_tag(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/tags", json={"name": "engineering"})
    assert response.status_code == 200
    tags = client.get("/api/tags").json()
    assert "engineering" in tags


def test_delete_tag(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/tags", json={"name": "engineering"})
    response = client.delete("/api/tags/engineering")
    assert response.status_code == 200
    tags = client.get("/api/tags").json()
    assert "engineering" not in tags
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_tags_api.py -v`
Expected: FAIL

- [ ] **Step 3: Implement tags router**

```python
# backend/routers/tags.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.config import DOCUMENTS_DIR
from backend.services.metadata import MetadataService

router = APIRouter(prefix="/api/tags", tags=["tags"])

_metadata_service: MetadataService | None = None


def get_service() -> MetadataService:
    global _metadata_service
    if _metadata_service is None:
        _metadata_service = MetadataService(DOCUMENTS_DIR)
    return _metadata_service


class CreateTagRequest(BaseModel):
    name: str


@router.get("")
async def list_tags():
    return get_service().get_tags()


@router.post("")
async def create_tag(body: CreateTagRequest):
    get_service().add_tag(body.name)
    return {"status": "created", "tag": body.name}


@router.delete("/{tag}")
async def delete_tag(tag: str):
    get_service().delete_tag(tag)
    return {"status": "deleted", "tag": tag}
```

- [ ] **Step 4: Register router in main.py**

Add to `backend/main.py`:
```python
from backend.routers.tags import router as tags_router
app.include_router(tags_router)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_tags_api.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add backend/routers/tags.py backend/tests/test_tags_api.py backend/main.py
git commit -m "feat: add tag API endpoints for CRUD operations"
```

---

## Phase 3: Document Manager — Frontend

### Task 11: API Client Functions

**Files:**
- Create: `src/api/documents.ts`
- Create: `src/api/tags.ts`

- [ ] **Step 1: Create document API client**

```typescript
// src/api/documents.ts
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
```

- [ ] **Step 2: Create tag API client**

```typescript
// src/api/tags.ts
export async function fetchTags(): Promise<string[]> {
  const res = await fetch('/api/tags')
  if (!res.ok) throw new Error('Failed to fetch tags')
  return res.json()
}

export async function createTag(name: string): Promise<void> {
  const res = await fetch('/api/tags', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  })
  if (!res.ok) throw new Error('Failed to create tag')
}

export async function deleteTag(name: string): Promise<void> {
  const res = await fetch(`/api/tags/${encodeURIComponent(name)}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete tag')
}
```

- [ ] **Step 3: Commit**

```bash
git add src/api/
git commit -m "feat: add API client functions for documents and tags"
```

---

### Task 12: DocumentManager Layout + TagSidebar

**Files:**
- Modify: `src/components/documents/DocumentManager.tsx`
- Create: `src/components/documents/TagSidebar.tsx`
- Create: `src/__tests__/documents/DocumentManager.test.tsx`
- Create: `src/__tests__/documents/TagSidebar.test.tsx`

- [ ] **Step 1: Write failing test for DocumentManager**

```typescript
// src/__tests__/documents/DocumentManager.test.tsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import DocumentManager from '../../components/documents/DocumentManager'

// Mock fetch globally
beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true,
    json: async () => [],
  }))
})

describe('DocumentManager', () => {
  it('renders the three-panel layout', async () => {
    render(<DocumentManager />)
    expect(screen.getByTestId('tag-sidebar')).toBeInTheDocument()
    expect(screen.getByTestId('document-list-panel')).toBeInTheDocument()
  })

  it('renders the page title', () => {
    render(<DocumentManager />)
    expect(screen.getByText('Documents')).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- src/__tests__/documents/DocumentManager.test.tsx`
Expected: FAIL

- [ ] **Step 3: Write failing test for TagSidebar**

```typescript
// src/__tests__/documents/TagSidebar.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { TagSidebar } from '../../components/documents/TagSidebar'
import type { DocumentMeta } from '../../api/documents'

const mockDocs: DocumentMeta[] = [
  { id: '1', original_name: 'a.txt', stored_name: '1_a.txt', display_name: 'a.txt', tags: ['resume'], uploaded_at: '', size_bytes: 10, mime_type: 'text/plain' },
  { id: '2', original_name: 'b.txt', stored_name: '2_b.txt', display_name: 'b.txt', tags: ['resume', 'cv'], uploaded_at: '', size_bytes: 20, mime_type: 'text/plain' },
]

describe('TagSidebar', () => {
  it('shows All Documents with total count', () => {
    render(<TagSidebar tags={['resume', 'cv']} documents={mockDocs} activeTag={null} onSelectTag={() => {}} onCreateTag={() => {}} onDeleteTag={() => {}} />)
    expect(screen.getByText('All Documents')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('shows tag counts', () => {
    render(<TagSidebar tags={['resume', 'cv']} documents={mockDocs} activeTag={null} onSelectTag={() => {}} onCreateTag={() => {}} onDeleteTag={() => {}} />)
    // resume appears in both docs
    const resumeItem = screen.getByText('resume').closest('[data-testid]')
    expect(resumeItem).toBeInTheDocument()
  })

  it('calls onSelectTag when tag is clicked', async () => {
    const onSelect = vi.fn()
    render(<TagSidebar tags={['resume', 'cv']} documents={mockDocs} activeTag={null} onSelectTag={onSelect} onCreateTag={() => {}} onDeleteTag={() => {}} />)
    await userEvent.click(screen.getByText('resume'))
    expect(onSelect).toHaveBeenCalledWith('resume')
  })
})
```

- [ ] **Step 4: Run test to verify it fails**

Run: `npm test -- src/__tests__/documents/TagSidebar.test.tsx`
Expected: FAIL

- [ ] **Step 5: Implement TagSidebar**

```typescript
// src/components/documents/TagSidebar.tsx
import { useState } from 'react'
import type { DocumentMeta } from '../../api/documents'

interface TagSidebarProps {
  tags: string[]
  documents: DocumentMeta[]
  activeTag: string | null
  onSelectTag: (tag: string | null) => void
  onCreateTag: (name: string) => void
  onDeleteTag: (name: string) => void
}

export function TagSidebar({ tags, documents, activeTag, onSelectTag, onCreateTag, onDeleteTag }: TagSidebarProps) {
  const [newTag, setNewTag] = useState('')
  const [showInput, setShowInput] = useState(false)

  const tagCounts = tags.reduce<Record<string, number>>((acc, tag) => {
    acc[tag] = documents.filter(d => d.tags.includes(tag)).length
    return acc
  }, {})

  const handleSubmit = () => {
    if (newTag.trim()) {
      onCreateTag(newTag.trim())
      setNewTag('')
      setShowInput(false)
    }
  }

  return (
    <div className="tag-sidebar" data-testid="tag-sidebar">
      <div className="tag-sidebar-title">Tags</div>
      <div
        className={`tag-item ${activeTag === null ? 'active' : ''}`}
        onClick={() => onSelectTag(null)}
        data-testid="tag-all"
      >
        <span>All Documents</span>
        <span className="tag-count">{documents.length}</span>
      </div>
      {tags.map(tag => (
        <div
          key={tag}
          className={`tag-item ${activeTag === tag ? 'active' : ''}`}
          onClick={() => onSelectTag(tag)}
          data-testid={`tag-${tag}`}
        >
          <span>{tag}</span>
          <span className="tag-count">{tagCounts[tag] || 0}</span>
        </div>
      ))}
      {showInput ? (
        <div className="tag-input-row">
          <input
            className="form-input"
            value={newTag}
            onChange={e => setNewTag(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSubmit()}
            placeholder="Tag name..."
            autoFocus
          />
          <button className="btn btn-primary btn-sm" onClick={handleSubmit}>Add</button>
          <button className="btn btn-secondary btn-sm" onClick={() => setShowInput(false)}>Cancel</button>
        </div>
      ) : (
        <div className="add-tag-btn" onClick={() => setShowInput(true)}>+ New Tag</div>
      )}
    </div>
  )
}
```

- [ ] **Step 6: Implement DocumentManager with layout**

```typescript
// src/components/documents/DocumentManager.tsx
import { useState, useEffect, useCallback } from 'react'
import { TagSidebar } from './TagSidebar'
import { DocumentToolbar } from './DocumentToolbar'
import { DropZone } from './DropZone'
import { DocumentList } from './DocumentList'
import { DocumentPreview } from './DocumentPreview'
import { fetchDocuments, uploadDocuments, updateDocument, deleteDocument, syncDocuments } from '../../api/documents'
import { fetchTags, createTag, deleteTag } from '../../api/tags'
import type { DocumentMeta } from '../../api/documents'

export default function DocumentManager() {
  const [documents, setDocuments] = useState<DocumentMeta[]>([])
  const [tags, setTags] = useState<string[]>([])
  const [activeTag, setActiveTag] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    const [docs, tagList] = await Promise.all([fetchDocuments(), fetchTags()])
    setDocuments(docs)
    setTags(tagList)
  }, [])

  useEffect(() => { loadData() }, [loadData])

  const filteredDocs = documents.filter(d => {
    if (activeTag && !d.tags.includes(activeTag)) return false
    if (search && !d.display_name.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  const selectedDoc = documents.find(d => d.id === selectedId) || null

  const handleUpload = async (files: File[]) => {
    await uploadDocuments(files)
    await loadData()
  }

  const handleSync = async () => {
    await syncDocuments()
    await loadData()
  }

  const handleUpdate = async (id: string, data: { display_name?: string; tags?: string[] }) => {
    await updateDocument(id, data)
    await loadData()
  }

  const handleDelete = async (id: string) => {
    await deleteDocument(id)
    setSelectedId(null)
    await loadData()
  }

  const handleCreateTag = async (name: string) => {
    await createTag(name)
    await loadData()
  }

  const handleDeleteTag = async (name: string) => {
    await deleteTag(name)
    if (activeTag === name) setActiveTag(null)
    await loadData()
  }

  return (
    <div className="document-manager">
      <h1>Documents</h1>
      <div className="document-manager-layout">
        <TagSidebar
          tags={tags}
          documents={documents}
          activeTag={activeTag}
          onSelectTag={setActiveTag}
          onCreateTag={handleCreateTag}
          onDeleteTag={handleDeleteTag}
        />
        <div className="document-list-panel" data-testid="document-list-panel">
          <DocumentToolbar search={search} onSearchChange={setSearch} onUpload={handleUpload} onSync={handleSync} />
          <DropZone onDrop={handleUpload} />
          <DocumentList documents={filteredDocs} selectedId={selectedId} onSelect={setSelectedId} />
          <div className="status-bar">
            {filteredDocs.length} document{filteredDocs.length !== 1 ? 's' : ''}
          </div>
        </div>
        {selectedDoc && (
          <DocumentPreview
            document={selectedDoc}
            allTags={tags}
            onUpdate={(data) => handleUpdate(selectedDoc.id, data)}
            onDelete={() => handleDelete(selectedDoc.id)}
          />
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 7: Create stub child components** (to be implemented in next tasks)

Create minimal stubs for `DocumentToolbar`, `DropZone`, `DocumentList`, `DocumentPreview` so the parent compiles:

`src/components/documents/DocumentToolbar.tsx`:
```typescript
interface Props { search: string; onSearchChange: (v: string) => void; onUpload: (f: File[]) => void; onSync: () => void }
export function DocumentToolbar({ search, onSearchChange, onUpload, onSync }: Props) {
  return <div className="document-toolbar" data-testid="document-toolbar">Toolbar stub</div>
}
```

`src/components/documents/DropZone.tsx`:
```typescript
interface Props { onDrop: (f: File[]) => void }
export function DropZone({ onDrop }: Props) {
  return <div className="drop-zone" data-testid="drop-zone">Drop zone stub</div>
}
```

`src/components/documents/DocumentList.tsx`:
```typescript
import type { DocumentMeta } from '../../api/documents'
interface Props { documents: DocumentMeta[]; selectedId: string | null; onSelect: (id: string) => void }
export function DocumentList({ documents, selectedId, onSelect }: Props) {
  return <div data-testid="document-list">List stub ({documents.length} items)</div>
}
```

`src/components/documents/DocumentPreview.tsx`:
```typescript
import type { DocumentMeta } from '../../api/documents'
interface Props { document: DocumentMeta; allTags: string[]; onUpdate: (data: { display_name?: string; tags?: string[] }) => void; onDelete: () => void }
export function DocumentPreview({ document: doc }: Props) {
  return <div data-testid="document-preview">Preview: {doc.display_name}</div>
}
```

- [ ] **Step 8: Add CSS for document manager layout**

Append to `src/index.css`:

```css
/* Document Manager */
.document-manager-layout {
  display: grid;
  grid-template-columns: 240px 1fr 400px;
  gap: var(--space-lg);
  height: calc(100vh - 140px);
}

.tag-sidebar {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  overflow-y: auto;
}

.tag-sidebar-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: var(--space-sm);
}

.tag-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 14px;
  transition: background var(--transition-base);
}

.tag-item:hover { background: var(--color-elevated); }
.tag-item.active { background: var(--color-primary); color: white; }

.tag-count {
  font-size: 12px;
  background: var(--color-elevated);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  color: var(--color-muted);
}

.tag-item.active .tag-count {
  background: rgba(255,255,255,0.2);
  color: white;
}

.add-tag-btn {
  padding: var(--space-sm) var(--space-md);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  text-align: center;
  color: var(--color-muted);
  cursor: pointer;
  font-size: 14px;
  margin-top: auto;
}

.add-tag-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.tag-input-row {
  display: flex;
  gap: var(--space-xs);
  margin-top: auto;
}

.tag-input-row .form-input {
  flex: 1;
  font-size: 13px;
  padding: 6px 10px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.document-list-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  overflow: hidden;
}

.status-bar {
  font-size: 12px;
  color: var(--color-muted);
  padding: var(--space-sm) 0;
}
```

- [ ] **Step 9: Run tests to verify they pass**

Run: `npm test -- src/__tests__/documents/`
Expected: All PASS

- [ ] **Step 10: Commit**

```bash
git add src/components/documents/ src/__tests__/documents/ src/index.css
git commit -m "feat: add DocumentManager layout with TagSidebar component"
```

---

### Task 13: DocumentToolbar, DropZone, DocumentList, DocumentItem

**Files:**
- Modify: `src/components/documents/DocumentToolbar.tsx`
- Modify: `src/components/documents/DropZone.tsx`
- Modify: `src/components/documents/DocumentList.tsx`
- Create: `src/components/documents/DocumentItem.tsx`
- Create: `src/__tests__/documents/DocumentToolbar.test.tsx`
- Create: `src/__tests__/documents/DropZone.test.tsx`
- Create: `src/__tests__/documents/DocumentList.test.tsx`

- [ ] **Step 1: Write failing tests for toolbar, dropzone, and list**

```typescript
// src/__tests__/documents/DocumentToolbar.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { DocumentToolbar } from '../../components/documents/DocumentToolbar'

describe('DocumentToolbar', () => {
  it('renders search input', () => {
    render(<DocumentToolbar search="" onSearchChange={() => {}} onUpload={() => {}} onSync={() => {}} />)
    expect(screen.getByPlaceholderText(/search/i)).toBeInTheDocument()
  })

  it('calls onSearchChange when typing', async () => {
    const onChange = vi.fn()
    render(<DocumentToolbar search="" onSearchChange={onChange} onUpload={() => {}} onSync={() => {}} />)
    await userEvent.type(screen.getByPlaceholderText(/search/i), 'test')
    expect(onChange).toHaveBeenCalled()
  })

  it('has upload and sync buttons', () => {
    render(<DocumentToolbar search="" onSearchChange={() => {}} onUpload={() => {}} onSync={() => {}} />)
    expect(screen.getByText(/upload/i)).toBeInTheDocument()
    expect(screen.getByText(/sync/i)).toBeInTheDocument()
  })
})
```

```typescript
// src/__tests__/documents/DropZone.test.tsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { DropZone } from '../../components/documents/DropZone'

describe('DropZone', () => {
  it('renders drop area text', () => {
    render(<DropZone onDrop={() => {}} />)
    expect(screen.getByText(/drop files/i)).toBeInTheDocument()
  })
})
```

```typescript
// src/__tests__/documents/DocumentList.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { DocumentList } from '../../components/documents/DocumentList'
import type { DocumentMeta } from '../../api/documents'

const mockDocs: DocumentMeta[] = [
  { id: '1', original_name: 'resume.pdf', stored_name: '1_resume.pdf', display_name: 'resume.pdf', tags: ['resume'], uploaded_at: '2026-03-20T00:00:00Z', size_bytes: 245000, mime_type: 'application/pdf' },
  { id: '2', original_name: 'notes.txt', stored_name: '2_notes.txt', display_name: 'notes.txt', tags: [], uploaded_at: '2026-03-19T00:00:00Z', size_bytes: 500, mime_type: 'text/plain' },
]

describe('DocumentList', () => {
  it('renders document items', () => {
    render(<DocumentList documents={mockDocs} selectedId={null} onSelect={() => {}} />)
    expect(screen.getByText('resume.pdf')).toBeInTheDocument()
    expect(screen.getByText('notes.txt')).toBeInTheDocument()
  })

  it('highlights selected document', () => {
    render(<DocumentList documents={mockDocs} selectedId="1" onSelect={() => {}} />)
    const item = screen.getByText('resume.pdf').closest('.document-item')
    expect(item).toHaveClass('selected')
  })

  it('calls onSelect when item is clicked', async () => {
    const onSelect = vi.fn()
    render(<DocumentList documents={mockDocs} selectedId={null} onSelect={onSelect} />)
    await userEvent.click(screen.getByText('resume.pdf'))
    expect(onSelect).toHaveBeenCalledWith('1')
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npm test -- src/__tests__/documents/DocumentToolbar.test.tsx src/__tests__/documents/DropZone.test.tsx src/__tests__/documents/DocumentList.test.tsx`
Expected: FAIL

- [ ] **Step 3: Implement DocumentToolbar**

```typescript
// src/components/documents/DocumentToolbar.tsx
import { useRef } from 'react'

interface Props {
  search: string
  onSearchChange: (value: string) => void
  onUpload: (files: File[]) => void
  onSync: () => void
}

export function DocumentToolbar({ search, onSearchChange, onUpload, onSync }: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      onUpload(Array.from(e.target.files))
      e.target.value = ''
    }
  }

  return (
    <div className="document-toolbar" data-testid="document-toolbar">
      <input
        className="form-input toolbar-search"
        placeholder="Search documents..."
        value={search}
        onChange={e => onSearchChange(e.target.value)}
      />
      <input ref={fileInputRef} type="file" multiple hidden onChange={handleFileChange} />
      <button className="btn btn-primary" onClick={() => fileInputRef.current?.click()}>Upload</button>
      <button className="btn btn-secondary" onClick={onSync}>Sync</button>
    </div>
  )
}
```

- [ ] **Step 4: Implement DropZone**

```typescript
// src/components/documents/DropZone.tsx
import { useState, useCallback } from 'react'

interface Props {
  onDrop: (files: File[]) => void
}

export function DropZone({ onDrop }: Props) {
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files)
    if (files.length) onDrop(files)
  }, [onDrop])

  return (
    <div
      className={`drop-zone ${isDragging ? 'active' : ''}`}
      data-testid="drop-zone"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="drop-zone-icon">+</div>
      <div className="drop-zone-text">Drop files here to upload</div>
      <div className="drop-zone-sub">PDF, DOCX, TXT, MD, XLSX, CSV, PPTX</div>
    </div>
  )
}
```

- [ ] **Step 5: Implement DocumentItem**

```typescript
// src/components/documents/DocumentItem.tsx
import type { DocumentMeta } from '../../api/documents'

interface Props {
  document: DocumentMeta
  isSelected: boolean
  onSelect: (id: string) => void
}

const EXT_STYLES: Record<string, { bg: string; color: string }> = {
  pdf: { bg: '#7f1d1d', color: '#fca5a5' },
  docx: { bg: '#1e3a5f', color: '#93c5fd' },
  md: { bg: '#1a3a2a', color: '#86efac' },
  txt: { bg: '#3b3520', color: '#fde68a' },
  csv: { bg: '#2d1b4e', color: '#c4b5fd' },
  xlsx: { bg: '#2d1b4e', color: '#c4b5fd' },
  pptx: { bg: '#5c2d1a', color: '#fdba74' },
}

function getExt(filename: string): string {
  return filename.split('.').pop()?.toLowerCase() || ''
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

export function DocumentItem({ document: doc, isSelected, onSelect }: Props) {
  const ext = getExt(doc.original_name)
  const style = EXT_STYLES[ext] || { bg: 'var(--color-elevated)', color: 'var(--color-muted)' }

  return (
    <div
      className={`document-item ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect(doc.id)}
    >
      <div className="file-icon" style={{ background: style.bg, color: style.color }}>
        {ext.toUpperCase()}
      </div>
      <div className="file-info">
        <div className="file-name">{doc.display_name}</div>
        <div className="file-meta">{formatSize(doc.size_bytes)} &middot; {formatDate(doc.uploaded_at)}</div>
      </div>
      <div className="file-tags">
        {doc.tags.map(t => <span key={t} className="tag-badge">{t}</span>)}
      </div>
    </div>
  )
}
```

- [ ] **Step 6: Implement DocumentList**

```typescript
// src/components/documents/DocumentList.tsx
import type { DocumentMeta } from '../../api/documents'
import { DocumentItem } from './DocumentItem'

interface Props {
  documents: DocumentMeta[]
  selectedId: string | null
  onSelect: (id: string) => void
}

export function DocumentList({ documents, selectedId, onSelect }: Props) {
  return (
    <div className="document-list" data-testid="document-list">
      {documents.map(doc => (
        <DocumentItem
          key={doc.id}
          document={doc}
          isSelected={doc.id === selectedId}
          onSelect={onSelect}
        />
      ))}
      {documents.length === 0 && (
        <div className="empty-state">No documents found</div>
      )}
    </div>
  )
}
```

- [ ] **Step 7: Add CSS for toolbar, dropzone, list, and items**

Append to `src/index.css`:

```css
/* Document Toolbar */
.document-toolbar {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.toolbar-search {
  flex: 1;
}

/* Drop Zone */
.drop-zone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  text-align: center;
  color: var(--color-muted);
  transition: all var(--transition-base);
  cursor: pointer;
}

.drop-zone.active {
  border-color: var(--color-primary);
  background: rgba(74, 111, 165, 0.1);
  color: var(--color-primary);
}

.drop-zone-icon { font-size: 32px; margin-bottom: var(--space-sm); }
.drop-zone-text { font-size: 14px; }
.drop-zone-sub { font-size: 12px; margin-top: var(--space-xs); }

/* Document List */
.document-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.document-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-base);
}

.document-item:hover { border-color: var(--color-primary); }
.document-item.selected { border-color: var(--color-primary); background: var(--color-elevated); }

.file-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.file-info { flex: 1; min-width: 0; }
.file-name { font-size: 14px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.file-meta { font-size: 12px; color: var(--color-muted); margin-top: 2px; }
.file-tags { display: flex; gap: var(--space-xs); flex-shrink: 0; }

.empty-state {
  text-align: center;
  padding: var(--space-3xl);
  color: var(--color-muted);
  font-size: 14px;
}
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `npm test -- src/__tests__/documents/`
Expected: All PASS

- [ ] **Step 9: Commit**

```bash
git add src/components/documents/ src/__tests__/documents/ src/index.css
git commit -m "feat: add DocumentToolbar, DropZone, DocumentList, and DocumentItem components"
```

---

### Task 14: DocumentPreview

**Files:**
- Modify: `src/components/documents/DocumentPreview.tsx`
- Create: `src/__tests__/documents/DocumentPreview.test.tsx`

- [ ] **Step 1: Write failing test**

```typescript
// src/__tests__/documents/DocumentPreview.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { DocumentPreview } from '../../components/documents/DocumentPreview'
import type { DocumentMeta } from '../../api/documents'

const mockTxtDoc: DocumentMeta = {
  id: '1', original_name: 'notes.txt', stored_name: '1_notes.txt',
  display_name: 'notes.txt', tags: ['resume'], uploaded_at: '2026-03-20T00:00:00Z',
  size_bytes: 500, mime_type: 'text/plain',
}

const mockDocxDoc: DocumentMeta = {
  id: '2', original_name: 'resume.docx', stored_name: '2_resume.docx',
  display_name: 'resume.docx', tags: [], uploaded_at: '2026-03-20T00:00:00Z',
  size_bytes: 38000, mime_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}

describe('DocumentPreview', () => {
  it('shows document name and metadata', () => {
    render(<DocumentPreview document={mockTxtDoc} allTags={['resume', 'cv']} onUpdate={() => {}} onDelete={() => {}} />)
    expect(screen.getByText('notes.txt')).toBeInTheDocument()
  })

  it('shows download and delete buttons', () => {
    render(<DocumentPreview document={mockTxtDoc} allTags={['resume']} onUpdate={() => {}} onDelete={() => {}} />)
    expect(screen.getByText(/download/i)).toBeInTheDocument()
    expect(screen.getByText(/delete/i)).toBeInTheDocument()
  })

  it('shows file info for non-previewable types', () => {
    render(<DocumentPreview document={mockDocxDoc} allTags={[]} onUpdate={() => {}} onDelete={() => {}} />)
    expect(screen.getByText(/no preview available/i)).toBeInTheDocument()
  })

  it('calls onDelete when delete is clicked', async () => {
    const onDelete = vi.fn()
    render(<DocumentPreview document={mockTxtDoc} allTags={[]} onUpdate={() => {}} onDelete={onDelete} />)
    await userEvent.click(screen.getByText(/delete/i))
    expect(onDelete).toHaveBeenCalled()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- src/__tests__/documents/DocumentPreview.test.tsx`
Expected: FAIL

- [ ] **Step 3: Implement DocumentPreview**

```typescript
// src/components/documents/DocumentPreview.tsx
import { useState, useEffect } from 'react'
import type { DocumentMeta } from '../../api/documents'
import { getContentUrl } from '../../api/documents'

interface Props {
  document: DocumentMeta
  allTags: string[]
  onUpdate: (data: { display_name?: string; tags?: string[] }) => void
  onDelete: () => void
}

const PREVIEWABLE = ['text/plain', 'text/markdown', 'text/csv', 'application/pdf']

function isPreviewable(mimeType: string): boolean {
  return PREVIEWABLE.includes(mimeType)
}

export function DocumentPreview({ document: doc, allTags, onUpdate, onDelete }: Props) {
  const [textContent, setTextContent] = useState<string | null>(null)
  const contentUrl = getContentUrl(doc.id)
  const previewable = isPreviewable(doc.mime_type)

  useEffect(() => {
    if (doc.mime_type === 'text/plain' || doc.mime_type === 'text/markdown' || doc.mime_type === 'text/csv') {
      fetch(contentUrl)
        .then(r => r.text())
        .then(setTextContent)
        .catch(() => setTextContent(null))
    } else {
      setTextContent(null)
    }
  }, [doc.id, doc.mime_type, contentUrl])

  const handleRemoveTag = (tag: string) => {
    onUpdate({ tags: doc.tags.filter(t => t !== tag) })
  }

  const handleAddTag = (tag: string) => {
    if (!doc.tags.includes(tag)) {
      onUpdate({ tags: [...doc.tags, tag] })
    }
  }

  return (
    <div className="document-preview card" data-testid="document-preview">
      <div className="preview-header">
        <div className="preview-filename">{doc.display_name}</div>
        <div className="preview-meta">
          {doc.mime_type} &middot; {(doc.size_bytes / 1024).toFixed(0)} KB
        </div>
        <div className="preview-tags">
          {doc.tags.map(t => (
            <span key={t} className="preview-tag">
              {t} <span className="remove" onClick={() => handleRemoveTag(t)}>&times;</span>
            </span>
          ))}
          <select
            className="add-tag-select"
            value=""
            onChange={e => { if (e.target.value) handleAddTag(e.target.value) }}
          >
            <option value="">+ tag</option>
            {allTags.filter(t => !doc.tags.includes(t)).map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="preview-content">
        {doc.mime_type === 'application/pdf' && (
          <iframe src={contentUrl} className="pdf-preview" title="PDF Preview" />
        )}
        {(doc.mime_type === 'text/plain' || doc.mime_type === 'text/markdown') && textContent !== null && (
          <pre className="text-preview">{textContent}</pre>
        )}
        {doc.mime_type === 'text/csv' && textContent !== null && (
          <pre className="text-preview">{textContent}</pre>
        )}
        {!previewable && (
          <div className="no-preview">No preview available for this file type.</div>
        )}
      </div>

      <div className="preview-actions">
        <a href={contentUrl} download={doc.original_name} className="btn btn-primary">Download</a>
        <button className="btn btn-danger" onClick={onDelete}>Delete</button>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Add CSS for preview panel**

Append to `src/index.css`:

```css
/* Document Preview */
.document-preview {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-header {
  padding: var(--space-md);
  border-bottom: 1px solid var(--color-border);
}

.preview-filename { font-size: 16px; font-weight: 600; margin-bottom: var(--space-xs); }
.preview-meta { font-size: 12px; color: var(--color-muted); }

.preview-tags {
  display: flex;
  gap: var(--space-xs);
  flex-wrap: wrap;
  margin-top: var(--space-sm);
}

.preview-tag {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  background: rgba(123, 147, 212, 0.15);
  color: var(--color-secondary);
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.preview-tag .remove { cursor: pointer; opacity: 0.6; }
.preview-tag .remove:hover { opacity: 1; }

.add-tag-select {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: var(--radius-full);
  border: 1px dashed var(--color-border);
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  outline: none;
}

.preview-content {
  flex: 1;
  padding: var(--space-md);
  overflow-y: auto;
}

.pdf-preview { width: 100%; height: 100%; border: none; }

.text-preview {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  color: var(--color-text);
}

.no-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--color-muted);
  font-size: 14px;
}

.preview-actions {
  padding: var(--space-md);
  border-top: 1px solid var(--color-border);
  display: flex;
  gap: var(--space-sm);
}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `npm test -- src/__tests__/documents/`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add src/components/documents/DocumentPreview.tsx src/__tests__/documents/DocumentPreview.test.tsx src/index.css
git commit -m "feat: add DocumentPreview with text, PDF, and file info rendering"
```

---

## Phase 4: Profile View — Backend

### Task 15: Profile Service

**Files:**
- Create: `backend/services/profile.py`
- Create: `backend/tests/test_profile_service.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_profile_service.py
import json
from backend.services.profile import ProfileService

EMPTY_PROFILE = {
    "summary": "",
    "skills": [],
    "experience": [],
    "education": [],
    "certifications": [],
    "objectives": "",
}


def test_get_creates_empty_scaffold(tmp_path):
    profile_path = tmp_path / ".profile.json"
    service = ProfileService(profile_path)
    profile = service.get()
    assert profile == EMPTY_PROFILE
    assert profile_path.exists()


def test_get_loads_existing_profile(tmp_path):
    profile_path = tmp_path / ".profile.json"
    profile_path.write_text(json.dumps({"summary": "Engineer", "skills": [], "experience": [],
                                         "education": [], "certifications": [], "objectives": ""}))
    service = ProfileService(profile_path)
    assert service.get()["summary"] == "Engineer"


def test_put_replaces_profile(tmp_path):
    profile_path = tmp_path / ".profile.json"
    service = ProfileService(profile_path)
    new_profile = {**EMPTY_PROFILE, "summary": "Updated summary"}
    service.put(new_profile)
    assert service.get()["summary"] == "Updated summary"


def test_patch_section(tmp_path):
    profile_path = tmp_path / ".profile.json"
    service = ProfileService(profile_path)
    service.patch("skills", [{"name": "Python", "proficiency": "advanced", "category": "technical"}])
    profile = service.get()
    assert len(profile["skills"]) == 1
    assert profile["skills"][0]["name"] == "Python"


def test_patch_invalid_section(tmp_path):
    profile_path = tmp_path / ".profile.json"
    service = ProfileService(profile_path)
    try:
        service.patch("invalid", "data")
        assert False, "Should have raised"
    except KeyError:
        pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_profile_service.py -v`
Expected: FAIL

- [ ] **Step 3: Implement ProfileService**

```python
# backend/services/profile.py
import json
from pathlib import Path
from threading import Lock

VALID_SECTIONS = {"summary", "skills", "experience", "education", "certifications", "objectives"}

EMPTY_PROFILE = {
    "summary": "",
    "skills": [],
    "experience": [],
    "education": [],
    "certifications": [],
    "objectives": "",
}


class ProfileService:
    def __init__(self, profile_path: Path):
        self.profile_path = profile_path
        self._lock = Lock()

    def get(self) -> dict:
        with self._lock:
            if not self.profile_path.exists():
                self._write(dict(EMPTY_PROFILE))
            return json.loads(self.profile_path.read_text())

    def put(self, profile: dict):
        with self._lock:
            self._write(profile)

    def patch(self, section: str, data) -> dict:
        if section not in VALID_SECTIONS:
            raise KeyError(f"Invalid section: {section}")
        with self._lock:
            profile = json.loads(self.profile_path.read_text()) if self.profile_path.exists() else dict(EMPTY_PROFILE)
            profile[section] = data
            self._write(profile)
            return profile

    def _write(self, data: dict):
        self.profile_path.write_text(json.dumps(data, indent=2))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_profile_service.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add backend/services/profile.py backend/tests/test_profile_service.py
git commit -m "feat: add ProfileService for profile JSON read/write/patch"
```

---

### Task 16: Profile API Endpoints

**Files:**
- Create: `backend/routers/profile.py`
- Create: `backend/tests/test_profile_api.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_profile_api.py
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.profile import ProfileService
import backend.config as config


def setup_test_env(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    config.DOCUMENTS_DIR = docs_dir
    config.PROFILE_PATH = docs_dir / ".profile.json"
    from backend.routers import profile
    profile._profile_service = ProfileService(config.PROFILE_PATH)


def test_get_profile_returns_scaffold(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == ""
    assert data["skills"] == []


def test_put_profile(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    profile = {"summary": "Engineer", "skills": [], "experience": [],
               "education": [], "certifications": [], "objectives": ""}
    response = client.put("/api/profile", json=profile)
    assert response.status_code == 200
    get_response = client.get("/api/profile")
    assert get_response.json()["summary"] == "Engineer"


def test_patch_section(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.get("/api/profile")  # init
    response = client.patch("/api/profile/skills", json=[{"name": "Python", "proficiency": "advanced", "category": "technical"}])
    assert response.status_code == 200
    assert len(response.json()["skills"]) == 1


def test_patch_invalid_section(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.patch("/api/profile/invalid", json="data")
    assert response.status_code == 400
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_profile_api.py -v`
Expected: FAIL

- [ ] **Step 3: Implement profile router**

```python
# backend/routers/profile.py
from fastapi import APIRouter, HTTPException, Request
from backend.config import PROFILE_PATH
from backend.services.profile import ProfileService

router = APIRouter(prefix="/api/profile", tags=["profile"])

_profile_service: ProfileService | None = None


def get_service() -> ProfileService:
    global _profile_service
    if _profile_service is None:
        _profile_service = ProfileService(PROFILE_PATH)
    return _profile_service


@router.get("")
async def get_profile():
    return get_service().get()


@router.put("")
async def put_profile(request: Request):
    body = await request.json()
    get_service().put(body)
    return get_service().get()


@router.patch("/{section}")
async def patch_section(section: str, request: Request):
    body = await request.json()
    try:
        return get_service().patch(section, body)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid section: {section}")
```

- [ ] **Step 4: Register router in main.py**

Add to `backend/main.py`:
```python
from backend.routers.profile import router as profile_router
app.include_router(profile_router)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_profile_api.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add backend/routers/profile.py backend/tests/test_profile_api.py backend/main.py
git commit -m "feat: add profile API endpoints for get, put, and patch"
```

---

### Task 17: Interview Service and Endpoints

**Files:**
- Create: `backend/services/interview.py`
- Create: `backend/routers/interview.py`
- Create: `backend/tests/test_interview_api.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write failing tests with mocked Claude API**

```python
# backend/tests/test_interview_api.py
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.profile import ProfileService
from backend.services.metadata import MetadataService
import backend.config as config


def setup_test_env(tmp_path):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    config.DOCUMENTS_DIR = docs_dir
    config.PROFILE_PATH = docs_dir / ".profile.json"
    from backend.routers import profile, interview, documents
    documents._metadata_service = MetadataService(docs_dir)
    profile._profile_service = ProfileService(config.PROFILE_PATH)
    interview._metadata_service = documents._metadata_service
    interview._profile_service = profile._profile_service
    interview._sessions = {}


def mock_claude_response(text, suggestion=None):
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text=text)]
    return mock_msg


@patch("backend.services.interview.get_claude_client")
def test_start_interview(mock_client, tmp_path):
    setup_test_env(tmp_path)
    mock_instance = MagicMock()
    mock_instance.messages.create.return_value = mock_claude_response("Hello! Let me review your documents.")
    mock_client.return_value = mock_instance

    client = TestClient(app)
    response = client.post("/api/interview/start")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "message" in data


@patch("backend.services.interview.get_claude_client")
def test_send_message(mock_client, tmp_path):
    setup_test_env(tmp_path)
    mock_instance = MagicMock()
    mock_instance.messages.create.return_value = mock_claude_response("Great question!")
    mock_client.return_value = mock_instance

    client = TestClient(app)
    start = client.post("/api/interview/start")
    session_id = start.json()["session_id"]

    response = client.post("/api/interview/message", json={"session_id": session_id, "message": "Tell me about my skills"})
    assert response.status_code == 200
    assert "message" in response.json()


def test_message_invalid_session(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/interview/message", json={"session_id": "invalid", "message": "hello"})
    assert response.status_code == 404
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_interview_api.py -v`
Expected: FAIL

- [ ] **Step 3: Implement interview service**

```python
# backend/services/interview.py
import uuid
import json
from pathlib import Path
from backend.config import ANTHROPIC_API_KEY

_sessions: dict = {}


def get_claude_client():
    import anthropic
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


SYSTEM_PROMPT = """You are a career profile interview assistant for hAId-hunter, a job application tool.

Your job is to help the user build a comprehensive candidate profile by:
1. Reviewing their uploaded documents (provided below)
2. Asking targeted follow-up questions to fill gaps and add detail
3. Proposing structured updates to their profile

When you want to suggest a profile update, include a JSON block in your response like:
```suggestion
{
  "suggestion_id": "sug_<random>",
  "section": "experience|skills|education|certifications|summary|objectives",
  "action": "add|update|remove",
  "target": { ... },
  "original": "...",
  "proposed": "..."
}
```

Focus on:
- Quantifiable accomplishments (numbers, percentages, team sizes)
- Technologies and tools used
- Impact and scope of work
- Leadership and collaboration examples
- Details that differentiate them from other candidates

Be conversational but focused. One question at a time. Base your questions on what you see in their documents and current profile."""


def read_document_contents(docs_dir: Path, metadata: dict) -> str:
    contents = []
    for file_id, meta in metadata.get("files", {}).items():
        mime = meta.get("mime_type", "")
        if mime in ("text/plain", "text/markdown", "text/csv"):
            file_path = docs_dir / meta["stored_name"]
            if file_path.exists():
                text = file_path.read_text(errors="ignore")
                contents.append(f"--- {meta['original_name']} ---\n{text[:5000]}")
    return "\n\n".join(contents) if contents else "No previewable documents found."


def start_session(profile: dict, doc_contents: str) -> tuple[str, str]:
    session_id = f"sess_{uuid.uuid4().hex[:12]}"

    messages = []
    system = f"{SYSTEM_PROMPT}\n\n## Current Profile\n```json\n{json.dumps(profile, indent=2)}\n```\n\n## Document Contents\n{doc_contents}"

    client = get_claude_client()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": "Please review my documents and profile, then start asking me questions to help build out my candidate profile."}],
    )

    assistant_msg = response.content[0].text
    messages.append({"role": "user", "content": "Please review my documents and profile, then start asking me questions to help build out my candidate profile."})
    messages.append({"role": "assistant", "content": assistant_msg})

    _sessions[session_id] = {
        "system": system,
        "messages": messages,
        "suggestions": {},
    }

    return session_id, assistant_msg


def send_message(session_id: str, user_message: str) -> dict:
    if session_id not in _sessions:
        raise KeyError(f"Session {session_id} not found")

    session = _sessions[session_id]
    session["messages"].append({"role": "user", "content": user_message})

    client = get_claude_client()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=session["system"],
        messages=session["messages"],
    )

    assistant_msg = response.content[0].text
    session["messages"].append({"role": "assistant", "content": assistant_msg})

    # Parse suggestion if present
    suggestion = None
    if "```suggestion" in assistant_msg:
        try:
            start = assistant_msg.index("```suggestion") + len("```suggestion")
            end = assistant_msg.index("```", start)
            suggestion = json.loads(assistant_msg[start:end].strip())
            session["suggestions"][suggestion["suggestion_id"]] = suggestion
        except (ValueError, json.JSONDecodeError, KeyError):
            pass

    return {"message": assistant_msg, "suggestion": suggestion}


def get_suggestion(session_id: str, suggestion_id: str) -> dict | None:
    if session_id not in _sessions:
        raise KeyError(f"Session {session_id} not found")
    return _sessions[session_id]["suggestions"].get(suggestion_id)
```

- [ ] **Step 4: Implement interview router**

```python
# backend/routers/interview.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.config import DOCUMENTS_DIR, PROFILE_PATH
from backend.services.metadata import MetadataService
from backend.services.profile import ProfileService
from backend.services import interview as interview_service

router = APIRouter(prefix="/api/interview", tags=["interview"])

_metadata_service: MetadataService | None = None
_profile_service: ProfileService | None = None


def get_metadata_service() -> MetadataService:
    global _metadata_service
    if _metadata_service is None:
        _metadata_service = MetadataService(DOCUMENTS_DIR)
    return _metadata_service


def get_profile_service() -> ProfileService:
    global _profile_service
    if _profile_service is None:
        _profile_service = ProfileService(PROFILE_PATH)
    return _profile_service


class MessageRequest(BaseModel):
    session_id: str
    message: str


class SuggestionRequest(BaseModel):
    session_id: str
    suggestion_id: str


@router.post("/start")
async def start_interview():
    profile = get_profile_service().get()
    metadata = get_metadata_service().read()
    doc_contents = interview_service.read_document_contents(DOCUMENTS_DIR, metadata)
    session_id, message = interview_service.start_session(profile, doc_contents)
    return {"session_id": session_id, "message": message}


@router.post("/message")
async def send_message(body: MessageRequest):
    try:
        result = interview_service.send_message(body.session_id, body.message)
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")


@router.post("/accept")
async def accept_suggestion(body: SuggestionRequest):
    try:
        suggestion = interview_service.get_suggestion(body.session_id, body.suggestion_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    service = get_profile_service()
    profile = service.get()
    section = suggestion["section"]
    action = suggestion["action"]
    target = suggestion.get("target", {})

    if action == "add" and isinstance(profile.get(section), list):
        profile[section].append(suggestion["proposed"])
    elif action == "update":
        if section in ("summary", "objectives"):
            profile[section] = suggestion["proposed"]
        elif isinstance(profile.get(section), list):
            # Update a specific item in a list section (e.g., experience, skills)
            index = target.get("index")
            field = target.get("field")
            if index is not None and 0 <= index < len(profile[section]):
                if field:
                    # Update a specific field within an item (e.g., accomplishments[0])
                    item = profile[section][index]
                    if isinstance(item, dict) and field in item:
                        sub_index = target.get("sub_index")
                        if sub_index is not None and isinstance(item[field], list):
                            item[field][sub_index] = suggestion["proposed"]
                        else:
                            item[field] = suggestion["proposed"]
                else:
                    # Replace the entire item at index
                    profile[section][index] = suggestion["proposed"]
    elif action == "remove" and isinstance(profile.get(section), list):
        index = target.get("index")
        if index is not None and 0 <= index < len(profile[section]):
            profile[section].pop(index)

    service.put(profile)
    return {"status": "accepted", "profile": profile}


@router.post("/reject")
async def reject_suggestion(body: SuggestionRequest):
    return {"status": "rejected"}
```

- [ ] **Step 5: Register router in main.py**

Add to `backend/main.py`:
```python
from backend.routers.interview import router as interview_router
app.include_router(interview_router)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_interview_api.py -v`
Expected: All PASS

- [ ] **Step 7: Commit**

```bash
git add backend/services/interview.py backend/routers/interview.py backend/tests/test_interview_api.py backend/main.py
git commit -m "feat: add interview service and API endpoints with Claude integration"
```

---

## Phase 5: Profile View — Frontend

### Task 18: Profile API Client + ProfileView Layout

**Files:**
- Create: `src/api/profile.ts`
- Create: `src/api/interview.ts`
- Modify: `src/components/profile/ProfileView.tsx`
- Create: `src/components/profile/ProfilePanel.tsx`
- Create: `src/components/profile/ProfileSection.tsx`
- Create: `src/components/profile/InterviewChat.tsx`
- Create: `src/__tests__/profile/ProfileView.test.tsx`

- [ ] **Step 1: Create API clients**

```typescript
// src/api/profile.ts
export interface Skill { name: string; proficiency: string; category: string }
export interface Experience { company: string; role: string; start_date: string; end_date: string | null; accomplishments: string[] }
export interface Education { institution: string; degree: string; start_date: string; end_date: string }
export interface Certification { name: string; issuer: string; date: string }

export interface Profile {
  summary: string
  skills: Skill[]
  experience: Experience[]
  education: Education[]
  certifications: Certification[]
  objectives: string
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
```

```typescript
// src/api/interview.ts
export interface Suggestion {
  suggestion_id: string
  section: string
  action: string
  target: Record<string, unknown>
  original: string | null
  proposed: string | null
}

export interface InterviewMessage {
  message: string
  suggestion?: Suggestion | null
}

export async function startInterview(): Promise<{ session_id: string; message: string }> {
  const res = await fetch('/api/interview/start', { method: 'POST' })
  if (!res.ok) throw new Error('Failed to start interview')
  return res.json()
}

export async function sendMessage(sessionId: string, message: string): Promise<InterviewMessage> {
  const res = await fetch('/api/interview/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
  })
  if (!res.ok) throw new Error('Failed to send message')
  return res.json()
}

export async function acceptSuggestion(sessionId: string, suggestionId: string): Promise<void> {
  const res = await fetch('/api/interview/accept', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, suggestion_id: suggestionId }),
  })
  if (!res.ok) throw new Error('Failed to accept suggestion')
}

export async function rejectSuggestion(sessionId: string, suggestionId: string): Promise<void> {
  const res = await fetch('/api/interview/reject', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, suggestion_id: suggestionId }),
  })
  if (!res.ok) throw new Error('Failed to reject suggestion')
}
```

- [ ] **Step 2: Write failing test for ProfileView**

```typescript
// src/__tests__/profile/ProfileView.test.tsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ProfileView from '../../components/profile/ProfileView'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ summary: '', skills: [], experience: [], education: [], certifications: [], objectives: '' }),
  }))
})

describe('ProfileView', () => {
  it('renders profile panel', async () => {
    render(<ProfileView />)
    expect(await screen.findByTestId('profile-panel')).toBeInTheDocument()
  })

  it('renders interview chat', async () => {
    render(<ProfileView />)
    expect(await screen.findByTestId('interview-chat')).toBeInTheDocument()
  })

  it('renders page title', async () => {
    render(<ProfileView />)
    expect(await screen.findByText('Profile')).toBeInTheDocument()
  })
})
```

- [ ] **Step 3: Run test to verify it fails**

Run: `npm test -- src/__tests__/profile/ProfileView.test.tsx`
Expected: FAIL

- [ ] **Step 4: Implement ProfileView (top-level layout)**

```tsx
// src/components/profile/ProfileView.tsx
import { useState, useEffect } from 'react'
import { fetchProfile, type Profile } from '../../api/profile'
import ProfilePanel from './ProfilePanel'
import InterviewChat from './InterviewChat'

export default function ProfileView() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [chatCollapsed, setChatCollapsed] = useState(false)

  useEffect(() => {
    fetchProfile().then(setProfile)
  }, [])

  const handleProfileUpdate = () => {
    fetchProfile().then(setProfile)
  }

  return (
    <div className="profile-view">
      <h1>Profile</h1>
      <div className="profile-layout">
        <div className="profile-main" data-testid="profile-panel">
          {profile && <ProfilePanel profile={profile} onUpdate={handleProfileUpdate} />}
        </div>
        <div className={`profile-chat ${chatCollapsed ? 'collapsed' : ''}`} data-testid="interview-chat">
          <button className="chat-toggle" onClick={() => setChatCollapsed(!chatCollapsed)}>
            {chatCollapsed ? '◀' : '▶'}
          </button>
          {!chatCollapsed && <InterviewChat onProfileUpdate={handleProfileUpdate} />}
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Implement ProfilePanel and ProfileSection**

```tsx
// src/components/profile/ProfileSection.tsx
import { useState, type ReactNode } from 'react'

interface Props {
  title: string
  children: ReactNode
  editor?: ReactNode
}

export default function ProfileSection({ title, children, editor }: Props) {
  const [editing, setEditing] = useState(false)

  return (
    <div className="profile-section">
      <div className="section-header">
        <h3>{title}</h3>
        <button onClick={() => setEditing(!editing)}>{editing ? 'Cancel' : 'Edit'}</button>
      </div>
      {editing ? editor : children}
    </div>
  )
}
```

```tsx
// src/components/profile/ProfilePanel.tsx
import type { Profile } from '../../api/profile'
import ProfileSection from './ProfileSection'
import SkillChips from './SkillChips'
import ExperienceList from './ExperienceList'
import EducationList from './EducationList'
import CertificationList from './CertificationList'

interface Props {
  profile: Profile
  onUpdate: () => void
}

export default function ProfilePanel({ profile, onUpdate }: Props) {
  return (
    <div className="profile-panel-inner">
      <ProfileSection title="Summary">
        <p>{profile.summary || 'No summary yet.'}</p>
      </ProfileSection>
      <ProfileSection title="Skills">
        <SkillChips skills={profile.skills} />
      </ProfileSection>
      <ProfileSection title="Experience">
        <ExperienceList experience={profile.experience} />
      </ProfileSection>
      <ProfileSection title="Education">
        <EducationList education={profile.education} />
      </ProfileSection>
      <ProfileSection title="Certifications">
        <CertificationList certifications={profile.certifications} />
      </ProfileSection>
      <ProfileSection title="Objectives">
        <p>{profile.objectives || 'No objectives yet.'}</p>
      </ProfileSection>
    </div>
  )
}
```

- [ ] **Step 6: Implement display components (SkillChips, ExperienceList, EducationList, CertificationList)**

```tsx
// src/components/profile/SkillChips.tsx
import type { Skill } from '../../api/profile'

const PROFICIENCY_CLASSES: Record<string, string> = {
  beginner: 'badge-muted',
  intermediate: 'badge-accent',
  advanced: 'badge-success',
  expert: 'badge-secondary',
}

export default function SkillChips({ skills }: { skills: Skill[] }) {
  if (skills.length === 0) return <p>No skills added yet.</p>
  return (
    <div className="skill-chips">
      {skills.map((s, i) => (
        <span key={i} className="skill-chip">
          {s.name}
          <span className={`proficiency-badge ${PROFICIENCY_CLASSES[s.proficiency] || ''}`}>
            {s.proficiency}
          </span>
        </span>
      ))}
    </div>
  )
}
```

```tsx
// src/components/profile/ExperienceList.tsx
import type { Experience } from '../../api/profile'

export default function ExperienceList({ experience }: { experience: Experience[] }) {
  if (experience.length === 0) return <p>No experience added yet.</p>
  return (
    <div className="experience-list">
      {experience.map((e, i) => (
        <div key={i} className="experience-item">
          <div className="experience-header">
            <strong>{e.role}</strong> at {e.company}
            <span className="experience-dates">{e.start_date} — {e.end_date || 'Present'}</span>
          </div>
          {e.accomplishments.length > 0 && (
            <ul>{e.accomplishments.map((a, j) => <li key={j}>{a}</li>)}</ul>
          )}
        </div>
      ))}
    </div>
  )
}
```

```tsx
// src/components/profile/EducationList.tsx
import type { Education } from '../../api/profile'

export default function EducationList({ education }: { education: Education[] }) {
  if (education.length === 0) return <p>No education added yet.</p>
  return (
    <div className="education-list">
      {education.map((e, i) => (
        <div key={i} className="education-item">
          <strong>{e.degree}</strong> — {e.institution}
          <span className="education-dates">{e.start_date} — {e.end_date}</span>
        </div>
      ))}
    </div>
  )
}
```

```tsx
// src/components/profile/CertificationList.tsx
import type { Certification } from '../../api/profile'

export default function CertificationList({ certifications }: { certifications: Certification[] }) {
  if (certifications.length === 0) return <p>No certifications added yet.</p>
  return (
    <div className="certification-list">
      {certifications.map((c, i) => (
        <div key={i} className="certification-item">
          <strong>{c.name}</strong> — {c.issuer} ({c.date})
        </div>
      ))}
    </div>
  )
}
```

- [ ] **Step 7: Implement InterviewChat, ChatMessage, and SuggestionCard**

```tsx
// src/components/profile/ChatMessage.tsx
interface Props {
  role: 'user' | 'assistant'
  content: string
}

export default function ChatMessage({ role, content }: Props) {
  return <div className={`chat-message ${role}`}>{content}</div>
}
```

```tsx
// src/components/profile/SuggestionCard.tsx
import type { Suggestion } from '../../api/interview'

interface Props {
  suggestion: Suggestion
  onAccept: (id: string) => void
  onReject: (id: string) => void
}

export default function SuggestionCard({ suggestion, onAccept, onReject }: Props) {
  return (
    <div className="suggestion-card">
      <div className="suggestion-header">
        Suggested {suggestion.action} for <strong>{suggestion.section}</strong>
      </div>
      {suggestion.original && (
        <div className="suggestion-original">
          <label>Current:</label>
          <p>{typeof suggestion.original === 'string' ? suggestion.original : JSON.stringify(suggestion.original)}</p>
        </div>
      )}
      {suggestion.proposed && (
        <div className="suggestion-proposed">
          <label>Proposed:</label>
          <p>{typeof suggestion.proposed === 'string' ? suggestion.proposed : JSON.stringify(suggestion.proposed)}</p>
        </div>
      )}
      <div className="suggestion-actions">
        <button className="btn-accept" onClick={() => onAccept(suggestion.suggestion_id)}>Accept</button>
        <button className="btn-reject" onClick={() => onReject(suggestion.suggestion_id)}>Reject</button>
      </div>
    </div>
  )
}
```

```tsx
// src/components/profile/InterviewChat.tsx
import { useState, useRef, useEffect } from 'react'
import { startInterview, sendMessage, acceptSuggestion, rejectSuggestion, type Suggestion } from '../../api/interview'
import ChatMessage from './ChatMessage'
import SuggestionCard from './SuggestionCard'

interface ChatEntry {
  role: 'user' | 'assistant'
  content: string
  suggestion?: Suggestion | null
}

interface Props {
  onProfileUpdate: () => void
}

export default function InterviewChat({ onProfileUpdate }: Props) {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatEntry[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleStart = async () => {
    setLoading(true)
    const { session_id, message } = await startInterview()
    setSessionId(session_id)
    setMessages([{ role: 'assistant', content: message }])
    setLoading(false)
  }

  const handleSend = async () => {
    if (!sessionId || !input.trim()) return
    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)
    const result = await sendMessage(sessionId, userMsg)
    setMessages(prev => [...prev, { role: 'assistant', content: result.message, suggestion: result.suggestion }])
    setLoading(false)
  }

  const handleAccept = async (suggestionId: string) => {
    if (!sessionId) return
    await acceptSuggestion(sessionId, suggestionId)
    onProfileUpdate()
  }

  const handleReject = async (suggestionId: string) => {
    if (!sessionId) return
    await rejectSuggestion(sessionId, suggestionId)
  }

  return (
    <div className="interview-chat-inner">
      <h3>Interview</h3>
      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={i}>
            <ChatMessage role={m.role} content={m.content} />
            {m.suggestion && (
              <SuggestionCard suggestion={m.suggestion} onAccept={handleAccept} onReject={handleReject} />
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      {!sessionId ? (
        <button onClick={handleStart} disabled={loading}>Start Interview</button>
      ) : (
        <div className="chat-input">
          <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleSend()} placeholder="Type a message..." />
          <button onClick={handleSend} disabled={loading || !input.trim()}>Send</button>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 8: Implement SectionEditor**

```tsx
// src/components/profile/SectionEditor.tsx
import { useState } from 'react'
import { patchSection } from '../../api/profile'
import type { Profile, Skill, Experience, Education, Certification } from '../../api/profile'

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
                <button onClick={() => { item.accomplishments.splice(j, 1); setValue([...items]) }}>×</button>
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

- [ ] **Step 5: Add CSS for profile view**

Append to `src/index.css` — profile layout, section cards, chat panel, suggestion cards, skill chips. Follow the styles from the mockup.

- [ ] **Step 6: Run all profile tests**

Run: `npm test -- src/__tests__/profile/`
Expected: All PASS

- [ ] **Step 7: Commit**

```bash
git add src/components/profile/ src/__tests__/profile/ src/api/profile.ts src/api/interview.ts src/index.css
git commit -m "feat: add ProfileView with sections, interview chat, and suggestion cards"
```

---

## Phase 6: Application Manager — Backend

### Task 19: Encryption Service

**Files:**
- Create: `backend/services/encryption.py`
- Create: `backend/tests/test_encryption.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_encryption.py
from backend.services.encryption import EncryptionService


def test_encrypt_decrypt_roundtrip():
    service = EncryptionService()
    plaintext = "my-secret-password"
    encrypted = service.encrypt(plaintext)
    assert encrypted != plaintext
    assert service.decrypt(encrypted) == plaintext


def test_encrypt_returns_different_ciphertext():
    service = EncryptionService()
    a = service.encrypt("password")
    b = service.encrypt("password")
    # Fernet uses random IV, so same plaintext -> different ciphertext
    assert a != b


def test_encrypt_none_returns_none():
    service = EncryptionService()
    assert service.encrypt(None) is None
    assert service.decrypt(None) is None


def test_mask():
    assert EncryptionService.mask("anything") == "***"
    assert EncryptionService.mask(None) is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_encryption.py -v`
Expected: FAIL

- [ ] **Step 3: Implement EncryptionService**

```python
# backend/services/encryption.py
from cryptography.fernet import Fernet
from backend.config import ENCRYPTION_KEY
from pathlib import Path
import os


class EncryptionService:
    def __init__(self, key: str | None = None):
        if key is None:
            key = ENCRYPTION_KEY
        if key is None:
            key = Fernet.generate_key().decode()
            # Write to .env
            env_path = Path(__file__).parent.parent.parent / ".env"
            with open(env_path, "a") as f:
                f.write(f"\nENCRYPTION_KEY={key}\n")
        self._fernet = Fernet(key.encode() if isinstance(key, str) else key)

    def encrypt(self, plaintext: str | None) -> str | None:
        if plaintext is None:
            return None
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str | None) -> str | None:
        if ciphertext is None:
            return None
        return self._fernet.decrypt(ciphertext.encode()).decode()

    @staticmethod
    def mask(value: str | None) -> str | None:
        if value is None:
            return None
        return "***"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_encryption.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add backend/services/encryption.py backend/tests/test_encryption.py
git commit -m "feat: add EncryptionService with Fernet encrypt/decrypt"
```

---

### Task 20: Database Service

**Files:**
- Create: `backend/services/database.py`
- Create: `backend/tests/test_database.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_database.py
import sqlite3
from backend.services.database import init_db, get_connection


def test_init_creates_tables(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    assert "applications" in tables
    assert "application_documents" in tables
    conn.close()


def test_insert_and_read_application(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        INSERT INTO applications (company, position, status, created_at, updated_at)
        VALUES (?, ?, ?, datetime('now'), datetime('now'))
    """, ("Acme", "Engineer", "bookmarked"))
    conn.commit()
    row = conn.execute("SELECT company, position, status FROM applications").fetchone()
    assert row == ("Acme", "Engineer", "bookmarked")
    conn.close()


def test_cascade_delete(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("""
        INSERT INTO applications (company, position, status, created_at, updated_at)
        VALUES (?, ?, ?, datetime('now'), datetime('now'))
    """, ("Acme", "Engineer", "applied"))
    conn.commit()
    app_id = conn.execute("SELECT id FROM applications").fetchone()[0]
    conn.execute("INSERT INTO application_documents (application_id, document_id, role) VALUES (?, ?, ?)",
                 (app_id, "doc123", "resume"))
    conn.commit()
    conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    conn.commit()
    docs = conn.execute("SELECT * FROM application_documents WHERE application_id = ?", (app_id,)).fetchall()
    assert len(docs) == 0
    conn.close()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_database.py -v`
Expected: FAIL

- [ ] **Step 3: Implement database service**

```python
# backend/services/database.py
import sqlite3
from pathlib import Path
from backend.config import DATABASE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    position TEXT NOT NULL,
    posting_url TEXT,
    login_page_url TEXT,
    login_email TEXT,
    login_password TEXT,
    status TEXT NOT NULL DEFAULT 'bookmarked',
    closed_reason TEXT,
    has_referral BOOLEAN DEFAULT 0,
    referral_name TEXT,
    notes TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS application_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    document_id TEXT NOT NULL,
    role TEXT,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);
"""


def init_db(db_path: Path | None = None):
    path = db_path or DATABASE_PATH
    path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    conn.close()


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DATABASE_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_database.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add backend/services/database.py backend/tests/test_database.py
git commit -m "feat: add SQLite database service with schema init"
```

---

### Task 21: Application API Endpoints

**Files:**
- Create: `backend/routers/applications.py`
- Create: `backend/tests/test_applications_api.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_applications_api.py
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.database import init_db, get_connection
from backend.services.encryption import EncryptionService
import backend.config as config
from cryptography.fernet import Fernet


def setup_test_env(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    key = Fernet.generate_key().decode()
    config.ENCRYPTION_KEY = key
    from backend.routers import applications
    applications._db_path = db_path
    applications._encryption = EncryptionService(key)


def test_list_applications_empty(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.get("/api/applications")
    assert response.status_code == 200
    assert response.json() == []


def test_create_application(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    response = client.post("/api/applications", json={
        "company": "Acme", "position": "Engineer", "status": "bookmarked"
    })
    assert response.status_code == 200
    assert response.json()["company"] == "Acme"
    assert response.json()["id"] is not None


def test_get_application(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={"company": "Acme", "position": "Engineer", "status": "applied"})
    app_id = create.json()["id"]
    response = client.get(f"/api/applications/{app_id}")
    assert response.status_code == 200
    assert response.json()["company"] == "Acme"


def test_credentials_masked_by_default(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={
        "company": "Acme", "position": "Engineer", "status": "applied",
        "login_email": "user@test.com", "login_password": "secret123"
    })
    app_id = create.json()["id"]
    response = client.get(f"/api/applications/{app_id}")
    assert response.json()["login_email"] == "***"
    assert response.json()["login_password"] == "***"


def test_credentials_revealed(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={
        "company": "Acme", "position": "Engineer", "status": "applied",
        "login_email": "user@test.com", "login_password": "secret123"
    })
    app_id = create.json()["id"]
    response = client.get(f"/api/applications/{app_id}?reveal_credentials=true")
    assert response.json()["login_email"] == "user@test.com"
    assert response.json()["login_password"] == "secret123"


def test_update_application(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={"company": "Acme", "position": "Engineer", "status": "bookmarked"})
    app_id = create.json()["id"]
    response = client.put(f"/api/applications/{app_id}", json={"company": "Acme Corp", "position": "Senior Engineer", "status": "applied"})
    assert response.status_code == 200
    assert response.json()["company"] == "Acme Corp"


def test_delete_application(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={"company": "Acme", "position": "Engineer", "status": "bookmarked"})
    app_id = create.json()["id"]
    response = client.delete(f"/api/applications/{app_id}")
    assert response.status_code == 200
    listing = client.get("/api/applications")
    assert len(listing.json()) == 0


def test_patch_status(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={"company": "Acme", "position": "Engineer", "status": "bookmarked"})
    app_id = create.json()["id"]
    response = client.patch(f"/api/applications/{app_id}/status", json={"status": "applied"})
    assert response.status_code == 200
    assert response.json()["status"] == "applied"


def test_filter_by_status(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    client.post("/api/applications", json={"company": "A", "position": "E", "status": "bookmarked"})
    client.post("/api/applications", json={"company": "B", "position": "E", "status": "applied"})
    response = client.get("/api/applications?status=bookmarked")
    assert len(response.json()) == 1


def test_link_document(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={"company": "Acme", "position": "Engineer", "status": "applied"})
    app_id = create.json()["id"]
    response = client.post(f"/api/applications/{app_id}/documents", json={"document_id": "doc123", "role": "resume"})
    assert response.status_code == 200
    docs = client.get(f"/api/applications/{app_id}/documents")
    assert len(docs.json()) == 1


def test_unlink_document(tmp_path):
    setup_test_env(tmp_path)
    client = TestClient(app)
    create = client.post("/api/applications", json={"company": "Acme", "position": "Engineer", "status": "applied"})
    app_id = create.json()["id"]
    link = client.post(f"/api/applications/{app_id}/documents", json={"document_id": "doc123", "role": "resume"})
    link_id = link.json()["id"]
    response = client.delete(f"/api/applications/{app_id}/documents/{link_id}")
    assert response.status_code == 200
    docs = client.get(f"/api/applications/{app_id}/documents")
    assert len(docs.json()) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_applications_api.py -v`
Expected: FAIL

- [ ] **Step 3: Implement applications router**

```python
# backend/routers/applications.py
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.config import DATABASE_PATH
from backend.services.database import get_connection, init_db
from backend.services.encryption import EncryptionService
from pathlib import Path

router = APIRouter(prefix="/api/applications", tags=["applications"])

_db_path: Path | None = None
_encryption: EncryptionService | None = None


def get_db():
    global _db_path
    path = _db_path or DATABASE_PATH
    return get_connection(path)


def get_encryption() -> EncryptionService:
    global _encryption
    if _encryption is None:
        _encryption = EncryptionService()
    return _encryption


class CreateApplicationRequest(BaseModel):
    company: str
    position: str
    posting_url: str | None = None
    login_page_url: str | None = None
    login_email: str | None = None
    login_password: str | None = None
    status: str = "bookmarked"
    closed_reason: str | None = None
    has_referral: bool = False
    referral_name: str | None = None
    notes: str | None = None


class UpdateStatusRequest(BaseModel):
    status: str
    closed_reason: str | None = None


class LinkDocumentRequest(BaseModel):
    document_id: str
    role: str | None = None


def row_to_dict(row, reveal_credentials: bool = False) -> dict:
    enc = get_encryption()
    d = dict(row)
    if reveal_credentials:
        d["login_email"] = enc.decrypt(d.get("login_email"))
        d["login_password"] = enc.decrypt(d.get("login_password"))
    else:
        d["login_email"] = enc.mask(d.get("login_email"))
        d["login_password"] = enc.mask(d.get("login_password"))
    return d


@router.get("")
async def list_applications(status: str | None = None, search: str | None = None, has_referral: bool | None = None):
    conn = get_db()
    query = "SELECT * FROM applications WHERE 1=1"
    params: list = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if search:
        query += " AND (company LIKE ? OR position LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if has_referral is not None:
        query += " AND has_referral = ?"
        params.append(1 if has_referral else 0)
    query += " ORDER BY updated_at DESC"
    rows = conn.execute(query, params).fetchall()
    result = [row_to_dict(r) for r in rows]

    # Add doc count
    for item in result:
        count = conn.execute("SELECT COUNT(*) FROM application_documents WHERE application_id = ?", (item["id"],)).fetchone()[0]
        item["doc_count"] = count

    conn.close()
    return result


@router.get("/{app_id}")
async def get_application(app_id: int, reveal_credentials: bool = False):
    conn = get_db()
    row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Application not found")
    result = row_to_dict(row, reveal_credentials)

    docs = conn.execute("SELECT * FROM application_documents WHERE application_id = ?", (app_id,)).fetchall()
    result["documents"] = [dict(d) for d in docs]
    conn.close()
    return result


@router.post("")
async def create_application(body: CreateApplicationRequest):
    enc = get_encryption()
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO applications (company, position, posting_url, login_page_url, login_email, login_password,
                                  status, closed_reason, has_referral, referral_name, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (body.company, body.position, body.posting_url, body.login_page_url,
          enc.encrypt(body.login_email), enc.encrypt(body.login_password),
          body.status, body.closed_reason, body.has_referral, body.referral_name, body.notes, now, now))
    conn.commit()
    app_id = cursor.lastrowid
    row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    conn.close()
    return row_to_dict(row)


@router.put("/{app_id}")
async def update_application(app_id: int, body: CreateApplicationRequest):
    enc = get_encryption()
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    conn.execute("""
        UPDATE applications SET company=?, position=?, posting_url=?, login_page_url=?,
        login_email=?, login_password=?, status=?, closed_reason=?, has_referral=?,
        referral_name=?, notes=?, updated_at=? WHERE id=?
    """, (body.company, body.position, body.posting_url, body.login_page_url,
          enc.encrypt(body.login_email), enc.encrypt(body.login_password),
          body.status, body.closed_reason, body.has_referral, body.referral_name, body.notes, now, app_id))
    conn.commit()
    row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")
    return row_to_dict(row)


@router.delete("/{app_id}")
async def delete_application(app_id: int):
    conn = get_db()
    conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}


@router.patch("/{app_id}/status")
async def update_status(app_id: int, body: UpdateStatusRequest):
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    conn.execute("UPDATE applications SET status=?, closed_reason=?, updated_at=? WHERE id=?",
                 (body.status, body.closed_reason, now, app_id))
    conn.commit()
    row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")
    return row_to_dict(row)


@router.get("/{app_id}/documents")
async def list_linked_documents(app_id: int):
    conn = get_db()
    rows = conn.execute("SELECT * FROM application_documents WHERE application_id = ?", (app_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("/{app_id}/documents")
async def link_document(app_id: int, body: LinkDocumentRequest):
    conn = get_db()
    cursor = conn.execute("INSERT INTO application_documents (application_id, document_id, role) VALUES (?, ?, ?)",
                          (app_id, body.document_id, body.role))
    conn.commit()
    link_id = cursor.lastrowid
    conn.close()
    return {"id": link_id, "application_id": app_id, "document_id": body.document_id, "role": body.role}


@router.delete("/{app_id}/documents/{link_id}")
async def unlink_document(app_id: int, link_id: int):
    conn = get_db()
    conn.execute("DELETE FROM application_documents WHERE id = ? AND application_id = ?", (link_id, app_id))
    conn.commit()
    conn.close()
    return {"status": "unlinked"}
```

- [ ] **Step 4: Register router and init DB in main.py**

Add to `backend/main.py`:
```python
from backend.routers.applications import router as applications_router
from backend.services.database import init_db

app.include_router(applications_router)

# In startup event:
init_db()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_applications_api.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add backend/routers/applications.py backend/tests/test_applications_api.py backend/main.py
git commit -m "feat: add application API endpoints with encryption and document linking"
```

---

## Phase 7: Application Manager — Frontend

### Task 22: Application API Client + ApplicationManager Layout

**Files:**
- Create: `src/api/applications.ts`
- Modify: `src/components/applications/ApplicationManager.tsx`
- Create: `src/components/applications/ApplicationToolbar.tsx`
- Create: `src/components/applications/TableView.tsx`
- Create: `src/components/applications/KanbanView.tsx`
- Create: `src/components/applications/ApplicationModal.tsx`
- Create: `src/__tests__/applications/ApplicationManager.test.tsx`

- [ ] **Step 1: Create application API client**

```typescript
// src/api/applications.ts
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
```

- [ ] **Step 2: Write failing test**

```typescript
// src/__tests__/applications/ApplicationManager.test.tsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ApplicationManager from '../../components/applications/ApplicationManager'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => [] }))
})

describe('ApplicationManager', () => {
  it('renders page title', async () => {
    render(<ApplicationManager />)
    expect(await screen.findByText('Applications')).toBeInTheDocument()
  })

  it('renders toolbar with add button', async () => {
    render(<ApplicationManager />)
    expect(await screen.findByText(/add application/i)).toBeInTheDocument()
  })

  it('renders view toggle', async () => {
    render(<ApplicationManager />)
    expect(await screen.findByText(/table/i)).toBeInTheDocument()
    expect(await screen.findByText(/kanban/i)).toBeInTheDocument()
  })
})
```

- [ ] **Step 3: Run test to verify it fails**

Run: `npm test -- src/__tests__/applications/ApplicationManager.test.tsx`
Expected: FAIL

- [ ] **Step 4: Implement ApplicationManager and ApplicationToolbar**

```tsx
// src/components/applications/ApplicationToolbar.tsx
interface Props {
  search: string
  onSearchChange: (value: string) => void
  statusFilter: string
  onStatusFilterChange: (value: string) => void
  viewMode: 'table' | 'kanban'
  onViewModeChange: (mode: 'table' | 'kanban') => void
  onAdd: () => void
}

export default function ApplicationToolbar({ search, onSearchChange, statusFilter, onStatusFilterChange, viewMode, onViewModeChange, onAdd }: Props) {
  return (
    <div className="application-toolbar">
      <input type="text" value={search} onChange={e => onSearchChange(e.target.value)} placeholder="Search applications..." className="search-input" />
      <select value={statusFilter} onChange={e => onStatusFilterChange(e.target.value)}>
        <option value="">All Statuses</option>
        <option value="bookmarked">Bookmarked</option>
        <option value="applied">Applied</option>
        <option value="in_progress">In Progress</option>
        <option value="offer">Offer</option>
        <option value="closed">Closed</option>
      </select>
      <div className="view-toggle">
        <button className={viewMode === 'table' ? 'active' : ''} onClick={() => onViewModeChange('table')}>Table</button>
        <button className={viewMode === 'kanban' ? 'active' : ''} onClick={() => onViewModeChange('kanban')}>Kanban</button>
      </div>
      <button className="btn-primary" onClick={onAdd}>+ Add Application</button>
    </div>
  )
}
```

```tsx
// src/components/applications/ApplicationManager.tsx
import { useState, useEffect, useCallback } from 'react'
import { fetchApplications, type Application } from '../../api/applications'
import ApplicationToolbar from './ApplicationToolbar'
import TableView from './TableView'
import KanbanView from './KanbanView'
import ApplicationModal from './ApplicationModal'

export default function ApplicationManager() {
  const [applications, setApplications] = useState<Application[]>([])
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [viewMode, setViewMode] = useState<'table' | 'kanban'>('table')
  const [modalOpen, setModalOpen] = useState(false)
  const [editingApp, setEditingApp] = useState<Application | null>(null)

  const loadApps = useCallback(async () => {
    const apps = await fetchApplications({ search: search || undefined, status: statusFilter || undefined })
    setApplications(apps)
  }, [search, statusFilter])

  useEffect(() => { loadApps() }, [loadApps])

  const handleEdit = (app: Application) => { setEditingApp(app); setModalOpen(true) }
  const handleAdd = () => { setEditingApp(null); setModalOpen(true) }
  const handleModalClose = () => { setModalOpen(false); setEditingApp(null); loadApps() }

  return (
    <div className="application-manager">
      <h1>Applications</h1>
      <ApplicationToolbar search={search} onSearchChange={setSearch} statusFilter={statusFilter} onStatusFilterChange={setStatusFilter} viewMode={viewMode} onViewModeChange={setViewMode} onAdd={handleAdd} />
      {viewMode === 'table' ? (
        <TableView applications={applications} onRowClick={handleEdit} />
      ) : (
        <KanbanView applications={applications} onCardClick={handleEdit} onRefresh={loadApps} />
      )}
      {modalOpen && <ApplicationModal application={editingApp} onClose={handleModalClose} />}
    </div>
  )
}
```

- [ ] **Step 5: Implement TableView**

```tsx
// src/components/applications/TableView.tsx
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

  return (
    <table className="application-table">
      <thead>
        <tr>
          <th onClick={() => handleSort('company')}>Company</th>
          <th onClick={() => handleSort('position')}>Position</th>
          <th onClick={() => handleSort('status')}>Status</th>
          <th>Referral</th>
          <th>Docs</th>
          <th onClick={() => handleSort('created_at')}>Applied</th>
        </tr>
      </thead>
      <tbody>
        {sorted.map(app => (
          <tr key={app.id} onClick={() => onRowClick(app)}>
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
  )
}
```

```tsx
// src/components/applications/StatusBadge.tsx
const STATUS_CLASSES: Record<string, string> = {
  bookmarked: 'status-muted',
  applied: 'status-primary',
  in_progress: 'status-accent',
  offer: 'status-success',
  closed: 'status-error',
}

const STATUS_LABELS: Record<string, string> = {
  bookmarked: 'Bookmarked',
  applied: 'Applied',
  in_progress: 'In Progress',
  offer: 'Offer',
  closed: 'Closed',
}

export default function StatusBadge({ status }: { status: string }) {
  return <span className={`status-badge ${STATUS_CLASSES[status] || ''}`}>{STATUS_LABELS[status] || status}</span>
}
```

- [ ] **Step 6: Implement KanbanView, KanbanColumn, KanbanCard**

```tsx
// src/components/applications/KanbanCard.tsx
import type { Application } from '../../api/applications'

interface Props {
  application: Application
  onClick: (app: Application) => void
}

export default function KanbanCard({ application, onClick }: Props) {
  const handleDragStart = (e: React.DragEvent) => {
    e.dataTransfer.setData('application/json', JSON.stringify({ id: application.id }))
    e.dataTransfer.effectAllowed = 'move'
  }

  return (
    <div className={`kanban-card ${application.status === 'closed' ? 'dimmed' : ''}`} draggable onDragStart={handleDragStart} onClick={() => onClick(application)}>
      <div className="card-company">{application.company}</div>
      <div className="card-position">{application.position}</div>
      <div className="card-meta">
        {application.referral_name && <span className="referral-badge">{application.referral_name}</span>}
        <span className="card-date">{new Date(application.created_at).toLocaleDateString()}</span>
        {(application.doc_count ?? 0) > 0 && <span className="doc-count">{application.doc_count} docs</span>}
      </div>
    </div>
  )
}
```

```tsx
// src/components/applications/KanbanColumn.tsx
import type { Application } from '../../api/applications'
import KanbanCard from './KanbanCard'
import StatusBadge from './StatusBadge'

interface Props {
  status: string
  applications: Application[]
  onCardClick: (app: Application) => void
  onDrop: (appId: number, newStatus: string) => void
}

export default function KanbanColumn({ status, applications, onCardClick, onDrop }: Props) {
  const handleDragOver = (e: React.DragEvent) => { e.preventDefault(); e.dataTransfer.dropEffect = 'move' }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const data = JSON.parse(e.dataTransfer.getData('application/json'))
    onDrop(data.id, status)
  }

  return (
    <div className="kanban-column" onDragOver={handleDragOver} onDrop={handleDrop}>
      <div className="column-header">
        <StatusBadge status={status} />
        <span className="column-count">{applications.length}</span>
      </div>
      <div className="column-cards">
        {applications.map(app => <KanbanCard key={app.id} application={app} onClick={onCardClick} />)}
      </div>
    </div>
  )
}
```

```tsx
// src/components/applications/KanbanView.tsx
import { useState } from 'react'
import type { Application } from '../../api/applications'
import { updateApplicationStatus } from '../../api/applications'
import KanbanColumn from './KanbanColumn'

const STATUSES = ['bookmarked', 'applied', 'in_progress', 'offer', 'closed']

interface Props {
  applications: Application[]
  onCardClick: (app: Application) => void
  onRefresh: () => void
}

export default function KanbanView({ applications, onCardClick, onRefresh }: Props) {
  const [optimisticApps, setOptimisticApps] = useState<Application[] | null>(null)
  const displayApps = optimisticApps ?? applications

  const handleDrop = async (appId: number, newStatus: string) => {
    // Prompt for closed reason if dropping into closed
    let closedReason: string | undefined
    if (newStatus === 'closed') {
      closedReason = prompt('Select reason: rejected, withdrawn, accepted, ghosted') || undefined
      if (!closedReason) return
    }

    // Optimistic update
    const updated = applications.map(a => a.id === appId ? { ...a, status: newStatus } : a)
    setOptimisticApps(updated)

    try {
      await updateApplicationStatus(appId, newStatus, closedReason)
      setOptimisticApps(null)
      onRefresh()
    } catch {
      // Revert on failure
      setOptimisticApps(null)
    }
  }

  return (
    <div className="kanban-board">
      {STATUSES.map(status => (
        <KanbanColumn key={status} status={status} applications={displayApps.filter(a => a.status === status)} onCardClick={onCardClick} onDrop={handleDrop} />
      ))}
    </div>
  )
}
```

- [ ] **Step 7: Implement ApplicationModal with DocumentLinker and DocumentPicker**

```tsx
// src/components/applications/DocumentPicker.tsx
import { useState, useEffect } from 'react'
import { fetchDocuments, type DocumentMeta } from '../../api/documents'

interface Props {
  onSelect: (documentId: string) => void
  excludeIds: string[]
}

export default function DocumentPicker({ onSelect, excludeIds }: Props) {
  const [documents, setDocuments] = useState<DocumentMeta[]>([])

  useEffect(() => {
    fetchDocuments().then(docs => setDocuments(docs.filter(d => !excludeIds.includes(d.id))))
  }, [excludeIds])

  return (
    <select onChange={e => { if (e.target.value) onSelect(e.target.value) }} defaultValue="">
      <option value="" disabled>Select a document...</option>
      {documents.map(d => <option key={d.id} value={d.id}>{d.display_name}</option>)}
    </select>
  )
}
```

```tsx
// src/components/applications/DocumentLinker.tsx
import { useState, useEffect } from 'react'
import { fetchLinkedDocuments, linkDocument, unlinkDocument, type LinkedDocument } from '../../api/applications'
import DocumentPicker from './DocumentPicker'

interface Props {
  applicationId: number
}

export default function DocumentLinker({ applicationId }: Props) {
  const [links, setLinks] = useState<LinkedDocument[]>([])
  const [showPicker, setShowPicker] = useState(false)

  useEffect(() => { loadLinks() }, [applicationId])

  const loadLinks = async () => {
    const docs = await fetchLinkedDocuments(applicationId)
    setLinks(docs)
  }

  const handleLink = async (documentId: string) => {
    const role = prompt('Document role (e.g., resume, cover_letter):') || undefined
    await linkDocument(applicationId, documentId, role)
    setShowPicker(false)
    loadLinks()
  }

  const handleUnlink = async (linkId: number) => {
    await unlinkDocument(applicationId, linkId)
    loadLinks()
  }

  return (
    <div className="document-linker">
      <h4>Linked Documents</h4>
      {links.map(l => (
        <div key={l.id} className="linked-doc">
          <span>{l.document_id}</span>
          {l.role && <span className="doc-role">{l.role}</span>}
          <button onClick={() => handleUnlink(l.id)}>Remove</button>
        </div>
      ))}
      {showPicker ? (
        <DocumentPicker onSelect={handleLink} excludeIds={links.map(l => l.document_id)} />
      ) : (
        <button onClick={() => setShowPicker(true)}>+ Link Document</button>
      )}
    </div>
  )
}
```

```tsx
// src/components/applications/ApplicationModal.tsx
import { useState } from 'react'
import { createApplication, updateApplication, deleteApplication, type Application } from '../../api/applications'
import DocumentLinker from './DocumentLinker'

interface Props {
  application: Application | null
  onClose: () => void
}

export default function ApplicationModal({ application, onClose }: Props) {
  const isEdit = application !== null
  const [form, setForm] = useState({
    company: application?.company || '',
    position: application?.position || '',
    posting_url: application?.posting_url || '',
    login_page_url: application?.login_page_url || '',
    login_email: '',
    login_password: '',
    status: application?.status || 'bookmarked',
    closed_reason: application?.closed_reason || '',
    has_referral: application?.has_referral || false,
    referral_name: application?.referral_name || '',
    notes: application?.notes || '',
  })
  const [showPassword, setShowPassword] = useState(false)

  const handleChange = (field: string, value: string | boolean) => {
    setForm(prev => ({ ...prev, [field]: value }))
  }

  const handleSave = async () => {
    const data = { ...form, login_email: form.login_email || undefined, login_password: form.login_password || undefined, closed_reason: form.closed_reason || undefined, referral_name: form.referral_name || undefined, posting_url: form.posting_url || undefined, login_page_url: form.login_page_url || undefined, notes: form.notes || undefined }
    if (isEdit) await updateApplication(application!.id, data)
    else await createApplication(data)
    onClose()
  }

  const handleDelete = async () => {
    if (isEdit && confirm('Delete this application?')) {
      await deleteApplication(application!.id)
      onClose()
    }
  }

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal-content">
        <h2>{isEdit ? 'Edit Application' : 'Add Application'}</h2>
        <div className="modal-section">
          <div className="form-row">
            <input value={form.company} onChange={e => handleChange('company', e.target.value)} placeholder="Company" required />
            <input value={form.position} onChange={e => handleChange('position', e.target.value)} placeholder="Position" required />
          </div>
          <input value={form.posting_url} onChange={e => handleChange('posting_url', e.target.value)} placeholder="Posting URL" />
        </div>
        <div className="modal-section">
          <select value={form.status} onChange={e => handleChange('status', e.target.value)}>
            <option value="bookmarked">Bookmarked</option>
            <option value="applied">Applied</option>
            <option value="in_progress">In Progress</option>
            <option value="offer">Offer</option>
            <option value="closed">Closed</option>
          </select>
          {form.status === 'closed' && (
            <select value={form.closed_reason} onChange={e => handleChange('closed_reason', e.target.value)}>
              <option value="">Select reason...</option>
              <option value="rejected">Rejected</option>
              <option value="withdrawn">Withdrawn</option>
              <option value="accepted">Accepted</option>
              <option value="ghosted">Ghosted</option>
            </select>
          )}
          <label><input type="checkbox" checked={form.has_referral} onChange={e => handleChange('has_referral', e.target.checked)} /> Has Referral</label>
          {form.has_referral && <input value={form.referral_name} onChange={e => handleChange('referral_name', e.target.value)} placeholder="Referral name" />}
        </div>
        <div className="modal-section">
          <input value={form.login_page_url} onChange={e => handleChange('login_page_url', e.target.value)} placeholder="Login Page URL" />
          <input value={form.login_email} onChange={e => handleChange('login_email', e.target.value)} placeholder="Portal Email/Username" />
          <div className="password-field">
            <input type={showPassword ? 'text' : 'password'} value={form.login_password} onChange={e => handleChange('login_password', e.target.value)} placeholder="Portal Password" />
            <button type="button" onClick={() => setShowPassword(!showPassword)}>{showPassword ? 'Hide' : 'Show'}</button>
          </div>
        </div>
        {isEdit && application && (
          <div className="modal-section">
            <DocumentLinker applicationId={application.id} />
          </div>
        )}
        <div className="modal-section">
          <textarea value={form.notes} onChange={e => handleChange('notes', e.target.value)} placeholder="Notes..." rows={3} />
        </div>
        <div className="modal-footer">
          {isEdit && <button className="btn-danger" onClick={handleDelete}>Delete</button>}
          <button onClick={onClose}>Cancel</button>
          <button className="btn-primary" onClick={handleSave}>Save</button>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Add CSS for application manager**

Append to `src/index.css` — table styles, kanban board, modal, status badges. Follow patterns from the mockup.

- [ ] **Step 6: Run all application tests**

Run: `npm test -- src/__tests__/applications/`
Expected: All PASS

- [ ] **Step 7: Commit**

```bash
git add src/components/applications/ src/__tests__/applications/ src/api/applications.ts src/index.css
git commit -m "feat: add ApplicationManager with table view, kanban view, and modal"
```

---

## Phase 8: Integration + Cleanup

### Task 23: Final Integration Test

- [ ] **Step 1: Run all backend tests**

Run: `cd backend && python -m pytest -v`
Expected: All PASS

- [ ] **Step 2: Run all frontend tests**

Run: `npm test`
Expected: All PASS

- [ ] **Step 3: Manual smoke test**

Start both servers:
```bash
# Terminal 1
cd backend && uvicorn backend.main:app --reload --port 8000

# Terminal 2
npm run dev
```

Verify:
- Navigate to `/documents` — upload a file, tag it, preview it
- Navigate to `/profile` — see empty scaffold, edit sections manually
- Navigate to `/applications` — add an application, toggle table/kanban, drag between columns
- NavBar links work and highlight active route

- [ ] **Step 4: Commit any fixes**

```bash
git add -A
git commit -m "chore: integration fixes and final cleanup"
```

- [ ] **Step 5: Run build**

Run: `npm run build`
Expected: Build succeeds with no TypeScript errors

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "chore: Phase I complete — Document Manager, Profile View, Application Manager"
```
