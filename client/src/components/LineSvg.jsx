export const LineSvg = ({coords}) => {
    const [x0, y0, x1, y1] = coords
    const xm = (x0 + x1) / 2
    const ym = (y0 + y1) / 2
    const dx = x1 - xm
    const dy = y1 - ym

    const L = Math.sqrt(dx * dx + dy * dy)
    const A = Math.atan2(dy, dx) * 180 / Math.PI
    const L2 = Math.max(L - 0.86, 0.05)
    return <g opacity={0.8} transform={`translate(${xm+0.5}, ${ym+0.5}) rotate(${A})`}>
        <rect width={L2} height="0.3" y="-0.15"></rect>
        <polygon transform={`translate(${L2})`} points={`0,-0.35 0,0.35 0.606,0`} />
    </g>
}
