import { createBrowserRouter, RouterProvider } from 'react-router'
import { Nav } from './nav'
import { Appointments } from './routes/Appointments'
import { Booking } from './routes/Booking'
import { Details } from './routes/Details'
import { Confirm } from './routes/Confirm'
import { Account } from './routes/Account'
import { Settings } from './routes/Settings'
import { Help } from './routes/Help'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Nav />,
    children: [
      { index: true, element: <Appointments /> },
      { path: 'book', element: <Booking /> },
      { path: 'book/details', element: <Details /> },
      { path: 'book/confirm', element: <Confirm /> },
      { path: 'account', element: <Account /> },
      { path: 'account/settings', element: <Settings /> },
      { path: 'help', element: <Help /> },
    ],
  },
])

export function App() {
  return <RouterProvider router={router} />
}
