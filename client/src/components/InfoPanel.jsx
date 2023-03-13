import { BagProgressBar } from '../components/BagProgressBar'
import Grid from '@mui/material/Grid'
import Typography from '@mui/material/Typography'
import ButtonBase from '@mui/material/ButtonBase'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import { styled } from '@mui/material/styles'
import { useSelector } from 'react-redux'


const StyledTableCell = styled(TableCell)(({ theme }) => ({
    color: '#ffffff',
}))

export const InfoPanel = ({ player }) => {
    const info = useSelector((state)=>state.data.info)

    const _renderObject = (obj) => {
        if (obj) {
            return (<ul style={{ listStyle: 'none' }}>
                {Object.entries(obj).map(([key, value], i) =>
                    (<li key={i}>{String(key)}={String(value)}</li>)
                )}
            </ul>)
        }
    }

    return (<div>
        <Grid container spacing={1}>
            <Grid item container xs={2} direction='column'> 
                <Grid item>Id</Grid>
                <Grid item>{player?.id ?? '-'}</Grid>
            </Grid>
            <Grid item container xs={4} direction='column'>
                <Grid item>Persona</Grid>
                <Grid item>{player?.persona ?? '-'}</Grid>
            </Grid>
            <Grid item container xs={4} direction='column'>
                <Grid item>Pos</Grid>
                <Grid item>{player?.pos ? `${player?.pos[0]}, ${player?.pos[1]}` : '-'}</Grid>
            </Grid>
            <Grid item container xs={2} direction='column'>
                <Grid item>Health</Grid>
                <Grid item>{player?.health ?? '-'}</Grid>
            </Grid>
        </Grid>
        <hr/>
        <Typography variant="overline">Backpack</Typography>
        <BagProgressBar label='Backpack' bag={player?.backpack} hasLimit={true} />
        <Typography variant="overline">Stomach</Typography>
        <BagProgressBar label='Stomach' bag={player?.stomach} hasLimit={false} />
        <hr/>
        <Grid container spacing={1}>
            <Grid item xs={5}>Collect remain</Grid>
            <Grid item xs={7}>{player?.collect_remain??0}</Grid>
            <Grid item xs={5}>Last action</Grid>
            <Grid item xs={7}>{player?.last_action.main_action.primary} {player?.last_action.main_action.secondary}</Grid>
            {/* <Grid item xs={5}>Trade result</Grid>
            <Grid item xs={7}>{player?.trade_result}</Grid> */}
        </Grid>
        <hr/>
        <ul style={{ listStyle: 'none', paddingLeft: '0', fontSize: '0.5em' }}>
            {Object.entries(info??{}).map(([key, value], i) =>
                <li key={i}>{String(key)}={String(value)}</li>
            )}
        </ul>
    </div>)
}
