import { useCallback, useRef, createElement } from 'react'
import { getSvgPath } from 'figma-squircle'

// §0: every [data-squircle] gets clip-path: path(...) computed from its
// computed border-radius, cornerSmoothing .6 (or the attribute value),
// preserveSmoothing false. Recomputed by a ResizeObserver and on fonts.ready.

const apply = (el) => {
  const w = el.offsetWidth
  const h = el.offsetHeight
  if (!w || !h) return
  const cs = getComputedStyle(el)
  const r = (p) => parseFloat(cs.getPropertyValue(p)) || 0
  const d = getSvgPath({
    width: w,
    height: h,
    topLeftCornerRadius: r('border-top-left-radius'),
    topRightCornerRadius: r('border-top-right-radius'),
    bottomRightCornerRadius: r('border-bottom-right-radius'),
    bottomLeftCornerRadius: r('border-bottom-left-radius'),
    cornerSmoothing: parseFloat(el.dataset.squircle ?? '') || 0.6,
    preserveSmoothing: false,
  })
  el.style.clipPath = `path("${d}")`
}

let ro = null
const tracked = new Set()
const getObserver = () => {
  if (!ro && typeof ResizeObserver !== 'undefined') {
    ro = new ResizeObserver((entries) => entries.forEach((e) => apply(e.target)))
    document.fonts?.ready.then(() => tracked.forEach(apply))
  }
  return ro
}

export function useSquircle() {
  const elRef = useRef(null)
  return useCallback((el) => {
    const obs = getObserver()
    if (elRef.current && elRef.current !== el) {
      obs?.unobserve(elRef.current)
      tracked.delete(elRef.current)
    }
    elRef.current = el
    if (el) {
      tracked.add(el)
      apply(el)
      obs?.observe(el)
    }
  }, [])
}

// <Squircle as="span" className="..."> renders the element with data-squircle
// and the clip-path hook attached.
export default function Squircle({ as = 'div', smoothing, children, ...props }) {
  const ref = useSquircle()
  return createElement(as, { ...props, ref, 'data-squircle': smoothing ?? '' }, children)
}
