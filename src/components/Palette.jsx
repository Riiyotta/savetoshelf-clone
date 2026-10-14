import { useEffect, useRef } from 'react'
import { Magnifier } from './icons.jsx'

// §3.3 Palette component, shared by the hero mockup and #finding.
// variant "hero": rounded-2xl + shadow, no keep, question row without border-b,
//   chips row with border-t, 20px question / 24px caret, 52×38 thumbs, 14px subs.
// variant "finding": rounded 20px, no shadow, keep, question row border-b,
//   21px question / 26px caret, 56×40 thumbs, 15px subs.

export default function Palette({ variant, question, chips, hits, total, className = '' }) {
  const hero = variant === 'hero'
  const keep = !hero
  const rootRef = useRef(null)
  const typedRef = useRef(null)
  const caretRef = useRef(null)
  const chipsRef = useRef(null)
  const hitsRef = useRef(null)

  useEffect(() => {
    const M = rootRef.current
    const P = typedRef.current
    const A = caretRef.current
    const c = chipsRef.current
    const t = hitsRef.current
    if (!M || !P || !A || !c || !t) return

    let alive = true
    const timers = new Set()
    const sleep = (ms) =>
      new Promise((r) => {
        const id = window.setTimeout(() => {
          timers.delete(id)
          r()
        }, ms)
        timers.add(id)
      })

    const show = (s) => {
      if (!keep) s.style.display = ''
      requestAnimationFrame(() => {
        s.style.opacity = '1'
      })
    }
    const hide = (s) => {
      s.style.opacity = '0'
      if (!keep) {
        const id = window.setTimeout(() => {
          s.style.display = 'none'
        }, 320)
        timers.add(id)
      }
    }

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      P.textContent = question
      show(c)
      show(t)
      return
    }

    let visible = false
    const io = new IntersectionObserver((es) => es.forEach((e) => (visible = e.isIntersecting)), { threshold: 0.35 })
    io.observe(M)
    const untilVisible = async () => {
      while (!visible) {
        await sleep(400)
        if (!alive) return
      }
    }

    ;(async () => {
      while (alive) {
        await untilVisible()
        if (!alive) return
        M.classList.add('is-open')
        A.style.opacity = '1'
        await sleep(700)
        for (let s = 1; s <= question.length; s++) {
          if (!alive) return
          P.textContent = question.slice(0, s)
          await sleep(38 + Math.random() * 40)
        }
        await sleep(350)
        if (!alive) return
        show(c)
        await sleep(300)
        if (!alive) return
        show(t)
        await sleep(6500)
        if (!alive) return
        M.classList.remove('is-open')
        hide(c)
        hide(t)
        A.style.opacity = '0'
        await sleep(500)
        P.textContent = ''
        await sleep(1400)
      }
    })()

    return () => {
      alive = false
      io.disconnect()
      timers.forEach((id) => window.clearTimeout(id))
    }
  }, [question, keep])

  // Initial (closed) state: chips/hits hidden. Without keep they are also
  // display:none so the hero palette is 77px tall when closed.
  const closedStyle = keep ? { opacity: 0 } : { opacity: 0, display: 'none' }

  const qSize = hero ? 'text-[20px]' : 'text-[21px]'
  const caretH = hero ? 'h-[24px]' : 'h-[26px]'
  const thumb = hero ? 'h-[38px] w-[52px]' : 'h-[40px] w-[56px]'
  const sub = hero ? 'text-[14px]' : 'text-[15px]'

  return (
    <div
      ref={rootRef}
      data-palette=""
      data-palette-question={question}
      data-palette-animate=""
      {...(keep ? { 'data-palette-keep': '' } : {})}
      className={`overflow-hidden border border-border bg-surface-raised ${hero ? 'rounded-2xl shadow-palette' : 'rounded-[1.25rem]'} ${className}`}
    >
      <div className={`flex items-center gap-4 px-8 py-6 ${hero ? '' : 'border-b border-border'}`}>
        <Magnifier className="size-[22px] shrink-0 text-text-muted" />
        <span className={`min-w-0 flex-1 truncate ${qSize}`}>
          <span ref={typedRef} data-palette-typed="" />
          <span
            ref={caretRef}
            data-palette-caret=""
            className={`ml-0.5 inline-block w-px translate-y-[4px] bg-text opacity-0 ${caretH}`}
          />
        </span>
      </div>

      <div
        ref={chipsRef}
        data-palette-chips=""
        className={`flex items-center gap-3 px-8 py-4 transition-opacity duration-300 ${hero ? 'border-t border-border' : ''}`}
        style={closedStyle}
      >
        <span className="text-[14px] text-text-muted">Searching</span>
        {chips.map((chip, i) => (
          <span
            key={chip}
            className={`rounded-lg px-3.5 py-2 text-[14px] ${i === chips.length - 1 ? 'bg-surface-sunken text-text' : 'bg-surface text-text-muted'}`}
          >
            {chip}
          </span>
        ))}
      </div>

      <div ref={hitsRef} data-palette-hits="" className="transition-opacity duration-300" style={closedStyle}>
        <div className="border-t border-border px-8 pt-4 pb-2">
          <p className="text-[14px] text-text-muted">My shelf</p>
          <ul className="mt-2">
            {hits.map((h) => (
              <li key={h.title} className="flex items-center gap-4 py-3">
                <span className={`shrink-0 rounded-md ${thumb} ${h.thumb}`} />
                <span className="min-w-0 flex-1">
                  <span className="block text-[17px] font-medium">{h.title}</span>
                  <span className={`mt-0.5 block ${sub} text-text-muted`}>{h.sub}</span>
                </span>
                <span className="shrink-0 text-[13px] text-text-faint">{h.date}</span>
              </li>
            ))}
          </ul>
        </div>
        <p className="flex items-center justify-between bg-surface px-8 py-4 text-[17px] font-medium">
          Show all {total} results <span className={`${sub} font-normal text-text-faint`}>Enter</span>
        </p>
        <p className={`flex gap-8 border-t border-border px-8 py-3.5 ${sub} text-text-muted`}>
          <span>Enter to see all</span>
          <span>Tab to browse</span>
          <span>Esc to close</span>
        </p>
      </div>
    </div>
  )
}
