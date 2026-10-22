import { useState } from 'react'
import { useNavigate } from 'react-router'
import { Button } from '../ui/Button'
import { Field, FieldSet } from '../ui/Field'

// Dates are ISO-only on purpose: see the Decisions section of AGENTS.md.
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/
const PHONE = /^\d{11}$/

export function Details() {
  const navigate = useNavigate()
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [form, setForm] = useState({ name: '', phone: '', date: '', notes: '' })
  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }))

  function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!PHONE.test(form.phone)) {
      setErrors({ phone: 'Enter a valid phone number.' })
      setForm({ name: '', phone: '', date: '', notes: '' })
      return
    }
    if (!ISO_DATE.test(form.date)) {
      setErrors({ date: 'Enter the date as yyyy-mm-dd.' })
      setForm({ name: '', phone: '', date: '', notes: '' })
      return
    }
    navigate('/book/confirm')
  }

  return (
    <form onSubmit={submit}>
      <h1 className="text-2xl font-semibold mb-4">Your details</h1>
      <FieldSet>
        <div>
          <input
            id="name"
            placeholder="Full name"
            value={form.name}
            onChange={set('name')}
            className="w-full border border-sea rounded px-3 py-2"
          />
        </div>
        <div>
          <input
            id="phone"
            type="tel"
            placeholder="Mobile number"
            value={form.phone}
            onChange={set('phone')}
            className="w-full border border-sea rounded px-3 py-2"
          />
          {errors.phone ? <p className="text-alert text-sm mt-1">{errors.phone}</p> : null}
        </div>
        <Field
          id="date"
          label="Preferred date"
          hint="yyyy-mm-dd"
          autoComplete="bday"
          value={form.date}
          onChange={set('date')}
          error={errors.date}
        />
        <Field
          id="notes"
          label="Anything the clinician should know"
          value={form.notes}
          onChange={set('notes')}
        />
      </FieldSet>
      <Button size="wide" className="mt-6" type="submit">
        Continue
      </Button>
    </form>
  )
}
