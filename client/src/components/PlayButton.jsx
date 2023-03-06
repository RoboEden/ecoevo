import { useEffect, useRef } from 'react'
import PlayArrowRoundedIcon from '@mui/icons-material/PlayArrowRounded'
import PauseIcon from '@mui/icons-material/Pause'

export const PlayButton = ({ state, dispatch }) => {
    // Playing effect
    const playInterval = useRef()
    useEffect(() => {
        if (state.isPlaying) {
            playInterval.current = setInterval(() => {
                dispatch({ type: 'PLAY' })
            }, 300)
        }
        else {
            clearInterval(playInterval.current)
        }
    }, [state.isPlaying])
    // Play / Pause
    const playPause = () => {
        dispatch({ type: state.isPlaying ? 'PAUSE' : 'PLAY' })
    }

    return (
        <button
            aria-label='Send'
            className='icon-button'
            onClick={playPause}
            onKeyDown={(e) => { if (e.key === 'Space') playPause() }}
        >
            {state.isPlaying ?
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