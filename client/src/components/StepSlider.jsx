import Slider from '@mui/material/Slider'
import { styled } from '@mui/material/styles'

export const StepSlider = ({ state, dispatch }) => {
    const percent = state.cacheStep / state.totalStep * 100
    const CustomSlider = styled(Slider)(({ theme }) => ({
        "& .MuiSlider-rail": {
            background: `linear-gradient(to right, #dedede, #dedede ${percent}%, #6c6c6c , #6c6c6c ${percent}%)`,
        }
    }))
    const handleSliderChange = (event, newValue) => {
        dispatch({ type: 'PAUSE' })
        dispatch({
            type: 'SLIDER_STEP',
            sliderStep: Math.min(newValue, state.cacheStep),
        })
        if (performance.now() - state.currTime > 250) {
            dispatch({
                type: 'RENDER_STEP',
                renderStep: Math.min(newValue, state.cacheStep),
            })
        }
    }
    return (
        <CustomSlider
            value={typeof state.sliderStep === 'number' ? state.sliderStep : 0}
            onChange={handleSliderChange}
            aria-labelledby="input-slider"
            min={0}
            max={state.totalStep}
        />
    )
}