import ProgressBar from 'react-bootstrap/ProgressBar'
import ReactDOMServer from 'react-dom/server'
import { useSelector } from "react-redux"

export const BagProgressBar = ({ bag, label, limit }) => {
    const bagVolume = limit ? useSelector((state)=>state.bagVolume) : 1

    const BagItemProgressBar = (name, num) => (<ProgressBar className={name}
        key={name}
        max={bagVolume}
        now={num}
        data-tooltip-id="tooltip"
        data-tooltip-html={ReactDOMServer.renderToStaticMarkup(<div>
            {name}<br/>
            &nbsp;&nbsp;num: {num}
        </div>)}
    />)

    return (< ProgressBar
            data-tooltip-id="tooltip"
            data-tooltip-html={label}>
        {Object.keys(bag??{}).map((name)=>BagItemProgressBar(name, bag[name]?.num)
        )}
    </ProgressBar >)
}