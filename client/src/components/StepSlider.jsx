import Slider from '@mui/material/Slider'
import { useDispatch, useSelector } from 'react-redux'

export const StepSlider = () => {
    const totalStep = useSelector((state)=>state.initMessage.totalStep)
    const cacheStep = useSelector((state)=>state.cache.length) - 1
    const sliderStep = useSelector((state)=>state.sliderStep)
    const dispatch = useDispatch()

    const percent = cacheStep / totalStep * 100

    return (
        <Slider
            value={sliderStep}
            onChange={(_, value) => {dispatch({ type: 'SLIDER_CHANGE', value: value})}}
            onChangeCommitted={(_, value) => {dispatch({ type: 'SLIDER_COMMIT', value: value})}}
            aria-labelledby="input-slider"
            min={0}
            max={totalStep}
            sx={{
                "& .MuiSlider-rail": {
                    background: `linear-gradient(to right, #dedede, #dedede ${percent}%, #6c6c6c , #6c6c6c ${percent}%)`,
                }
            }}
        />
    )
}