import { styled } from '@mui/material/styles'
import Grid from '@mui/material/Grid'
import Typography from '@mui/material/Typography'
import MuiInput from '@mui/material/Input'
import { useDispatch, useSelector } from 'react-redux'
const Input = styled(MuiInput)(({ theme }) => ({
    width: " 4rem",
    fontSize: '1.1rem',
    color: '#eeeeee',
}))

export const StepInput = () => {
    const cacheStep = useSelector((state)=>state.cacheStep)
    const renderStep = useSelector((state)=>state.renderStep)
    const sliderStep = useSelector((state)=>state.sliderStep)
    const dispatch = useDispatch()

    const handleInputChange = (event) => {
        const newValue = event.target.value === '' ? '' : Number(event.target.value)
        dispatch({ type: 'PAUSE' })
        dispatch({
            type: 'SLIDER_STEP',
            sliderStep: Math.min(newValue, cacheStep),
        })
        dispatch({
            type: 'RENDER_STEP',
            renderStep: newValue,
        })
    }

    const handleBlur = () => {
        const clipValue = Math.max(0, Math.min(renderStep, cacheStep))
        dispatch({
            type: 'SLIDER_STEP',
            sliderStep: clipValue,
        })
        dispatch({
            type: 'RENDER_STEP',
            renderStep: clipValue,
        })
    }

    return (
        <Grid container spacing={1} justifyContent="center" alignItems="baseline">
            <Typography id="input-slider" gutterBottom>
                Step
            </Typography>
            <Grid item>
                <Input
                    value={sliderStep}
                    size="medium"
                    onChange={handleInputChange}
                    onBlur={handleBlur}
                    inputProps={{
                        step: 1,
                        min: 0,
                        max: 1000,
                        type: 'number',
                        'aria-labelledby': 'input-slider',
                    }}
                />
            </Grid>
        </Grid>
    )
}