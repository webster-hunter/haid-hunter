export async function toggleTask(id: number, completed: boolean) {
  const res = await fetch(`/api/tasks/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed }),
  })
  if (!res.ok) throw new Error('Failed to toggle task')
  return res.json()
}

export async function addTask(title: string, recurrence: string | null, intervalDays: number | null) {
  const res = await fetch('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, recurrence, interval_days: intervalDays }),
  })
  if (!res.ok) throw new Error('Failed to add task')
  return res.json()
}

export async function deleteTask(id: number) {
  const res = await fetch(`/api/tasks/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete task')
  return res.json()
}
