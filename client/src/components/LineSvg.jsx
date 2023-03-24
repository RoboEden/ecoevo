export const LineSvg = ({from, to, gridSize}) => {
    const [x0, y0] = from.map(x=>x/gridSize+0.5)
    const [x1, y1] = to.map(x=>x/gridSize+0.5)
    const dx = x1 - x0
    const dy = y1 - y0

    const L = Math.sqrt(dx * dx + dy * dy)
    const A = Math.atan2(dy, dx) * 180 / Math.PI // rotate angle
    const W = 0.3   // line width
    const W0 = 0.7    // head width
    const LS = L > 1.5 ? 0.4 : 0  // head start
    const LT = L > 1.5 ? 0.9 : 0.4 // head end
    return <g opacity={0.8} transform={`scale(${gridSize}) translate(${x0}, ${y0}) rotate(${A})`}>
        <polygon points={`${L/2},${-W/2} ${L/2},${W/2} ${L-LT},${W/2} ${L-LT},${W0/2} ${L-LS},0 ${L-LT},${-W0/2} ${L-LT},${-W/2}`} />
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