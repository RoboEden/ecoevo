import PlayArrowRoundedIcon from '@mui/icons-material/PlayArrowRounded'
import PauseIcon from '@mui/icons-material/Pause'
import { useDispatch, useSelector } from 'react-redux'

export const PlayButton = () => {
    const isPlaying = useSelector(state => state.isPlaying)
    const dispatch = useDispatch()

    return (
        <button
            aria-label='Send'
            className='icon-button play-button'
            onClick={() => {dispatch({ type: 'SWITCH_PLAYING' } )}}
        >
            {isPlaying ?
                <PauseIcon
                    sx={{
                        color: "black",
                        backgroundColor: "black",
                    }} /> :
                <PlayArrowRoundedIcon
                    sx={{
                        color: "black",
                        backgroundColor: "black",
                    }}
                />
            }
        </button>
    )
}