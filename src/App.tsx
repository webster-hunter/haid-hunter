import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { NavBar } from './components/shared/NavBar'

const Dashboard = lazy(() => import('./components/home/Dashboard'))
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
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/home" element={<Dashboard />} />
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
