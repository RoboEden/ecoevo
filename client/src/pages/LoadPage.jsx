import { useEffect } from "react"

export const LoadPage = ({ isLoading, log }) => {


	const showMainPage = () => {
		const loadEl = document.getElementById('load-page')
		const mainEl = document.getElementById('main-page')
		if (loadEl && mainEl) {
			loadEl.remove()
			mainEl.style.visibility = "visible"
		}
	}
	return (
		<main className='simple-wrapper'>
			<p className='simple-heading'>EcoEvo</p>

			<p id='name-label' className='simple-subhead'>
				AI Economic Evolution
			</p>
			<p className='simple-section'>{log}</p>
			<div className='simple-section'>
				{isLoading ? null :
					<button
						onClick={showMainPage}
						onKeyDown={(e) => { if (e.key === 'Enter') showMainPage() }}>
						Start</button>
				}
			</div>
		</main>
	)
}