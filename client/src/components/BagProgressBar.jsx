import ProgressBar from 'react-bootstrap/ProgressBar'

export const BagProgressBar = ({ bag, label }) => {
    return (< ProgressBar max={1000}
        data-tooltip-id="tooltip"
        data-tooltip-content={`${label}`}>
        <ProgressBar className='gold'
            now={bag?.gold.num}
            data-tooltip-id="tooltip"
            data-tooltip-html={`gold<br/>&nbsp;&nbsp;num: ${bag?.gold.num}`} />
        <ProgressBar className='hazelnut'
            now={bag?.hazelnut.num}
            data-tooltip-id="tooltip"
            data-tooltip-html={`hazelnut<br/>&nbsp;&nbsp;num: ${bag?.hazelnut.num}`} />
        <ProgressBar className='coral'
            now={bag?.coral.num}
            data-tooltip-id="tooltip"
            data-tooltip-html={`coral<br/>&nbsp;&nbsp;num: ${bag?.coral.num}`} />
        <ProgressBar className='sand'
            now={bag?.sand.num}
            data-tooltip-id="tooltip"
            data-tooltip-html={`sand<br/>&nbsp;&nbsp;num: ${bag?.sand.num}`} />
        <ProgressBar className='pineapple'
            now={bag?.pineapple.num}
            data-tooltip-id="tooltip"
            data-tooltip-html={`pineapple<br/>&nbsp;&nbsp;num: ${bag?.pineapple.num}`} />
        <ProgressBar className='peanut'
            now={bag?.peanut.num}
            data-tooltip-id="tooltip"
            data-tooltip-html={`peanut<br/>&nbsp;&nbsp;num: ${bag?.peanut.num}`} />
        <ProgressBar className='stone'
            now={bag?.stone.num}
            data-tooltip-id="tooltip"
            data-tooltip-html={`stone<br/>&nbsp;&nbsp;num: ${bag?.stone.num}`} />
        <ProgressBar className='pumpkin'
            now={bag?.pumpkin.num}
            data-tooltip-id="tooltip"
            data-tooltip-html={`pumpkin<br/>&nbsp;&nbsp;num: ${bag?.pumpkin.num}`} />
    </ProgressBar >)
}