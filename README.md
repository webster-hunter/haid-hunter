# hAId-hunter

A locally hosted job application management tool that helps you organize documents,
build a candidate profile, and track applications — optimized for the AI-driven
hiring landscape.

## Overview

hAId-hunter runs entirely on your local machine. It provides three core features:

- **Home Dashboard**: At-a-glance overview of your entire job search — profile
  banner, document and application statistics, referral contacts, and a
  user-defined task system with recurring and one-time tasks.
- **Document Manager**: Upload and tag resumes, cover letters, and supporting
  documents. Preview files in-browser and organize them with custom tags.
- **Profile View**: Build a structured candidate profile covering skills,
  experience, education, and certifications. A Claude-powered interview chat helps
  you refine your profile through guided questions, and document extraction
  automatically pulls skills and keywords from your uploaded files.
- **Job Posting Analysis**: Paste a job posting URL and get back key requirements,
  emphasis areas, and keywords — mapped against your profile.
- **Application Manager**: Track job applications with company details, posting
  URLs, portal credentials (encrypted at rest), status tracking, and linked
  documents. View applications in a sortable table or Kanban board.

## Prerequisites

- [Node.js](https://nodejs.org/) (v18 or later)
- [Python](https://www.python.org/) (3.12 or later)
- [Claude Code](https://claude.com/claude-code) (for AI features — interview chat,
  document extraction, and posting analysis)

## Set up

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/haid-hunter.git
   cd haid-hunter
   ```

2. Install frontend dependencies:

   ```bash
   npm install
   ```

3. Install backend dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root:

   ```text
   ENCRYPTION_KEY=your-fernet-key-here
   ```

   Generate a Fernet encryption key with Python:

   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

   The `ENCRYPTION_KEY` is required for encrypting application portal credentials.
   No separate API key is needed — AI features use your Claude Code subscription.

## Run the application

Start the backend and frontend servers from the project root.

Start the backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

In a separate terminal, start the frontend dev server:

```bash
npm run dev
```

Open `http://localhost:5173` in your browser.

The Vite dev server proxies API requests to the backend on port 8000 automatically.

## Project structure

```
haid-hunter/
├── backend/                 # FastAPI backend
│   ├── routers/             # API route handlers
│   │   ├── applications.py  # Application CRUD and document linking
│   │   ├── dashboard.py     # Aggregated dashboard endpoint
│   │   ├── documents.py     # Document upload, preview, and management
│   │   ├── interview.py     # Claude-powered interview chat
│   │   ├── profile.py       # Candidate profile endpoints
│   │   ├── settings.py      # User settings (key-value)
│   │   ├── tags.py          # Tag management
│   │   └── tasks.py         # User-defined task CRUD
│   ├── services/            # Business logic
│   │   ├── database.py      # SQLite connection and schema
│   │   ├── encryption.py    # Fernet encryption for credentials
│   │   ├── extraction.py    # Document skill/keyword extraction
│   │   ├── interview.py     # Interview session management (ClaudeSDKClient)
│   │   ├── metadata.py      # Document metadata tracking
│   │   ├── posting.py       # Job posting analysis
│   │   ├── profile.py       # Profile read/write operations
│   │   └── schema.py        # Auto-generated profile schema for LLM prompts
│   ├── tests/               # Backend test suite (pytest)
│   ├── config.py            # Configuration and environment variables
│   └── main.py              # FastAPI application entry point
├── src/                     # React frontend
│   ├── api/                 # API client functions
│   ├── components/          # React components by feature
│   │   ├── applications/    # Application manager components
│   │   ├── documents/       # Document manager components
│   │   ├── home/            # Dashboard and stat components
│   │   ├── profile/         # Profile view components
│   │   └── shared/          # Navigation and shared UI
│   └── __tests__/           # Frontend test suite (Vitest)
├── documents/               # User document storage (gitignored)
├── data/                    # SQLite database (gitignored)
└── docs/                    # Design specs and style guide
```

## Run tests

```bash
# Frontend tests
npm test

# Backend tests
pytest
```

## Tech stack

| Layer    | Technology                    |
| -------- | ----------------------------- |
| Frontend | React 19, TypeScript, Vite 8  |
| Backend  | FastAPI, Uvicorn              |
| Database | SQLite                        |
| Testing  | Vitest, pytest                |
| AI       | Claude Code Agent SDK         |

## Data storage

All data stays on your local machine:

- **Documents**: Stored in the `documents/` directory as files on disk. Metadata
  is tracked in `documents/.metadata.json`.
- **Profile**: Stored as `documents/.profile.json`.
- **Applications, tasks, and settings**: Stored in a SQLite database at
  `data/applications.db`. Portal credentials are encrypted with Fernet symmetric
  encryption.
- **Interview sessions**: Held in memory via persistent Claude SDK clients. Sessions
  expire after 30 minutes of inactivity and are lost when the backend restarts.

## Supported file types

PDF, DOCX, TXT, Markdown, XLSX, CSV, PPTX. Maximum upload size is 50 MB.

## API reference

| Method | Endpoint                              | Description                    |
| ------ | ------------------------------------- | ------------------------------ |
| GET    | `/api/health`                         | Health check                   |
| GET    | `/api/dashboard`                      | Aggregated dashboard data      |
| GET    | `/api/documents`                      | List documents                 |
| POST   | `/api/documents/upload`               | Upload documents               |
| GET    | `/api/documents/{id}/content`         | View document content          |
| PUT    | `/api/documents/{id}`                 | Update document metadata       |
| DELETE | `/api/documents/{id}`                 | Delete a document              |
| POST   | `/api/documents/sync`                 | Sync filesystem with metadata  |
| GET    | `/api/tags`                           | List all tags                  |
| GET    | `/api/profile`                        | Get candidate profile          |
| PUT    | `/api/profile`                        | Replace entire profile         |
| PATCH  | `/api/profile/{section}`              | Update a profile section       |
| POST   | `/api/interview/start`                | Start interview session        |
| POST   | `/api/interview/message`              | Send interview message         |
| POST   | `/api/interview/accept`               | Accept a suggestion            |
| POST   | `/api/interview/reject`               | Reject a suggestion            |
| POST   | `/api/extraction/analyze`             | Extract skills from documents  |
| POST   | `/api/extraction/accept`              | Accept extraction results      |
| POST   | `/api/posting/analyze`                | Analyze a job posting URL      |
| GET    | `/api/applications`                   | List applications              |
| POST   | `/api/applications`                   | Create an application          |
| PUT    | `/api/applications/{id}`              | Update an application          |
| DELETE | `/api/applications/{id}`              | Delete an application          |
| PATCH  | `/api/applications/{id}/status`       | Update application status      |
| GET    | `/api/applications/{id}/documents`    | List linked documents          |
| POST   | `/api/applications/{id}/documents`    | Link a document                |
| DELETE | `/api/applications/{id}/documents/{docId}` | Unlink a document         |
| GET    | `/api/tasks`                          | List tasks                     |
| POST   | `/api/tasks`                          | Create a task                  |
| PATCH  | `/api/tasks/{id}`                     | Toggle task completion         |
| DELETE | `/api/tasks/{id}`                     | Delete a task                  |
| GET    | `/api/settings/{key}`                 | Get a setting value            |
| PUT    | `/api/settings/{key}`                 | Set a setting value            |

## License

This project is for personal use.
