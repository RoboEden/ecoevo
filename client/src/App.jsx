import { useKeyControl } from './hooks'
import { LoadPage, MainPage } from './pages'
import { useSelector } from 'react-redux'
import { WebSocketClient } from './components'

export const Pages = () => {
	const isLoading = useSelector(state => state.cache.length <= 0)
	return isLoading
		? <div id='load-page'><LoadPage /></div>
		: <div id='main-page'><MainPage /></div>
}

export const App = () => {
	useKeyControl()
	return <div>
		<WebSocketClient />
		<Pages />
	</div>
}