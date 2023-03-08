import { useDispatch, useSelector } from 'react-redux'
import { useEcoEvo, useAnimator } from './hooks'
import { LoadPage, MainPage } from './pages'

export const App = () => {
	const state = useSelector((state)=>state)
	const dispatch = useDispatch()

	const [load, render, trade] = useAnimator(state, dispatch)

	const [reset, resume, shutdown] = useEcoEvo(load, render, trade, state, dispatch) // start serverside gamecore and cache all history

	return (<div>
		<div id='load-page'>
			<LoadPage log={state.log} isLoading={state.isLoading} />
		</div>
		<div id='main-page' style={{ visibility: "hidden" }}>
			<MainPage shutdown={shutdown} state={state} dispatch={dispatch} />
		</div>
	</div>)
}