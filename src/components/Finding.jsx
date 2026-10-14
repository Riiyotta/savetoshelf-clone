import { useEffect, useRef } from 'react'
import Palette from './Palette.jsx'

// §4 section#finding
export default function Finding() {
  const revealRef = useRef(null)

  useEffect(() => {
    const e = revealRef.current
    if (!e) return
    const io = new IntersectionObserver(
      (entries) =>
        entries.forEach((r) => {
          if (r.isIntersecting) {
            e.classList.add('is-in')
            return
          }
          e.classList.add('no-anim')
          e.classList.remove('is-in')
          requestAnimationFrame(() => e.classList.remove('no-anim'))
        }),
      { rootMargin: '0px 0px -32% 0px' },
    )
    io.observe(e)
    return () => io.disconnect()
  }, [])

  return (
    <section id="finding">
      <div className="mx-auto max-w-4xl px-6 pb-20 text-center sm:pb-28">
        <div ref={revealRef} data-reveal="">
          <span className="line mx-auto block h-24 w-px bg-gradient-to-b from-transparent to-border-strong sm:h-32" aria-hidden="true" />
          <h2 className="reveal mx-auto mt-8 max-w-3xl text-balance font-display text-[36px] font-semibold leading-[1.1] sm:text-[48px]">
            <span className="inline-block">You can find them in one place now</span>
          </h2>
          <p className="reveal mx-auto mt-5 max-w-xl text-pretty text-[17px] leading-relaxed text-text-muted">
            <span className="inline-block">
              Shelf catches all twelve of them. Ask in the same words you would use out loud, and it answers with what you saved, and why you saved it.
            </span>
          </p>
        </div>

        <Palette
          variant="finding"
          className="mt-14 text-left"
          question="Every LinkedIn post about Webflow pricing I saved"
          chips={['source: LinkedIn', 'topic: pricing', 'Webflow']}
          hits={[
            {
              title: "Why Webflow's per-site pricing breaks agency retainers",
              sub: 'LinkedIn, saved for the anchoring argument in the client deck',
              date: '12 Aug',
              thumb: 'bg-swatch-sky',
            },
            {
              title: 'webflow.com/pricing',
              sub: 'Web, saved while comparing the Growth and Agency tiers',
              date: '3 Aug',
              thumb: 'bg-surface-sunken',
            },
          ]}
          total={9}
        />
      </div>
    </section>
  )
}
