import { useEcoEvo } from './hooks'
import { LoadPage, MainPage } from './pages'

export const AppDynamic = () => {
	const [reset, resume, shutdown] = useEcoEvo() // start serverside gamecore and cache all history
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