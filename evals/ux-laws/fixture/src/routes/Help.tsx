import { Link } from 'react-router'

const TOPICS = [
  { to: '/book', title: 'Book an appointment', body: 'Choose a clinic, give your details, then check and book.' },
  { to: '/', title: 'Cancel an appointment', body: 'Open Your appointments and use the cancel button on the appointment you no longer need.' },
  { to: '/account', title: 'Check your NHS number', body: 'Your record shows the NHS number we hold for you, along with your name.' },
]

export function Help() {
  return (
    <section>
      <h1 className="text-2xl font-semibold mb-6">Help</h1>
      <div className="space-y-6">
        {TOPICS.map(t => (
          <article key={t.to} className="bg-white rounded p-4">
            <h2 className="text-lg font-medium mb-2">{t.title}</h2>
            <p className="mb-3">{t.body}</p>
            <Link to={t.to} className="text-sea underline">
              Go to {t.title.toLowerCase()}
            </Link>
          </article>
        ))}
      </div>
    </section>
  )
}
