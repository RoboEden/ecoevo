import { GridWorld, InfoPanel, StepSlider, StepInput, PlayButton, ReplaySaveButton } from "../components"
import { Tooltip } from 'react-tooltip'
import { RenderTimer } from "../components/RenderTimer"

export const MainPage = () => {
    return (
        <main className='main-wrapper'>
            <header className='main-header'>
                <h3>EcoEvo</h3>
            </header>
            <div className='main-canvas'>
                <GridWorld />
            </div>
            <div className='main-info-panel' >
                <InfoPanel />
            </div>
            <footer className='main-footer'>
                <StepSlider />
                <div className='play-control'>
                    <PlayButton />
                    <StepInput />
                    <ReplaySaveButton />
                </div>
            </footer>
            <Tooltip id='tooltip' />
            <RenderTimer/>
        </main >
    )
}