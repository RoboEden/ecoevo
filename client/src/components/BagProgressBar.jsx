import ProgressBar from 'react-bootstrap/ProgressBar'
import { useSelector } from "react-redux"

export const BagProgressBar = ({ bagName, playerSelector }) => {
    const KEYS = ['gold', 'hazelnut', 'coral', 'sand', 'pineapple', 'peanut', 'stone', 'pumpkin']

    const limit = bagName == 'backpack' ? useSelector((state)=>state.bagVolume) : 1
    const allItemData = useSelector((state)=>state.allItemData)
    const player = useSelector(playerSelector)
    const bag = player?.[bagName]

    const data = KEYS.map((key)=>{
        const num = bag ? bag[key].num : 0
        const capacity = allItemData ? allItemData[key].capacity : 0
        return {
            key: key,
            num: num,
            volume: num * capacity,
        }
    })

    return <ProgressBar data-tooltip-id="tooltip" data-tooltip-html={bagName}>
        {data.map(({key, num, volume}) =>
            <ProgressBar
                key={key}
                label={num}
                className={key}
                max={limit}
                now={volume}
                data-tooltip-id="tooltip"
                data-tooltip-html={`${key}<br/>&nbsp;&nbsp;num: ${num}<br/>&nbsp;&nbsp;volume: ${volume}<br/>`}
            />
        )}
    </ProgressBar >
}