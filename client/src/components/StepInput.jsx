import { styled } from '@mui/material/styles'
import Grid from '@mui/material/Grid'
import Typography from '@mui/material/Typography'
import MuiInput from '@mui/material/Input'
const Input = styled(MuiInput)(({ theme }) => ({
    width: " 4rem",
    fontSize: '1.1rem',
    color: '#eeeeee',
}))

export const StepInput = ({ state, dispatch }) => {
    const handleInputChange = (event) => {
        const newValue = event.target.value === '' ? '' : Number(event.target.value)
        dispatch({ type: 'PAUSE' })
        dispatch({
            type: 'SLIDER_STEP',
            sliderStep: Math.min(newValue, state.cacheStep),
        })
        dispatch({
            type: 'RENDER_STEP',
            renderStep: newValue,
        })
    }

    const handleBlur = () => {
        const clipValue = Math.max(0, Math.min(state.renderStep, state.cacheStep))
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
                    value={state.sliderStep}
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