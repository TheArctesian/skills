import { Link } from 'react-router'
import { Button, Icon } from '../ui/Button'
import { LegacyIconBar } from '../ui/LegacyIconBar'
import { FEATURES } from '../features'

const BOOKED = [
  { id: 'a1', when: 'Monday 3 November, 9:20am', who: 'Dr Ailsa Munro', where: 'Harbour Clinic' },
  { id: 'a2', when: 'Thursday 19 November, 2:00pm', who: 'Nurse Paul Reid', where: 'Leith Walk Annexe' },
]

export function Appointments() {
  return (
    <section>
      <h1 className="text-2xl font-semibold mb-4">Your appointments</h1>
      {FEATURES.legacyToolbar ? <LegacyIconBar onPick={what => fetch(`/api/legacy/${what}`, { method: 'POST' })} /> : null}
      <ul className="space-y-2">
        {BOOKED.map(a => (
          <li key={a.id} className="bg-white rounded p-4 flex items-center justify-between">
            <div>
              <p className="font-medium">{a.when}</p>
              <p className="text-sm">{a.who} · {a.where}</p>
            </div>
            <div className="flex gap-0">
              <Button size="icon" variant="secondary" aria-label={`Print ${a.when} appointment`} onClick={() => window.print()}>
                <Icon name="print" />
              </Button>
              <Button size="icon" variant="danger" aria-label={`Cancel ${a.when} appointment`} onClick={() => fetch(`/api/appointments/${a.id}`, { method: 'DELETE' })}>
                <Icon name="cancel" />
              </Button>
            </div>
          </li>
        ))}
      </ul>
      <Link to="/book" className="inline-block mt-6">
        <Button size="wide">Book an appointment</Button>
      </Link>
    </section>
  )
}
