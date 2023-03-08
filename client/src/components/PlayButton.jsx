import { useEffect, useRef } from 'react'
import PlayArrowRoundedIcon from '@mui/icons-material/PlayArrowRounded'
import PauseIcon from '@mui/icons-material/Pause'
import { useDispatch, useSelector } from 'react-redux'

export const PlayButton = () => {
    const isPlaying = useSelector((state)=>(state.isPlaying))
    const dispatch = useDispatch()

    // Playing effect
    const playInterval = useRef()
    useEffect(() => {
        if (isPlaying) {
            playInterval.current = setInterval(() => {
                dispatch({ type: 'PLAY' })
            }, 300)
        }
        else {
            clearInterval(playInterval.current)
        }
    }, [isPlaying])
    // Play / Pause
    const playPause = () => {
        dispatch({ type: isPlaying ? 'PAUSE' : 'PLAY' })
    }

    return (
        <button
            aria-label='Send'
            className='icon-button'
            onClick={playPause}
            onKeyDown={(e) => { if (e.key === 'Space') playPause() }}
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