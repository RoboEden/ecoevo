import ProgressBar from 'react-bootstrap/ProgressBar'
import ReactDOMServer from 'react-dom/server'
import { useSelector } from "react-redux"

const BagItemProgessBar = ({key, num, limit}) => {
    const allItemData = useSelector((state)=>state.allItemData)
    const volume = num * allItemData?.[key]?.capacity
    return <ProgressBar
        key={key}
        className={key}
        max={limit}
        now={volume}
        data-tooltip-id="tooltip"
        data-tooltip-html={ReactDOMServer.renderToStaticMarkup(
            <div>
                {key}<br/>
                &nbsp;&nbsp;num: {num}<br/>
                &nbsp;&nbsp;volume: {volume}<br/>                    
            </div>
        )}
    />
}

export const BagProgressBar = ({ bag, label, hasLimit }) => {
    const limit = hasLimit ? useSelector((state)=>state.bagVolume) : 1
    const keys = ['gold', 'hazelnut', 'coral', 'sand', 'pineapple', 'peanut', 'stone', 'pumpkin']
    return <ProgressBar data-tooltip-id="tooltip" data-tooltip-html={label}>
        {keys.map((key)=>
            BagItemProgessBar({
                key: key,
                num: bag?.[key]?.num,
                limit: limit
            })
        )}
    </ProgressBar >
}