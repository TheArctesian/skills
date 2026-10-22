import { Icon } from './Button'

// The 2021 toolbar, kept behind the legacyToolbar flag while the per-row actions in Appointments bed in.
export function LegacyIconBar({ onPick }: { onPick: (what: string) => void }) {
  return (
    <div className="flex gap-0">
      {['print', 'export', 'archive', 'delete'].map(what => (
        <button key={what} aria-label={what} className="p-0" onClick={() => onPick(what)}>
          <Icon name={what} />
        </button>
      ))}
    </div>
  )
}
