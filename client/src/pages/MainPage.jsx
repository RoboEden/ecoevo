import { GridWorld, StepSlider, StepInput, PlayButton } from "../components"
import { InfoPanel } from '../components/InfoPanel'
import Grid from '@mui/material/Grid'
import { useEffect } from "react"
import { Tooltip } from 'react-tooltip'
import { useDispatch, useSelector } from "react-redux"

export const MainPage = () => {
    const data = useSelector((state)=>state.data)
    const clickedId = useSelector((state)=>state.clickedId)
    const dispatch = useDispatch()

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
    const players = getPlayers(data?.map)
    useEffect(() => {
        for (const player of Object.values(players)) {
            addSvgEventListener(player)
        }
    }, [data])

    return (
        <main className='main-wrapper'>
            <header className='main-header'>
                <h1>EcoEvo</h1>
            </header>
            <Grid className='view-container' container spacing={1} justifyContent="center" alignItems="baseline">
                <GridWorld />
            </Grid>
            <div className='main-info-panel' >
                <InfoPanel player={players[clickedId]} />
            </div>
            <footer className='main-footer'>
                <StepSlider/>
                <Grid container direction='row' spacing={3}>
                    <Grid item><PlayButton/></Grid>
                    <Grid item><StepInput/></Grid>
                </Grid>
            </footer>
            <Tooltip id={`tooltip`} />
        </main >
    )
}