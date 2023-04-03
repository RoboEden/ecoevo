import { useEffect, useRef } from "react"
import { useDispatch, useSelector } from "react-redux"

export const WebSocketClient = () => {
    const dispatch = useDispatch()
    const mode = useSelector(state => state.mode)

    const ws = useRef()
    useEffect(() => {
        if (mode != 'websocket') return
        ws.current = new WebSocket(`ws://localhost:8081/ws/`)
        ws.current.onopen = () => {
            ws.current.send(JSON.stringify({ step: 0, body: 'Reseting' }))
        }
        ws.current.onmessage = (evt) => {
            const msg = JSON.parse(evt.data)
            if (msg.totalStep) {
                dispatch({type: 'RECV_INIT_MESSAGE', value: msg})
                return
            }
            msg.forEach((data, index) => {
                dispatch(({ type: 'RECV_DATA', value: data}))
                ws.current.send(JSON.stringify({ step: data.info.curr_step, body: 'Requesting' }))
            })
        }
        ws.current.onclose = () => {}
        ws.current.onerror = () => {}
        return () => {
            ws.current.close()
        }
    }, [mode])
}