import type { ComponentProps } from 'react'

// Every form on the site is built from this.
export function Field({ label, hint, error, ...rest }: ComponentProps<'input'> & { label: string; hint?: string; error?: string }) {
  return (
    <div>
      <label htmlFor={rest.id} className="block mb-4 text-sm font-medium">
        {label}
      </label>
      <input {...rest} className="w-full border border-sea rounded px-3 py-2" />
      {hint ? <p className="mt-0.5 text-xs text-sea">{hint}</p> : null}
      {error ? <p className="mt-0.5 text-alert text-sm">{error}</p> : null}
    </div>
  )
}

export function FieldSet({ children }: { children: React.ReactNode }) {
  return <div className="space-y-2">{children}</div>
}
