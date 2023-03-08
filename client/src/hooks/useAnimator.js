import { useEffect, useRef } from "react"
import { gsap } from 'gsap'

export class Animator {
    constructor(root) {
        this.root = root
        this.secondPerStep = 0.2
        this.playerSize = '1.6rem'
        this.itmeSize = '1.8rem'
        this.prevPos = {}
    }
    itemCoord(n) { return 2 * n + 0.1 + 'rem' }
    playerCoord(n) { return 2 * n + 0.2 + 'rem' }
    centerCoord(n) { return 2 * n + 1 }
    loadSvg(path, width, height) {
        let image = document.createElementNS('http://www.w3.org/2000/svg', 'image')
        image.setAttribute('width', `${width}`)
        image.setAttribute('height', `${height}`)
        image.setAttribute('href', path)
        return image
    }
    load(map) {
        if (map === undefined) return
        console.time('Resource loading finished in')
        for (const [pos, tile] of Object.entries(map)) {
            const [x, y] = pos.replace(new RegExp(/^\(|\)$/, "g"), "").split(",").map(Number)
            if (tile.item) {
                const itemSvg = this.loadSvg(`/svg/${tile.item.name}.svg`, this.itmeSize, this.itmeSize)
                itemSvg.setAttribute('id', `item-x${x}-y${y}`)
                itemSvg.setAttribute('opacity', '0.8')
                itemSvg.setAttribute('data-tooltip-id', 'tooltip')
                itemSvg.setAttribute('data-tooltip-html',
                    `<div>${tile.item.name}<br/>
                    &nbsp;&nbsp;num : ${tile.item.num}<br/>
                    &nbsp;&nbsp;refresh remain: ${tile.item.refresh_remain}<br/>
                    </div>`)
                this.root.append(itemSvg)
                gsap.to(itemSvg, { duration: 0, x: this.itemCoord(x), y: this.itemCoord(y), svgOrigin: "0 0" })
            }
            if (tile.player) {
                const playerSvg = this.loadSvg(`/svg/${tile.player.persona}.svg`, this.playerSize, this.playerSize)
                playerSvg.setAttribute('id', `player-${tile.player.id}`)
                playerSvg.setAttribute('opacity', (tile.item) ? '0.8' : '1')
                playerSvg.setAttribute('data-tooltip-id', 'tooltip')
                // playerSvg.setAttribute('data-tooltip-content', `${tile.player.persona} ${tile.player.id}`)
                playerSvg.setAttribute('data-tooltip-html',
                    `<div>${tile.player.persona}<br/>
                    &nbsp;&nbsp;id : ${tile.player.id}<br/>
                    &nbsp;&nbsp;pos: ${x}, ${y}<br/>
                    </div>`)
                this.prevPos[tile.player.id] = [x, y]

                this.root.append(playerSvg)
                gsap.to(playerSvg, { duration: 0, x: this.playerCoord(x), y: this.playerCoord(y), svgOrigin: "0 0" })
            }
            // customdata_item.push([tile.item.name, tile.item.num])
        }
        console.timeEnd('Resource loading finished in')
    }
    render(map) {
        if (map === undefined) return
        for (const [pos, tile] of Object.entries(map)) {
            const [x, y] = pos.replace(new RegExp(/^\(|\)$/, "g"), "").split(",").map(Number)
            if (tile.item) {
                const itemSvg = document.getElementById(`item-x${x}-y${y}`)
                itemSvg.setAttribute('opacity', (tile.item.num === 0) ? '0.2' : '0.8')
                // itemSvg.setAttribute('data-tooltip-content', `${tile.item.name} ${tile.item.num} ${tile.item.refresh_remain}`)
                itemSvg.setAttribute('data-tooltip-html',
                    `<div>${tile.item.name}<br/>
                    &nbsp;&nbsp;num : ${tile.item.num}<br/>
                    &nbsp;&nbsp;refresh remain: ${tile.item.refresh_remain}<br/>
                    </div>`)
                if (tile.item.num !== 0) itemSvg.setAttribute('opacity', (tile.player) ? '0.6' : '0.8')
            }
            if (tile.player) {
                const [prev_x, prev_y] = this.prevPos[tile.player.id]
                if (prev_x !== x || prev_y !== y) {
                    const playerSvg = document.getElementById(`player-${tile.player.id}`)
                    playerSvg.setAttribute('opacity', (tile.item) ? '0.8' : '1')
                    playerSvg.setAttribute('data-tooltip-html',
                        `<div>${tile.player.persona}<br/>
                        &nbsp;&nbsp;id : ${tile.player.id}<br/>
                        &nbsp;&nbsp;pos: ${x}, ${y}<br/>
                        </div>`)
                    this.prevPos[tile.player.id] = [x, y]
                    gsap.fromTo(playerSvg,
                        { x: this.playerCoord(prev_x), y: this.playerCoord(prev_y) },
                        { x: this.playerCoord(x), y: this.playerCoord(y), duration: this.secondPerStep })
                }
                // customdata_player.push([tile.player.persona, tile.player.id])
            }
        }
    }
    trade(transactionGraph) {
        Array.from(document.querySelectorAll("[id='trade-lines']"))?.map((el) => { el.remove() })
        if (transactionGraph === undefined || Object.keys(transactionGraph).length === 0) {
            return
        }
        const tradeLines = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
        tradeLines.setAttribute('viewBox', '0 0 64 64')
        tradeLines.setAttribute('id', 'trade-lines')
        for (const [giveNTake, offer] of Object.entries(transactionGraph)) {
            const [giveId, takeId] = giveNTake.replace(new RegExp(/^\(|\)$/, "g"), "").split(",").map(Number)
            const [giveItem, giveNum] = offer
            const [xcG, ycG] = this.prevPos[giveId].map(this.centerCoord)
            const [xcT, ycT] = this.prevPos[takeId].map(this.centerCoord)
            const newpath = document.createElementNS('http://www.w3.org/2000/svg', "path")
            const xcM = (xcG + xcT) / 2
            const ycM = (ycG + ycT) / 2
            newpath.setAttributeNS(null, "d", `M ${xcG} ${ycG} L ${xcM} ${ycM}`)
            newpath.setAttribute("class", `${giveItem}--trade-line`)
            newpath.setAttribute("stroke-width", 0.3)
            newpath.setAttribute("stroke-opacity", 0.3)
            newpath.setAttribute('data-tooltip-id', 'tooltip')
            newpath.setAttribute("data-tooltip-content", `${giveNum} ${giveItem} (${giveId}->${takeId})`)
            tradeLines.append(newpath)
        }
        this.root.append(tradeLines)
    }
}

export const useAnimator = () => {
    const rd = useRef()
    useEffect(() => {
        rd.current = new Animator(document.getElementById('svg-root'))
    }, [])
    const load = (map) => { rd.current.load(map) }
    const render = (map) => { rd.current.render(map) }
    const trade = (transactionGraph) => { rd.current.trade(transactionGraph) }
    return [load, render, trade]
}