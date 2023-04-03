import { useDispatch, useSelector } from 'react-redux'

export const ConnectServerButton = () => {
    const mode = useSelector(state => state.mode)
    const dispatch = useDispatch()

    return <button
        style={{visibility: mode ? 'hidden' : 'visible'}}
        disabled={mode && mode != 'websocket'}
        onClick={() => {dispatch({type: 'CONNECT_SERVER_BUTTON'})}}
    >
        Connect server
    </button>
}