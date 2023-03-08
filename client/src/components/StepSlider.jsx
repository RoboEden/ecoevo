import Slider from '@mui/material/Slider'
import { styled } from '@mui/material/styles'
import { useDispatch, useSelector } from 'react-redux'

export const StepSlider = () => {
    const cacheStep = useSelector((state)=>state.cacheStep)
    const totalStep = useSelector((state)=>state.totalStep)
    const currTime = useSelector((state)=>state.currTime)
    const sliderStep = useSelector((state)=>state.sliderStep)
    const dispatch = useDispatch()

    const percent = cacheStep / totalStep * 100
    const CustomSlider = styled(Slider)(({ theme }) => ({
        "& .MuiSlider-rail": {
            background: `linear-gradient(to right, #dedede, #dedede ${percent}%, #6c6c6c , #6c6c6c ${percent}%)`,
        }
    }))
    const handleSliderChange = (event, newValue) => {
        dispatch({ type: 'PAUSE' })
        dispatch({
            type: 'SLIDER_STEP',
            sliderStep: Math.min(newValue, cacheStep),
        })
        if (performance.now() - currTime > 250) {
            dispatch({
                type: 'RENDER_STEP',
                renderStep: Math.min(newValue, cacheStep),
            })
        }
    }
    return (
        <CustomSlider
            value={typeof sliderStep === 'number' ? sliderStep : 0}
            onChange={handleSliderChange}
            aria-labelledby="input-slider"
            min={0}
            max={totalStep}
        />
    )
}