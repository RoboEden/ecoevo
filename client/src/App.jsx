import { useDispatch, useSelector } from 'react-redux'
import { useEcoEvo, useAnimator } from './hooks'
import { LoadPage, MainPage } from './pages'

export const App = () => {
	const [load, render, trade] = useAnimator()

	const [reset, resume, shutdown] = useEcoEvo(load, render, trade) // start serverside gamecore and cache all history

	return (<div>
		<div id='load-page'>
			<LoadPage />
		</div>
		<div id='main-page' style={{ visibility: "hidden" }}>
			<MainPage />
		</div>
	</div>)
}