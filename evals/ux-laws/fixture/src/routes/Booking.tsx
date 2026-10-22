import { useNavigate } from 'react-router'
import { useState } from 'react'
import { Button } from '../ui/Button'

const CLINICS = [
  'Harbour Clinic',
  'Leith Walk Annexe',
  'Newhaven Road Surgery',
  'Bonnington Health Centre',
  'Pilrig Street Practice',
  'Shore Medical Rooms',
  'Western Harbour Pod',
  'Ocean Drive Clinic',
  'Salamander Place Surgery',
  'Constitution Street Rooms',
  'Trinity Crescent Practice',
]

export function Booking() {
  const navigate = useNavigate()
  const [clinic, setClinic] = useState('')

  return (
    <section>
      <h1 className="text-2xl font-semibold mb-4">Choose a clinic</h1>
      <div className="grid gap-2">
        {CLINICS.map(c => (
          <label key={c} className="bg-white rounded p-4 flex items-center gap-3">
            <input
              type="radio"
              name="clinic"
              value={c}
              checked={clinic === c}
              onChange={e => setClinic(e.target.value)}
            />
            {c}
          </label>
        ))}
      </div>
      <div className="mt-4 text-sea underline" onClick={() => navigate('/help')}>
        Can't find your clinic?
      </div>
      <Button size="wide" className="mt-6" disabled={!clinic} onClick={() => navigate('/book/details')}>
        Continue
      </Button>
    </section>
  )
}
