import { useEffect, useRef } from 'react'
import Squircle from './Squircle.jsx'
import Eyebrow from './Eyebrow.jsx'
import HeroMockup from './HeroMockup.jsx'
import Funnel from './Funnel.jsx'
import WaitlistForm from './WaitlistForm.jsx'
import { Spark } from './icons.jsx'
import { initBookmark, initTags } from '../lib/bookmark.js'

// §3 Hero block: header[data-bookmark] holding the hero text, the demo
// mockup, the funnel and the falling tags.
export default function Hero() {
  const headerRef = useRef(null)

  useEffect(() => {
    const header = headerRef.current
    if (!header) return
    const offClip = initBookmark(header)
    const offTags = initTags(header)
    return () => {
      offClip()
      offTags()
    }
  }, [])

  return (
    <div className="px-2 sm:px-3">
      <header ref={headerRef} data-bookmark="" className="relative mx-auto max-w-[1440px] rounded-b-[3.5rem] bg-surface-raised">
        <section className="mx-auto max-w-4xl px-6 pb-16 pt-16 text-center sm:pb-20 sm:pt-24">
          <Eyebrow as="p" tone="sunken" icon={<Spark className="size-[18px] shrink-0" />}>
            Bookmarks with a Brain
          </Eyebrow>

          <h1 className="hero-h1 mt-5 font-display text-[length:clamp(2.75rem,8.5vw,5.25rem)] font-semibold leading-[1.02]">
            <span className="line">Everything you saved</span>
            <span className="line">
              <span className="mark px-[0.23em]">
                <Squircle as="span" className="mark-fill rounded-[0.23em]" aria-hidden="true" />
                finally
              </span>
              {/* one text node, as in the original: separate " " + "findable" nodes shape differently */}
              {' findable'}
            </span>
          </h1>

          <p className="mx-auto mt-8 max-w-lg text-pretty text-[19px] leading-relaxed text-text-muted">
            Your personal inspiration library that remembers<br className="hidden sm:inline" /> not just what you saved, but why.
          </p>

          <div id="waitlist" className="mt-10 scroll-mt-24">
            <WaitlistForm id="waitlist-hero" variant="hero" />
          </div>
        </section>

        <HeroMockup />
        <Funnel />
      </header>
    </div>
  )
}
