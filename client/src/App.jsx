
import { useReducer } from 'react'
import { useEcoEvo, useAnimator } from './hooks'
import { appReducer, funcInitialState } from "./reducers"
import { LoadPage, MainPage } from './pages'

export const App = () => {
	const [state, dispatch] = useReducer(appReducer, null, funcInitialState)

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