export const GridWorld = ({ state }) => {
    const mapWidth = state.mapSize
    const mapHeight = state.mapSize
    const xyArray = []
    for (let i = 0; i < mapWidth * mapHeight; i++) {
        xyArray.push([Math.floor(i / mapWidth), i % mapWidth])
    }

    return (<svg xmlns="http://www.w3.org/2000/svg" className='grid-world' id='svg-root' >
        {xyArray.map(([x, y], i) =>
            <rect key={i} className='grid' id={`g-x${x}-y${y}`}
                x={2 * x + 'rem'} y={2 * y + 'rem'}
                data-tooltip-id="my-tooltip"
                data-tooltip-content="Hello world!"
                data-tooltip-place="top"
            />)}
    </svg>)
}