import { BagProgressBar } from '../components/BagProgressBar'
import Grid from '@mui/material/Grid'
import Typography from '@mui/material/Typography'
import { useSelector } from 'react-redux'

const playerSelector = (state) => {
    const map = state?.data?.map
    if (!map) return null
    if (!state.clickedId) return null
    for (const [pos, tile] of Object.entries(map)) {
        if (tile.player && tile.player.id == state.clickedId) {
            return tile.player
        }
    }
}

const PlainList = ({ data }) => <ul>
    {data.map((value, index) => <li key={index}>{value}</li>)}
</ul>

const OfferList = () => {
    const player = useSelector(playerSelector)
    const data = (player?.offers ?? []).map(
        (offer) => offer ? `${-offer[0][1]} ${offer[0][0]} -> ${offer[1][1]} ${offer[1][0]}` : '-'
    )
    return <PlainList data={data} />
}

const InfoList = () => {
    const info = useSelector((state) => state.data.info)
    const data = Object.entries(info ?? {}).map(
        ([key, value]) => `${key}=${value}`
    )
    return <PlainList data={data} />
}

const PlayerInfo = ({ getter }) => {
    const player = useSelector(playerSelector)
    const data = player ? getter(player) : '-'
    return data
}

export const InfoPanel = () => {
    return (<div>
        <Grid container spacing={1}>
            <Grid item container xs={6} direction='column'>
                <Grid item xs={6}>Persona</Grid>
                <Grid item xs={6}><PlayerInfo getter={player => player.persona} /></Grid>
            </Grid>
            <Grid item container xs={2} direction='column'>
                <Grid item xs={6}>Id</Grid>
                <Grid item xs={6}><PlayerInfo getter={player => player.id} /></Grid>
            </Grid>
            <Grid item container xs={2} direction='column'>
                <Grid item xs={6}>Pos</Grid>
                <Grid item xs={6}><PlayerInfo getter={player => `${player.pos[0]}, ${player.pos[1]}`} /></Grid>
            </Grid>
            <Grid item container xs={2} direction='column'>
                <Grid item xs={6}>Health</Grid>
                <Grid item xs={6}><PlayerInfo getter={player => player.health} /></Grid>
            </Grid>
        </Grid>
        <hr />
        <Typography variant="overline">Backpack</Typography>
        <BagProgressBar bagName='backpack' playerSelector={playerSelector} />
        <Typography variant="overline">Stomach</Typography>
        <BagProgressBar bagName='stomach' playerSelector={playerSelector} />
        <hr />
        <Grid container spacing={1}>
            <Grid item xs={4}>Collect remain</Grid>
            <Grid item xs={8}><PlayerInfo getter={player => player.collect_remain} /></Grid>
            <Grid item xs={4}>Last action</Grid>
            <Grid item xs={8}><PlayerInfo getter={player => `${player.last_action.main_action.primary} ${player?.last_action.main_action.secondary}`} /></Grid>
            <Grid item xs={4}>Current offer</Grid>
            <Grid item xs={8}><OfferList /></Grid>
        </Grid>
        <hr />
        <InfoList />
    </div>)
}
