import { describe, it, expect, vi, beforeEach } from 'vitest'

describe('dashboard API module', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ profile: {}, documents: {}, applications: {}, tasks: {} }),
    }))
  })

  it('fetchDashboard calls /api/dashboard and returns data', async () => {
    const { fetchDashboard } = await import('../../api/dashboard')
    const data = await fetchDashboard()
    expect(fetch).toHaveBeenCalledWith('/api/dashboard')
    expect(data).toHaveProperty('profile')
  })

  it('fetchDashboard throws on non-ok response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 500 }))
    const { fetchDashboard } = await import('../../api/dashboard')
    await expect(fetchDashboard()).rejects.toThrow()
  })
})

describe('tasks API module', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ id: 1, title: 'Test' }),
    }))
  })

  it('toggleTask sends PATCH with completed flag', async () => {
    const { toggleTask } = await import('../../api/tasks')
    await toggleTask(1, true)
    expect(fetch).toHaveBeenCalledWith('/api/tasks/1', expect.objectContaining({
      method: 'PATCH',
    }))
  })

  it('addTask sends POST with task data', async () => {
    const { addTask } = await import('../../api/tasks')
    await addTask('New task', 'daily', null)
    expect(fetch).toHaveBeenCalledWith('/api/tasks', expect.objectContaining({
      method: 'POST',
    }))
  })

  it('deleteTask sends DELETE', async () => {
    const { deleteTask } = await import('../../api/tasks')
    await deleteTask(1)
    expect(fetch).toHaveBeenCalledWith('/api/tasks/1', expect.objectContaining({
      method: 'DELETE',
    }))
  })

  it('toggleTask throws on non-ok response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 500 }))
    const { toggleTask } = await import('../../api/tasks')
    await expect(toggleTask(1, true)).rejects.toThrow()
  })
})
