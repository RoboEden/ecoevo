import { useDispatch, useSelector } from 'react-redux'

export const StepInput = () => {
    const sliderStep = useSelector((state)=>state.sliderStep)
    const dispatch = useDispatch()

    const onChange = (event) => {
        const newValue = event.target.value ? Number(event.target.value) : 0
        dispatch({ type: 'STEP_INPUT', value: newValue })
    }

    return <div>
        <label>Step&nbsp;</label>
        <input
            className='step-input'
            type="number"
            value={sliderStep}
            onChange={onChange}
            min={0}
            max={1000}
        />
    </div>
}