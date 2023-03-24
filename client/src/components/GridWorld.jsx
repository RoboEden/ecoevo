import ReactDOMServer from 'react-dom/server'
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

    const mapSize = useSelector((state) => state.mapSize)
    const dataMap = useSelector((state) => state.data.map)??{}
    const transactionGraph = useSelector((state) => state.data.info?.transaction_graph)??{}
    const clickedId = useSelector((state) => state.clickedId)
    const dispatch = useDispatch()

    const players = {}
    for ( const tile of Object.values(dataMap) ) {
        if (tile.player) {
            players[tile.player.id] = tile.player
        }
    }

    const mapArray = Object.entries(dataMap ?? {})
        .map(([rawPos, tile]) => {
            const [x, y] = rawPos.replace(new RegExp(/^\(|\)$/, "g"), "").split(",").map(Number)
            return { ...tile, x: x, y: y }
        })

    const gridSize = 20
    const gridX = (x) => x * gridSize
    const gridY = (y) => (mapSize-1-y) * gridSize
    const gridPos = ([x, y]) => [gridX(x), gridY(y)]
    
    const transitions = useTransition(
        mapArray,
        {
            key: (tile) => tile.player?.id,
            from: ({ x, y }) => ({ x: gridX(x), y: gridY(y) }),
            enter: ({ x, y }) => ({ x: gridX(x), y: gridY(y) }),
            update: ({ x, y }) => ({ x: gridX(x), y: gridY(y) }),
            config: {
                duration: 130
            },
        })

    return (<svg className='grid-world' id='svg-root' xmlns="http://www.w3.org/2000/svg" viewBox={`0 0 ${gridSize * mapSize} ${gridSize * mapSize}`}>
        {/* Grid world */}
        <svg className='grid-board'>
            {(mapSize === undefined) ? null :
                Array.from(Array(Math.pow(mapSize, 2)))
                    .map((_, i) => [Math.floor(i / mapSize), i % mapSize])
                    .map(([x, y], i) =>
                        <rect key={i} className="grid-cell"
                            id={`g-x${x}-y${y}`}
                            x={gridX(x)} y={gridY(y)}
                            width={gridSize} height={gridSize}
                        />
            )}
        </svg>
        {/* Item */}
        {mapArray.map((tile, i) =>
            (tile.item === null) ? null :
                <image key={i} width={gridSize} height={gridSize}
                    href={`/svg/${tile.item.name}.svg`}
                    x={gridX(tile.x)}
                    y={gridY(tile.y)}
                    className='item-svg highlight'
                    id={`item-x${tile.x}-y${tile.y}`}
                    opacity={(tile.item.num === 0) ? '0.2' : ((tile.player) ? '0.6' : '0.8')}
                    data-tooltip-id='tooltip'
                    data-tooltip-html={
                        ReactDOMServer.renderToStaticMarkup(
                            <div>{tile.item.name}<br />
                                &nbsp;&nbsp;num : {tile.item.num}<br />
                                &nbsp;&nbsp;refresh remain: {tile.item.refresh_remain}<br />
                            </div>)} />
        )}
        {/* Player */}
        {transitions((style, tile) =>
            (tile.player === null) ? undefined :
                <animated.image
                    width={gridSize}
                    height={gridSize}
                    style={style}
                    href={`/svg/${tile.player.persona}.svg`}
                    className={'player-svg highlight' + (tile.player.id == clickedId ? ' grid-focus' : '')}
                    id={`player-${tile.player.id}`}
                    opacity={(tile.item) ? 0.8 : 1}
                    data-tooltip-id='tooltip'
                    data-tooltip-html={
                        ReactDOMServer.renderToStaticMarkup(
                            <div>{tile.player.persona}<br />
                                &nbsp;&nbsp;id : {tile.player.id}<br />
                                &nbsp;&nbsp;pos: {tile.x}, {tile.y}<br />
                            </div>)}
                    onMouseDown={() => { dispatch({ type: 'CLICKED_ID', clickedId: tile.player.id }) }}
                />
        )}
        {/* Trade */}
        {Object.entries(transactionGraph).map(([ids, [item, num]]) => {
            const [id0, id1] = ids.slice(1, -1).split(',').map(Number)
            return <g
                key={ids}
                data-tooltip-id='tooltip'
                data-tooltip-content={`${num} ${item} (${id0}->${id1})`}
                className={`color-${item}--trade-line`} >
                    <LineSvg from={gridPos(players[id0].pos)} to={gridPos(players[id1].pos)} gridSize={gridSize} />
            </g>
        })}
    </svg >)
}