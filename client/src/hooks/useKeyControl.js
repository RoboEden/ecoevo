import { useRef } from "react"
import { useEffect } from "react"
import { useDispatch } from "react-redux"

export const useKeyControl = () => {
    const dispatch = useDispatch()

    const binded = useRef()
    useEffect(() => {
        if (binded.current) return
        binded.current = true
        window.addEventListener("keydown", (evt) => {
            if ([" ", "Enter"].includes(evt.key)) {
                dispatch({type: "SWITCH_PLAYING"})
            } else if (["a", "ArrowLeft"].includes(evt.key)) {
                dispatch({type: "STEP_PREVIOUS"})
            } else if (["d", "ArrowRight"].includes(evt.key)) {
                dispatch({type: "STEP_NEXT"})
            } else if (["Home"].includes(evt.key)) {
                dispatch({type: "STEP_FIRST"})
            } else if (["End"].includes(evt.key)) {
                dispatch({type: "STEP_LAST"})
            }
        })
    })
}