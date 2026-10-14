import Matter from 'matter-js'

// §3.4, ported from the original bundle (`kt`, `et`, `Wt`, `B`, and the tags
// physics block). Returns a cleanup function.

const cubicBezier = (x1, y1, x2, y2) => {
  const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx
  const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by
  const X = (t) => ((ax * t + bx) * t + cx) * t
  const Y = (t) => ((ay * t + by) * t + cy) * t
  const dX = (t) => (3 * ax * t + 2 * bx) * t + cx
  return (x) => {
    if (x <= 0) return 0
    if (x >= 1) return 1
    let t = x
    for (let i = 0; i < 8; i++) {
      const err = X(t) - x
      if (Math.abs(err) < 1e-5) return Y(t)
      const d = dX(t)
      if (Math.abs(d) < 1e-6) break
      t -= err / d
    }
    let lo = 0, hi = 1
    t = x
    for (let i = 0; i < 24; i++) {
      const err = X(t) - x
      if (Math.abs(err) < 1e-5) break
      err > 0 ? (hi = t) : (lo = t)
      t = (lo + hi) / 2
    }
    return Y(t)
  }
}

const ease = cubicBezier(0.45, 0, 0.55, 1)
const clamp01 = (v) => Math.min(1, Math.max(0, v))
const cssNum = (el, v, fb) => {
  const n = parseFloat(getComputedStyle(el).getPropertyValue(v))
  return Number.isFinite(n) ? n : fb
}

export function measure(el) {
  const { width: W, height: H, top } = el.getBoundingClientRect()
  if (!W || !H) return null
  const notch = cssNum(el, '--notch', 96)
  const hold = cssNum(el, '--hold', 180)
  const line = window.innerHeight * 0.7
  const a = H - hold
  const holdP = clamp01((line - top + notch - a) / hold)
  const base = a + hold * holdP
  const n = line - top - (H - notch)
  const tipP = clamp01(n / notch)
  const bendP = clamp01(n / cssNum(el, '--bend', 620))
  return { width: W, height: H, sideY: base - notch * ease(bendP), tipY: base - notch + notch * tipP, funnel: bendP, hold: holdP }
}

// y of the floor line at x (used for the reduced-motion placement)
const floorY = (x, m) => {
  const half = m.width / 2
  const u = half > 0 ? Math.min(1, Math.abs(x - half) / half) : 0
  return m.tipY + (m.sideY - m.tipY) * u
}

export function pathD(w, corner, sideY, tipY) {
  const L = { x: 0, y: sideY }, R = { x: w, y: sideY }, T = { x: w / 2, y: tipY }
  const s = Math.min(corner, sideY, w / 2)
  const toward = (p, q, d) => {
    const dx = q.x - p.x, dy = q.y - p.y, len = Math.hypot(dx, dy) || 1, u = Math.min(d / len, 0.5)
    return { x: p.x + dx * u, y: p.y + dy * u }
  }
  const e = toward(R, T, s), i = toward(T, R, s), o = toward(T, L, s), f = toward(L, T, s)
  return [
    'M 0 0',
    `H ${w}`,
    `V ${sideY - s}`,
    `Q ${R.x} ${R.y} ${e.x} ${e.y}`,
    `L ${i.x} ${i.y}`,
    `Q ${T.x} ${T.y} ${o.x} ${o.y}`,
    `L ${f.x} ${f.y}`,
    `Q ${L.x} ${L.y} 0 ${sideY - s}`,
    'Z',
  ].join(' ')
}

// ---- Clip-path + funnel trigger ----
export function initBookmark(header) {
  const trigger = header.querySelector('[data-funnel-trigger]')
  let queued = false
  const update = () => {
    queued = false
    const m = measure(header)
    if (!m) return
    const corner = parseFloat(getComputedStyle(header).getPropertyValue('--corner')) || 56
    header.style.clipPath = `path("${pathD(m.width, corner, m.sideY, m.tipY)}")`
    trigger?.classList.toggle('is-in', m.hold >= 0.45)
  }
  const onScroll = () => {
    if (queued) return
    queued = true
    requestAnimationFrame(update)
  }
  update()
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('resize', onScroll)
  return () => {
    window.removeEventListener('scroll', onScroll)
    window.removeEventListener('resize', onScroll)
  }
}

