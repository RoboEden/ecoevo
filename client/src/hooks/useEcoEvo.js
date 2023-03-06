import { useEffect, useRef } from "react"
import localforage from "localforage"

export const useEcoEvo = (load, render, trader, state, dispatch) => {
    const setLog = (str) => { dispatch({ type: 'LOG', log: str }) }
    const reset = () => {
        localforage.clear().then(() => {
            setLog('Cache cleared.')
            ws.current.send(JSON.stringify({ step: 0, body: 'Reseting' }))
            setLog('Reseting...')
        })
    }
    const shutdown = () => {
        ws.current.send(JSON.stringify({ step: null, body: 'Shutdown' }))
    }
    const resume = (step) => {
        // TODO
        (step === 0) ?
            reset() : localforage.getItem(`step-${step - 1}`).then(() => {
                ws.current.send(JSON.stringify({ step: step, body: 'Requesting' }))
            })
    }
    const ws = useRef()

    // Websocket
    useEffect(() => {
        ws.current = new WebSocket(`ws://localhost:8081/ws/`)
        setLog('Connecting...')
        ws.current.onopen = () => {
            setLog('Connection opened.')
            reset()
        }
        ws.current.onmessage = (evt) => {
            const msg = JSON.parse(evt.data)
            // Init
            if (msg.totalStep) {
                dispatch({
                    type: 'INIT',
                    mapSize: msg.mapSize,
                    totalStep: msg.totalStep
                })
                return
            }
            msg.forEach((data, index) => {
                // Load
                if (state.isLoading) {
                    if (data.info.curr_step === 0) {
                        setLog('Loading...')
                        load(data.map)
                    }
                    if (data.info.curr_step > 0) {
                        dispatch({ type: 'LOADED' })
                        setLog('Ready to start!')
                    }
                }
                // Cache
                localforage.setItem('step-' + data.info.curr_step, data)
                    .then((data) => {
                        if (index === msg.length - 1) {
                            dispatch({ type: 'CACHE_STEP', cacheStep: data.info.curr_step })
                            ws.current.send(JSON.stringify({ step: data.info.curr_step, body: 'Requesting' }))
                        }
                    })
                    .catch((err) => {
                        console.error(err)
                    })
            })
        }
        ws.current.onclose = (evt) => {
            console.error(`Connection closed! ${evt.reason}`)
        }
        return () => {
            localforage.clear().then(console.log('Cache cleared.'))
            ws.current.close()
            console.log('Cleaning up! 🧼')
        }
    }, [])

    // Render
    useEffect(() => {
        localforage.getItem('step-' + state.renderStep).then((data) => {
            if (data && !(state.isLoading)) {
                dispatch({ type: 'DATA', data: data })
                render(data.map)
                trader(data.info.transaction_graph)
            }
        }).catch((err) => {
            console.error('step-' + state.renderStep, err)
        })
    }, [state.renderStep])


    return [reset, resume, shutdown]
}