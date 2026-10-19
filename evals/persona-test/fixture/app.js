const PRODUCTS = [
  { id: 'rice', name: 'Basmati rice, 1 kg', price: 2.4 },
  { id: 'eggs', name: 'Free-range eggs, 6', price: 2.1 },
  { id: 'oats', name: 'Rolled oats, 750 g', price: 1.6 },
  { id: 'apples', name: 'Braeburn apples, 6', price: 2.8 },
]
const COUNTRIES = ['Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Argentina', 'Armenia', 'Australia', 'Austria',
  'Belgium', 'Brazil', 'Bulgaria', 'Canada', 'Chile', 'China', 'Croatia', 'Cyprus', 'Czechia', 'Denmark', 'Egypt', 'Estonia',
  'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Iceland', 'India', 'Ireland', 'Italy', 'Japan', 'Kenya', 'Latvia',
  'Lithuania', 'Luxembourg', 'Malta', 'Mexico', 'Netherlands', 'New Zealand', 'Nigeria', 'Norway', 'Poland', 'Portugal',
  'Romania', 'Slovakia', 'Slovenia', 'South Africa', 'Spain', 'Sweden', 'Switzerland', 'Turkey', 'Ukraine',
  'United Kingdom', 'United States', 'Uruguay', 'Vietnam', 'Zambia']
const store = {
  get: (k, d) => JSON.parse(localStorage.getItem(k) || JSON.stringify(d)),
  set: (k, v) => localStorage.setItem(k, JSON.stringify(v)),
}
const basket = () => store.get('basket', {})
const showCount = () => {
  const n = Object.values(basket()).reduce((a, b) => a + b, 0)
  document.getElementById('count').textContent = n || ''
}
showCount()

const products = document.getElementById('products')
if (products) {
  for (const p of PRODUCTS) {
    const card = document.createElement('div')
    card.className = 'card'
    card.innerHTML = `<svg aria-hidden="true" viewBox="0 0 24 24" width="20" height="20"><path d="M5 19c8 0 14-6 14-14C11 5 5 11 5 19z" fill="#4a4"/></svg>
      <h2>${p.name}</h2><p>£${p.price.toFixed(2)}</p><button data-id="${p.id}">Add</button>`
    products.append(card)
  }
  products.addEventListener('click', e => {
    const id = e.target.dataset && e.target.dataset.id
    if (!id) return
    const b = basket()
    b[id] = (b[id] || 0) + 1
    store.set('basket', b)
    showCount()
  })
}

const lines = document.getElementById('lines')
if (lines) {
  const b = basket()
  let total = 0
  for (const [id, n] of Object.entries(b)) {
    const p = PRODUCTS.find(x => x.id === id)
    total += p.price * n
    lines.insertAdjacentHTML('beforeend', `<li>${n} × ${p.name}</li>`)
  }
  document.getElementById('total').textContent = total ? `Total £${total.toFixed(2)}` : 'Your basket is empty.'
}

const checkout = document.getElementById('checkout')
if (checkout) {
  const sel = document.getElementById('country')
  for (const c of COUNTRIES) sel.add(new Option(c, c, c === 'United Kingdom', c === 'United Kingdom'))
  const news = document.getElementById('news')
  news.setAttribute('aria-labelledby', 'news-label')
  news.addEventListener('click', () => {
    const on = news.getAttribute('aria-checked') !== 'true'
    news.setAttribute('aria-checked', String(on))
    news.textContent = on ? 'On' : 'Off'
  })
  const saved = store.get('profile', null)
  if (saved) { checkout.address.value = saved.address; checkout.postcode.value = saved.postcode }
  checkout.addEventListener('submit', e => {
    e.preventDefault()
    const f = Object.fromEntries(new FormData(checkout))
    if (!f.name || !f.address || !f.postcode || !f.phone) {
      document.getElementById('err').textContent = 'Please check your details.'
      checkout.reset()
      return
    }
    store.set('order', { ...f, basket: basket() })
    store.set('basket', {})
    location.href = 'done.html'
  })
}

const where = document.getElementById('where')
if (where) { const o = store.get('order', {}); where.textContent = `${o.address || ''}, ${o.postcode || ''}` }

const profile = document.getElementById('profile')
if (profile) {
  const saved = store.get('profile', { address: '', postcode: '' })
  profile.address.value = saved.address
  profile.postcode.value = saved.postcode
  profile.addEventListener('submit', e => {
    e.preventDefault()
    store.set('profile', Object.fromEntries(new FormData(profile)))
  })
}
