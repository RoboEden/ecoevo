import { createRoot } from 'react-dom/client'
import { App } from './App'
import { configureStore } from '@reduxjs/toolkit'
import { appReducer } from './reducers'
import { Provider } from 'react-redux'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'react-tooltip/dist/react-tooltip.css'
import './index.scss'

export const store = configureStore({
    reducer: appReducer,
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            thunk: true,
            immutableCheck: false,
            serializableCheck: false,
    }),
})

const root = createRoot(document.getElementById('app-root'))
root.render(
    <Provider store={store}>
        <App />
    </Provider>
)