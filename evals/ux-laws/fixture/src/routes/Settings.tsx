import { useState } from 'react'

const TOGGLES = [
  'Appointment reminders by SMS',
  'Appointment reminders by email',
  'Reminder 24 hours before',
  'Reminder 2 hours before',
  'Prescription ready alerts',
  'Test result alerts',
  'Clinic closure notices',
  'Annual review invitations',
  'Flu clinic invitations',
  'Share records with the health board',
  'Share records with your pharmacy',
  'Research contact opt-in',
  'Allow trainee clinicians to attend',
  'Large print correspondence',
]

export function Settings() {
  const [on, setOn] = useState<string[]>([])
  const [status, setStatus] = useState('')

  async function toggle(t: string, next: boolean) {
    const updated = next ? [...on, t] : on.filter(x => x !== t)
    setOn(updated)
    const r = await fetch('/api/settings', { method: 'PUT', body: JSON.stringify(updated) })
    setStatus(r.ok ? `${t} ${next ? 'on' : 'off'}. Saved.` : 'Could not save that change. Try again.')
  }

  return (
    <section>
      <h1 className="text-2xl font-semibold mb-4">Settings</h1>
      <p role="status" className="mb-4 text-sm text-sea">{status}</p>
      <div className="space-y-2">
        {TOGGLES.map(t => (
          <label key={t} className="bg-white rounded p-4 flex items-center justify-between">
            {t}
            <input type="checkbox" checked={on.includes(t)} onChange={e => toggle(t, e.target.checked)} />
          </label>
        ))}
      </div>
    </section>
  )
}
