import { useSelector } from "react-redux"
import { ReplayLoadButton } from "../components"
import { ConnectServerButton } from "../components/ConnectServerButton"

export const LoadPage = () => {
	const mode = useSelector((state)=>state.mode)

	const hint = {
		default: 'Please select:',
		websocket: 'Connecting...',
		replay: 'Uploading...',
	}
	
	return (
		<main className='simple-wrapper'>
			<p className='simple-heading'>EcoEvo</p>

			<p id='name-label' className='simple-subhead'>
				AI Economic Evolution
			</p>
			<p className='simple-section'>{hint[mode ?? 'default']}</p>
			<div className='simple-section'>
				<ConnectServerButton />
				<ReplayLoadButton/>
			</div>
		</main>
	)
}