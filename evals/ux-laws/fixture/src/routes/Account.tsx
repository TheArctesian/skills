import { useEffect, useState } from 'react'

type Patient = { id: string; name: string; nhsNumber: string }

export function Account() {
  const [patient, setPatient] = useState<Patient | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch('/api/patient')
      .then(r => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setPatient)
      .catch(e => setError(`HTTP 500: ECONNREFUSED fetching patient_record: ${e.message}`))
  }, [])

  if (error) return <p className="text-alert">{error}</p>
  if (!patient) return <p className="text-sea">Loading your record…</p>

  return (
    <section>
      <h1 className="text-2xl font-semibold mb-4">Your record</h1>
      <dl className="bg-white rounded p-4 space-y-2">
        <div>
          <dt className="text-sm text-sea">patient_id</dt>
          <dd>{patient.id}</dd>
        </div>
        <div>
          <dt className="text-sm text-sea">Name</dt>
          <dd>{patient.name}</dd>
        </div>
        <div>
          <dt className="text-sm text-sea">NHS number</dt>
          <dd>{patient.nhsNumber}</dd>
        </div>
      </dl>
    </section>
  )
}
