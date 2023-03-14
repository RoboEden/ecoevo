import { useDispatch, useSelector } from 'react-redux'
import { useEcoEvo, useAnimator } from './hooks'
import { LoadPage, MainPage } from './pages'

export const AppDynamic = () => {
	const [load, render, trade] = useAnimator()
	const [reset, resume, shutdown] = useEcoEvo(load, render, trade) // start serverside gamecore and cache all history
}

export const App = () => {
	return <div>
		<AppDynamic />
		<div id='load-page'>
			<LoadPage />
		</div>
		<div id='main-page' style={{ visibility: "hidden" }}>
			<MainPage />
		</div>
	</div>
}