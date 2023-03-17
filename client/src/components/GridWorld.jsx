import ReactDOMServer from 'react-dom/server'
import { useTransition, animated } from '@react-spring/web'
import { useSelector, useDispatch } from 'react-redux'
import gridScssVar from '../grid.scss?inline'

const gridSize = Number(gridScssVar.match(/grid\W+width:.+rem/g)[0].match(/[\d\.]/g).join(''))
const playerSize = Number(gridScssVar.match(/player-svg\W+width:.+rem/g)[0].match(/[\d\.]/g).join(''))
const itemSize = Number(gridScssVar.match(/item-svg\W+width:.+rem/g)[0].match(/[\d\.]/g).join(''))

export const GridWorld = () => {
    const mapSize = useSelector((state) => state.mapSize)
    const dataMap = useSelector((state) => state.data.map)
    const dispatch = useDispatch()

    const itemRem = (n) => { return gridSize * n + (gridSize - itemSize) * 0.5 + 'rem' }
    const playerRem = (n) => { return gridSize * n + (gridSize - playerSize) * 0.5 + 'rem' }
    const centerRem = (n) => { return gridSize * (n + 0.5) }

    const mapArray = Object.entries(dataMap ?? {})
        .map(([rawPos, tile]) => {
            const [x, y] = rawPos.replace(new RegExp(/^\(|\)$/, "g"), "").split(",").map(Number)
            return { ...tile, x: x, y: y }
        })

    const transitions = useTransition(
        mapArray,
        {
            key: (tile) => tile.player?.id,
            from: ({ x, y }) => ({ x: playerRem(x), y: playerRem(y) }),
            enter: ({ x, y }) => ({ x: playerRem(x), y: playerRem(y) }),
            update: ({ x, y }) => ({ x: playerRem(x), y: playerRem(y) }),
            config: {
                duration: 130
            },
        })

    return (<svg className='grid-world' id='svg-root' xmlns="http://www.w3.org/2000/svg">
        {/* Grid world */}
        {(mapSize === undefined) ? null :
            Array.from(Array(Math.pow(mapSize, 2)))
                .map((_, i) => [Math.floor(i / mapSize), i % mapSize])
                .map(([x, y], i) =>
                    <rect className='grid' key={i}
                        id={`g-x${x}-y${y}`}
                        x={gridSize * x + 'rem'} y={gridSize * y + 'rem'} />)}
        {/* Item */}
        {mapArray.map((tile, i) =>
            (tile.item === null) ? null :
                <image key={i}
                    href={`/svg/${tile.item.name}.svg`}
                    x={itemRem(tile.x)}
                    y={itemRem(tile.y)}
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
                    style={style}
                    href={`/svg/${tile.player.persona}.svg`}
                    className='player-svg highlight'
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
                >
                </animated.image>
        )}
    </svg >)
}