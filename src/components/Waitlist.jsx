import { useEffect, useRef } from 'react'
import Squircle from './Squircle.jsx'
import WaitlistForm from './WaitlistForm.jsx'

// §7 Closing waitlist with the animated side blocks.
export default function Waitlist() {
  const blocksRef = useRef(null)

  useEffect(() => {
    const e = blocksRef.current
    if (!e) return
    const io = new IntersectionObserver(
      (entries) =>
        entries.forEach((r) => {
          if (r.isIntersecting) {
            e.classList.add('is-in')
            return
          }
          e.classList.remove('is-in')
        }),
      { rootMargin: '0px 0px -15% 0px' },
    )
    io.observe(e)
    return () => io.disconnect()
  }, [])

  return (
    <section className="px-2 sm:px-3">
      <div ref={blocksRef} data-blocks="" className="mx-auto flex max-w-[1440px] gap-2 sm:gap-3">
        <Squircle className="side left hidden shrink-0 rounded-[1.75rem] bg-accent lg:block" aria-hidden="true" />
        <Squircle className="min-w-0 flex-1 rounded-[1.75rem] bg-accent px-8 py-20 sm:px-14 sm:py-28">
          <h2 className="max-w-2xl text-balance font-display text-[36px] font-semibold leading-[1.05] sm:text-[48px]">Join the waitlist</h2>
          <p className="mt-5 max-w-lg text-pretty text-[17px] leading-relaxed text-text/70">
            Shelf is in private testing. The list moves in order, and members hear the price before anyone else.
          </p>
          <div className="mt-10">
            <WaitlistForm id="waitlist-closing" variant="closing" />
          </div>
        </Squircle>
        <Squircle className="side right hidden shrink-0 rounded-[1.75rem] bg-accent lg:block" aria-hidden="true" />
      </div>
    </section>
  )
}
