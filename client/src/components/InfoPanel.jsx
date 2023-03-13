import { BagProgressBar } from '../components/BagProgressBar'
import Grid from '@mui/material/Grid'
import Typography from '@mui/material/Typography'
import { useSelector } from 'react-redux'

const PlainList = ({data}) => <ul>
    {data.map((value, index) => <li key={index}>{value}</li>)}
</ul>

export const InfoPanel = ({ player }) => {
    const info = useSelector((state)=>state.data.info)

    const empty = '-'

    const getOfferList = (player) => (player?.offers??[]).map(
        (offer) => offer ? `${-offer[0][1]} ${offer[0][0]} -> ${offer[1][1]} ${offer[1][0]}` : '/'
    )

    const getInfoList = (info) => (Object.entries(info??{}).map(
        ([key, value]) => `${key}=${value}`)
    )

    return (<div>
        <Grid container spacing={1}>
            <Grid item container xs={6} direction='column'>
                <Grid item xs={6}>Persona</Grid>
                <Grid item xs={6}>{player?.persona ?? empty}</Grid>
            </Grid>
            <Grid item container xs={2} direction='column'> 
                <Grid item xs={6}>Id</Grid>
                <Grid item xs={6}>{player?.id ?? empty}</Grid>
            </Grid>
            <Grid item container xs={2} direction='column'>
                <Grid item xs={6}>Pos</Grid>
                <Grid item xs={6}>{player ? `${player.pos[0]}, ${player.pos[1]}` : empty}</Grid>
            </Grid>
            <Grid item container xs={2} direction='column'>
                <Grid item xs={6}>Health</Grid>
                <Grid item xs={6}>{player?.health ?? empty}</Grid>
            </Grid> 
        </Grid>
        <hr/>
        <Typography variant="overline">Backpack</Typography>
        <BagProgressBar label='Backpack' bag={player?.backpack} hasLimit={true} />
        <Typography variant="overline">Stomach</Typography>
        <BagProgressBar label='Stomach' bag={player?.stomach} hasLimit={false} />
        <hr/>
        <Grid container spacing={1}>
            <Grid item xs={4}>Collect remain</Grid>
            <Grid item xs={8}>{player?.collect_remain??empty}</Grid>
            <Grid item xs={4}>Last action</Grid>
            <Grid item xs={8}>{player ? `${player.last_action.main_action.primary} ${player?.last_action.main_action.secondary}` : empty}</Grid>
            <Grid item xs={4}>Current offer</Grid>
            <Grid item xs={8}><PlainList data={getOfferList(player)}/></Grid>
        </Grid>
        <hr/>
        <PlainList data={getInfoList(info)} />
    </div>)
}
