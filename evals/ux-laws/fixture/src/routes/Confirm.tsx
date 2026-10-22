import { useState } from 'react'
import { useNavigate } from 'react-router'
import { Button } from '../ui/Button'

export function Confirm() {
  const navigate = useNavigate()
  const [agreed, setAgreed] = useState(false)

  async function book() {
    await fetch('/api/appointments', { method: 'POST', body: JSON.stringify({ agreed }) })
    navigate('/')
  }

  return (
    <section>
      <h1 className="text-2xl font-semibold mb-4">Check and book</h1>
      <p className="mb-4">Harbour Clinic · your chosen date · Dr Ailsa Munro</p>
      <label className="flex items-center gap-3 mb-6">
        <input type="checkbox" checked={agreed} onChange={e => setAgreed(e.target.checked)} />
        I understand the cancellation policy
      </label>
      <Button size="wide" disabled={!agreed} onClick={book}>
        Book this appointment
      </Button>
    </section>
  )
}
