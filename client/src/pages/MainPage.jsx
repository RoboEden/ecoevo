import { GridWorld, StepSlider, StepInput, PlayButton } from "../components"
import { InfoPanel } from '../components/InfoPanel'
import Grid from '@mui/material/Grid'
import { Tooltip } from 'react-tooltip'

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
                <Grid container direction='row' spacing={3}>
                    <Grid item><PlayButton /></Grid>
                    <Grid item><StepInput /></Grid>
                </Grid>
            </footer>
            <Tooltip id='tooltip' />
        </main >
    )
}