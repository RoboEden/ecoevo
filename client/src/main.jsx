import { createRoot } from 'react-dom/client'
import { App } from './App'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'react-tooltip/dist/react-tooltip.css'
import './index.scss'

const root = createRoot(document.getElementById('app-root'))
root.render(<App />)