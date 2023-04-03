import { useDispatch, useSelector } from "react-redux"
import ReactFileReader from "react-file-reader"
import LZString from "lz-string"

export const ReplayLoadButton = () => {
    const mode = useSelector(state => state.mode)
    const dispatch = useDispatch()
    
    const handleFiles = files => {
        files[0].text()
            .then(LZString.decompressFromUTF16)
            .then(JSON.parse)
            .then((obj)=>{
                dispatch({type: 'UPDATE_REPLAY_DATA', value: obj})
            })
    }

    return <ReactFileReader handleFiles={handleFiles}>
        <button
            style={{visibility: (!mode || mode == 'replay') ? 'visible' : 'hidden'}}
            disabled={mode && mode != 'replay'}
            onClick={() => {dispatch({type: 'REPLAY_LOAD_BUTTON'})}}
        >
            Load Replay
        </button>
    </ReactFileReader>
}