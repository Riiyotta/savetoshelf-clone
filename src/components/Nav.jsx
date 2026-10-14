import { useEffect, useRef } from 'react'
import Squircle from './Squircle.jsx'
import { LogoBooks, ArrowRight } from './icons.jsx'

// §2 Nav
export default function Nav() {
  const navRef = useRef(null)

  useEffect(() => {
    const nav = navRef.current
    if (!nav) return
    // --nav-h = nav offsetHeight (76 at sm+, 72 below)
    const setH = () => document.documentElement.style.setProperty('--nav-h', `${nav.offsetHeight}px`)
    let queued = false
    const onScroll = () => {
      if (queued) return
      queued = true
      requestAnimationFrame(() => {
        queued = false
        nav.classList.toggle('is-stuck', window.scrollY > 12)
      })
    }
    setH()
    onScroll()
    const ro = new ResizeObserver(setH)
    ro.observe(nav)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      ro.disconnect()
      window.removeEventListener('scroll', onScroll)
    }
  }, [])

  const links = [
    ['Finding', '#finding'],
    ['Saving', '#saving'],
    ['FAQ', '#faq'],
  ]

  return (
    <nav ref={navRef} data-nav="" className="fixed inset-x-0 top-0 z-50 px-2 pt-2 sm:px-3 sm:pt-3" aria-label="Main">
      <div data-nav-bar="" className="relative mx-auto flex items-center justify-between rounded-[1rem] bg-surface-raised py-2 pr-2 pl-6">
        <a href="/" className="logo flex items-center gap-2" aria-label="Shelf, home">
          <LogoBooks className="size-7 overflow-visible" />
          <span className="sr-only">Shelf</span>
        </a>
        <div className="flex items-center gap-5 sm:gap-6">
          <ul className="hidden items-center gap-4 text-[15px] sm:flex sm:gap-5">
            {links.map(([label, href]) => (
              <li key={href}>
                <a href={href} className="text-text transition hover:text-text-muted">
                  {label}
                </a>
              </li>
            ))}
          </ul>
          <Squircle as="a" href="#waitlist" className="button-009" data-button-009="">
            <span className="button-009__inner">
              <ArrowRight className="button-009__icon is--left" />
              <span className="button-009__text">Join waitlist</span>
              <ArrowRight className="button-009__icon is--right" />
            </span>
            <span className="button-009__bg" />
          </Squircle>
        </div>
      </div>
    </nav>
  )
}
