import { useTransition, animated } from '@react-spring/web'
import { useSelector, useDispatch } from 'react-redux'
import { LineSvg } from "./LineSvg"

export const GridWorld = () => {
    // const mapSize = 32
    // const dataMap = {
    //     "(14,14)": {item: null, player: {id: 5, persona: 'gold_digger', pos: [14, 14]}},
    //     "(14,18)": {item: null, player: {id: 8, persona: 'gold_digger', pos: [14, 18]}},
    //     "(20,18)": {item: {name: 'gold', num: 100, refresh_remain: 0}, player: null},
    // }
    // const clickedId = 5
    // const transactionGraph = {
    //     "(5,8)": ['gold', 100],
    //     "(8,5)": ['sand', 100],
    // }
    // const dispatch = (x) => null

    const mapSize = useSelector((state) => state.initMessage.mapSize) ?? 0
    const dataMap = useSelector((state) => state.cache[state.step]?.map) ?? {}
    const transactionGraph = useSelector((state) => state.cache[state.step]?.info?.transaction_graph) ?? {}
    const focusPlayerId = useSelector((state) => state.focusPlayerId)
    const dispatch = useDispatch()

    const flip = (y) => mapSize - 1 - y

    const itemArray = []
    const playerArray = []
    const playerPos = {}
    for ( const [posStr, tile] of Object.entries(dataMap) ) {
        if (tile.player) {
            playerArray.push({
                id: tile.player.id,
                persona: tile.player.persona,
                x: tile.player.pos[0],
                y: flip(tile.player.pos[1]),
                pos: posStr.slice(1, -1),
                overlap: !!tile.item,
            })
            playerPos[tile.player.id] = tile.player.pos
        }
        if (tile.item) {
            const [x, y] = posStr.slice(1, -1).split(',').map(Number)
            itemArray.push({
                name: tile.item.name,
                num: tile.item.num,
                refresh_remain: tile.item.refresh_remain,
                x: x, y: flip(y),
                overlap: !!tile.player,
            })
        }
    }
    const tradeArray = []
    for ( const [idsStr, [item, num]] of Object.entries(transactionGraph)) {
        const [id0, id1] = idsStr.slice(1, -1).split(',').map(Number)
        const [x0, y0] = playerPos[id0]
        const [x1, y1] = playerPos[id1]
        tradeArray.push({
            id0: id0, id1: id1,
            item: item, num: num,
            coords: [x0, flip(y0), x1, flip(y1)]
        })
    }
    const indexArray = Array.from({length: mapSize * mapSize}, (_, i) => [Math.floor(i / mapSize), i %mapSize])
    
    const transitions = useTransition(
        playerArray,
        {
            key: ({id}) => (id),
            from: ({ x, y }) => ({ x: x, y: y }),
            enter: ({ x, y }) => ({ x: x, y: y }),
            update: ({ x, y }) => ({ x: x, y: y }),
            config: {
                duration: 130
            },
        })
    
    return (<svg className='grid-world' id='svg-root' xmlns="http://www.w3.org/2000/svg" viewBox={`0 0 ${mapSize} ${mapSize}`}>
        {/* Grid world */}
        <g className='grid-board'>
            {indexArray.map(([x, y], i) =>
                <rect key={i}
                    className="grid-cell"
                    x={x} y={y}
                    width={1} height={1}
                />
            )}
        </g>
        {/* Item */}
        {itemArray.map(({name, x, y, num, refresh_remain, overlap}, i) =>
            <g key={i}
                className={num == 0 ? ' grid-harvested' : ''}
                data-tooltip-id='tooltip'
                data-tooltip-html={
                    `<div>${name}<br />` +
                    `&nbsp;&nbsp;num : ${num}<br />` +
                    `&nbsp;&nbsp;refresh remain: ${refresh_remain}<br />` +
                    `</div>`
                }
            >
                <image
                    width={1} height={1}
                    href={`/svg/${name}.svg`}
                    x={x} y={y}
                />
            </g>
        )}
        {/* Player */}
        {transitions((style, {id, pos, persona, overlap}) =>
            <animated.g key={id} style={style}
                data-tooltip-id='tooltip'
                data-tooltip-html={
                    `<div>${persona}<br />` +
                    `&nbsp;&nbsp;id : ${id}<br />` +
                    `&nbsp;&nbsp;pos: ${pos}<br />` +
                    `</div>`}
                onMouseDown={() => { dispatch({ type: 'CLICK_PLAYER', value: id }) }}
            >
                <image
                    className={(id == focusPlayerId ? 'grid-focus' : '') + (overlap ? ' grid-overlap' : '')}
                    href={`/svg/${persona}.svg`}
                    width={16}
                    height={16}
                    transform='scale(0.0625)'
                />                    
            </animated.g>
        )}
        {/* Trade */}
        {tradeArray.map(({id0, id1, coords, num, item}, i) =>
            <g key={i}
                data-tooltip-id='tooltip'
                data-tooltip-content={`${num} ${item} (${id0}->${id1})`}
                className={`color-${item}--trade-line`}
            >
                <LineSvg coords={coords} />
            </g>
        )}
    </svg >)
}