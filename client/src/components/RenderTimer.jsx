import { useEffect, useRef } from "react"
import { useSelector, useDispatch } from "react-redux"

export const RenderTimer = () => {
    const nextRenderTime = useSelector(state => state.nextRenderTime)
    const dispatch = useDispatch()

    const timout = useRef()
    useEffect(() => {
        clearTimeout(timout.current)
        timout.current = setTimeout(() => {
            dispatch( {type: 'RENDER'} )
        }, nextRenderTime - performance.now())
    }, [nextRenderTime])
}