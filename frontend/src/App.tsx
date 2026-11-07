import { RouterProvider } from 'react-router-dom'
import AppRouter from './router/AppRouter'

function App(): React.ReactNode {
  return <RouterProvider router={AppRouter()} />
}

export default App