// ---- Falling tags ----
const WALL = 240
const PAD = 24

export function initTags(header) {
  const tagsEl = header.querySelector('[data-tags]')
  const funnel = header.querySelector('[data-funnel]')
  if (!tagsEl) return () => {}
  const { Engine, Bodies, Body, Composite, Vertices } = Matter

  const tags = Array.from(tagsEl.querySelectorAll('[data-tag]'))
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const engine = Engine.create({ enableSleeping: false })
  const G_FALL = 2.4
  const G_RELEASE = -3.2
  engine.gravity.y = G_FALL

  const floorL = Bodies.rectangle(0, 0, 10, 10, { isStatic: true, friction: 0.6 })
  const floorR = Bodies.rectangle(0, 0, 10, 10, { isStatic: true, friction: 0.6 })
  const wallL = Bodies.rectangle(0, 0, 10, 10, { isStatic: true })
  const wallR = Bodies.rectangle(0, 0, 10, 10, { isStatic: true })
  Composite.add(engine.world, [floorL, floorR, wallL, wallR])

  let items = []
  let started = false
  let lastT = 0
  let gen = 0
  let idle = true
  let releasing = false
  let lastShape = ''
  let down = true
  let lastY = window.scrollY
  let ready = false
  let disposed = false

  const setShape = (body, verts) => {
    Body.setAngle(body, 0)
    Body.setVertices(body, verts)
    Body.setPosition(body, Vertices.centre(verts))
  }
  const slab = (x1, y1, x2, y2) => [
    { x: x1, y: y1 },
    { x: x2, y: y2 },
    { x: x2, y: y2 + WALL },
    { x: x1, y: y1 + WALL },
  ]
  const updateFloor = (m) => {
    const half = m.width / 2
    setShape(floorL, slab(-PAD, m.sideY, half, m.tipY))
    setShape(floorR, slab(half, m.tipY, m.width + PAD, m.sideY))
    setShape(wallL, [{ x: -WALL, y: 0 }, { x: 0, y: 0 }, { x: 0, y: m.height }, { x: -WALL, y: m.height }])
    setShape(wallR, [{ x: m.width, y: 0 }, { x: m.width + WALL, y: 0 }, { x: m.width + WALL, y: m.height }, { x: m.width, y: m.height }])
  }
  const spawnY = (m) => (funnel ? funnel.offsetTop - 40 : m.height - 40)

  const spawn = () => {
    const m = measure(header)
    if (!m) return
    items.forEach((it) => Composite.remove(engine.world, it.body))
    const y0 = spawnY(m)
    const order = [...tags]
    for (let i = order.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      ;[order[i], order[j]] = [order[j], order[i]]
    }
    let x = PAD
    let rowN = 0
    items = order.map((el) => {
      const w = el.offsetWidth
      const h = el.offsetHeight
      if (x + w > m.width - PAD) {
        rowN += 1
        x = PAD
      }
      const cx = x + w / 2 + (Math.random() - 0.5) * 18
      x += w + 34
      const body = Bodies.rectangle(cx, y0 - rowN * (h + 30) - Math.random() * 150, w, h, {
        chamfer: { radius: h / 2 },
        restitution: 0.2,
        friction: 0.28,
        frictionStatic: 0.25,
        frictionAir: 0.055,
      })
      Body.setAngle(body, (Math.random() - 0.5) * 1)
      Body.setAngularVelocity(body, (Math.random() - 0.5) * 0.26)
      Body.setVelocity(body, { x: (Math.random() - 0.5) * 6, y: Math.random() * 3 })
      return { el, body, width: w, height: h, delay: 0, live: false }
    })
    updateFloor(m)
  }

  const render = (it) => {
    it.el.style.visibility = 'visible'
    it.el.style.transform = `translate(${it.body.position.x - it.width / 2}px, ${it.body.position.y - it.height / 2}px) rotate(${it.body.angle}rad)`
  }

  const step = (g) => (now) => {
    if (g !== gen || disposed) return
    const m = measure(header)
    if (!m) return
    const dt = Math.min(32, now - lastT)
    lastT = now
    updateFloor(m)
    const shape = `${m.sideY.toFixed(1)}|${m.tipY.toFixed(1)}|${m.width}`
    const shapeChanged = shape !== lastShape
    lastShape = shape
    if (releasing) {
      const top = header.getBoundingClientRect().top
      if (items.every((it) => !it.live || top + it.body.position.y < -it.height - 40)) {
        reset()
        return
      }
    }
    let pending = false
    items.forEach((it) => {
      if (!it.live) {
        it.delay -= dt / 1000
        if (it.delay > 0) {
          pending = true
          return
        }
        it.live = true
        Composite.add(engine.world, it.body)
      }
    })
    Engine.update(engine, dt)
    items.forEach((it) => it.live && render(it))
    const moving = items.some((it) => it.live && (it.body.speed > 0.05 || Math.abs(it.body.angularSpeed) > 0.0015))
    if (!(pending || shapeChanged || releasing || moving)) {
      idle = true
      return
    }
    requestAnimationFrame(step(g))
  }

  const wake = () => {
    if (!idle || !started) return
    idle = false
    lastT = performance.now()
    gen += 1
    requestAnimationFrame(step(gen))
  }

  const start = () => {
    if (started) return
    started = true
    releasing = false
    engine.gravity.y = G_FALL
    spawn()
    if (reduced) {
      const m = measure(header)
      if (!m) return
      items.forEach((it) => {
        it.live = true
        Body.setPosition(it.body, { x: it.body.position.x, y: floorY(it.body.position.x, m) - it.height / 2 })
        Body.setAngle(it.body, 0)
        render(it)
      })
      return
    }
    wake()
  }

  function reset() {
    started = false
    releasing = false
    idle = true
    gen += 1
    engine.gravity.y = G_FALL
    items.forEach((it) => {
      it.el.style.visibility = 'hidden'
      it.el.style.transform = ''
      it.live = false
      Composite.remove(engine.world, it.body)
    })
  }

  const release = () => {
    if (!started || releasing) return
    releasing = true
    engine.gravity.y = G_RELEASE
    items.forEach((it) => {
      if (!it.live) return
      Body.setVelocity(it.body, { x: (Math.random() - 0.5) * 6, y: -(9 + Math.random() * 7) })
      Body.setAngularVelocity(it.body, (Math.random() - 0.5) * 0.3)
    })
    wake()
  }

  const onScroll = () => {
    const d = window.scrollY - lastY
    if (Math.abs(d) > 2) down = d > 0
    lastY = window.scrollY
    const m = measure(header)
    if (!m || !ready) return
    if (!started && down && m.hold >= 0.45) start()
    else if ((started && !releasing && !down && m.hold < 0.42) || (started && m.hold < 0.15)) release()
    else wake()
  }

  const firstCheck = () => {
    if (disposed) return
    lastY = window.scrollY
    ready = true
    const m = measure(header)
    if (m && !started && m.hold >= 0.45) start()
  }

  const onResize = () => {
    if (started) {
      reset()
      start()
    }
  }

  let firstTimer = null
  const onLoad = () => {
    firstTimer = setTimeout(firstCheck, 300)
  }
  if (document.readyState === 'complete') onLoad()
  else window.addEventListener('load', onLoad, { once: true })
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('resize', onResize)

  return () => {
    disposed = true
    gen += 1
    clearTimeout(firstTimer)
    window.removeEventListener('load', onLoad)
    window.removeEventListener('scroll', onScroll)
    window.removeEventListener('resize', onResize)
    Engine.clear(engine)
  }
}
