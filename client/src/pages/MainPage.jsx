import { GridWorld, StepSlider, StepInput, PlayButton } from "../components"
import { InfoPanel } from '../components/InfoPanel'
import Grid from '@mui/material/Grid'
import { useEffect } from "react"
import { Tooltip } from 'react-tooltip'

export const MainPage = ({ shutdown, state, dispatch }) => {
    function getPlayers(map) {
        let players = {}
        if (map) {
            for (const [pos, tile] of Object.entries(map)) {
                if (tile.player) { players[tile.player.id] = tile.player }
            }
        }
        return players
    }
    function addSvgEventListener(player) {
        const id = player.id
        const playerSvg = document.getElementById(`player-${id}`)
        playerSvg.onmousedown = () => {
            dispatch({ type: 'CLICKED_ID', clickedId: id })
            // playerSvg.style.filter = 'brightness(0.8)'
        }
        // playerSvg.onmouseup = () => {
        //     playerSvg.style.filter = 'brightness(1)'
        // }
    }
    const players = getPlayers(state.data?.map)
    useEffect(() => {
        for (const player of Object.values(players)) {
            addSvgEventListener(player)
        }
    }, [state.data])

    return (
        <main className='main-wrapper'>
            <header className='main-header'>
                <h1>EcoEvo</h1>
            </header>
            <Grid className='view-container' container spacing={1} justifyContent="center" alignItems="baseline">
                <GridWorld state={state} />
            </Grid>
            <div className='main-info-panel' >
                <InfoPanel info={state.data.info} player={players[state.clickedId]} />
            </div>
            <footer className='main-footer'>
                <StepInput state={state} dispatch={dispatch} />
                <PlayButton state={state} dispatch={dispatch} />
                <StepSlider state={state} dispatch={dispatch} />
            </footer>
            <Tooltip id={`tooltip`} />
        </main >
    )
}