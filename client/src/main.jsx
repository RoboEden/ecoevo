import { createRoot } from 'react-dom/client'
import { App } from './App'
import { store } from './store'
import { Provider } from 'react-redux'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'react-tooltip/dist/react-tooltip.css'
import './index.scss'


const root = createRoot(document.getElementById('app-root'))
root.render(
<Provider store={store}>
    <App />
</Provider>
)