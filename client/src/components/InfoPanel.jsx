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
                    (<li key={i}>{String(key)}:{String(value)}</li>)
                )}
            </ul>)
        }
    }
    return (
        <Grid container spacing={2}>
            <Grid item >
                <TableContainer component={Grid}>
                    <Table aria-label="simple table">
                        <TableHead>
                            <TableRow>
                                <StyledTableCell>Persona</StyledTableCell>
                                <StyledTableCell align="center">Id</StyledTableCell>
                                <StyledTableCell align="center">Pos</StyledTableCell>
                                <StyledTableCell align="center">Health</StyledTableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            <TableRow>
                                <StyledTableCell component="th" scope="row">{player?.persona}</StyledTableCell>
                                <StyledTableCell align="center">{player?.id}</StyledTableCell>
                                <StyledTableCell align="center">{player?.pos ? `[${player?.pos[0]}, ${player?.pos[1]}]` : ''}</StyledTableCell>
                                <StyledTableCell align="center">{player?.health}</StyledTableCell>
                            </TableRow>
                        </TableBody>
                    </Table>
                </TableContainer>
                <Grid item>
                    <Typography variant="overline">
                        Backpack
                    </Typography>
                    <BagProgressBar label='Backpack' bag={player?.backpack} />
                    <Typography variant="overline">
                        Stomach
                    </Typography>
                    <BagProgressBar label='Stomach' bag={player?.stomach} />
                </Grid>
                <TableContainer component={Grid}>
                    <Table aria-label="simple table">
                        <TableHead>
                            <TableRow>
                                <StyledTableCell>Collect remain</StyledTableCell>
                                <StyledTableCell align="center" >Last action</StyledTableCell>
                                <StyledTableCell align="center">Trade result</StyledTableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            <TableRow>
                                <StyledTableCell component="th" scope="row">{player?.collect_remain ?? 'None'}</StyledTableCell>
                                <StyledTableCell align="left">
                                    {_renderObject(player?.last_action.main_action)}
                                    {_renderObject(player?.last_action.sell_offer)}
                                    {_renderObject(player?.last_action.buy_offer)}
                                </StyledTableCell>
                                <StyledTableCell align="center">{player?.trade_result}
                                </StyledTableCell>
                            </TableRow>
                        </TableBody>
                    </Table>
                </TableContainer>
            </Grid>
            <Grid item xs={12} sm container>
                <Grid item xs container direction="column" spacing={2}>
                    <Typography variant="caption">
                        {_renderObject(info)}
                    </Typography>
                </Grid>

            </Grid>
        </Grid>
    )
}
