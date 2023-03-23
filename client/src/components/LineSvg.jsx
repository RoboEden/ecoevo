export const LineSvg = ({from, to}) => {
    const [x0, y0] = from.map(x=>x+0.5)
    const [x1, y1] = to.map(x=>x+0.5)
    const dx = x1 - x0
    const dy = y1 - y0

    const S = 0.3
    const A = Math.atan2(dy, dx) * 180 / Math.PI
    const L = Math.sqrt(dx * dx + dy * dy) / S
    return <g opacity={0.8} transform={`translate(${x0}, ${y0}) scale(${S}) rotate(${A})`}>
        <polygon points={`${L/2},-0.5 ${L/2},0.5 ${L-2},0.5 ${L-2},1 ${L},0 ${L-2},-1 ${L-2},-0.5`} />
        {/* <polygon points={`${L/2},-0.5 ${L/2},0.5 ${L},0`} /> */}
        {/* <rect width={L/2} height={1} y={-0.5} /> */}
    </g>
}

export const LineSvg2 = ({from, to}) => {
    const [x0, y0] = from.map(x=>x+0.5)
    const [x1, y1] = to.map(x=>x+0.5)
    const dx = x1 - x0
    const dy = y1 - y0

    const S = 0.5
    const A = Math.atan2(dy, dx) * 180 / Math.PI
    const L = Math.sqrt(dx * dx + dy * dy) / S
    return <g opacity={0.8} transform={`translate(${x0}, ${y0}) scale(${S}) rotate(${A})`}>
        <polygon points={`${L},0 ${L-1},-1 ${L-1},-0.5 0,-0.5 0,0`} />
        {/* <polygon points={`${L-1},-0.5 ${L-1},-1 ${L},0 ${L-1},1 ${L-1},0.5 1,-0.5`} /> */}
        {/* <polygon points={`${L},0 ${L-1},-1 ${L-1},-0.5 0,0`} /> */}
    </g>
}