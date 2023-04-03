import { useSelector } from 'react-redux'
import fileDownload from "js-file-download"
import LZString from "lz-string"
import DownloadIcon from '@mui/icons-material/Download';

export const ReplaySaveButton = () => {
    const show = useSelector(state => state.step >= state.initMessage.totalStep && state.mode != 'replay')
    const initMessage = useSelector(state => state.initMessage)
    const cache = useSelector(state => state.cache)

    const saveReplay = () => {
        const fileData = LZString.compressToUTF16(JSON.stringify({initMessage: initMessage, cache: cache}))
        fileDownload(fileData, 'replay.json')
    }

    return <button
        style={{visibility: show ? "visible" : "hidden"}}
        aria-label='save'
        className='icon-button save-button'
        onClick={saveReplay}
    >
        <DownloadIcon/>
    </button>
}