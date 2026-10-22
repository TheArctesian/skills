import { NavLink, Outlet } from 'react-router'

const GROUPS = [
  { label: 'Care', items: [['/', 'Appointments'], ['/book', 'Book'], ['/help', 'Help']] },
  { label: 'Account', items: [['/account', 'Your record'], ['/account/settings', 'Settings']] },
]

export function Nav() {
  return (
    <div className="min-h-screen bg-shell text-ink">
      <nav aria-label="Main" className="flex gap-8 p-4">
        {GROUPS.map(({ label, items }) => (
          <section key={label} aria-label={label} className="flex flex-col gap-1">
            <p className="text-xs uppercase tracking-wide text-sea">{label}</p>
            {items.map(([to, text]) => (
              <NavLink
                key={to}
                to={to}
                end
                className={({ isActive }) => `px-3 py-2 rounded ${isActive ? 'bg-white font-medium' : 'hover:bg-white'}`}
              >
                {text}
              </NavLink>
            ))}
          </section>
        ))}
      </nav>
      <main className="p-4">
        <Outlet />
      </main>
    </div>
  )
}
