import { useEffect } from 'react'
import Lenis from 'lenis'
import 'lenis/dist/lenis.css' // the original inlines Lenis's stylesheet
import Nav from './components/Nav.jsx'
import Hero from './components/Hero.jsx'
import Finding from './components/Finding.jsx'
import Saving from './components/Saving.jsx'
import Faq from './components/Faq.jsx'
import Waitlist from './components/Waitlist.jsx'
import Footer from './components/Footer.jsx'

export default function App() {
  // §0: Lenis, manual rAF loop, skipped under reduced motion.
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    const lenis = new Lenis({ lerp: 0.1, smoothWheel: true, syncTouch: false, anchors: { offset: -100 } })
    let id
    const raf = (t) => {
      lenis.raf(t)
      id = requestAnimationFrame(raf)
    }
    id = requestAnimationFrame(raf)
    return () => {
      cancelAnimationFrame(id)
      lenis.destroy()
    }
  }, [])

  return (
    <>
      <Nav />
      <Hero />
      <main>
        <Finding />
        <Saving />
        <Faq />
        <Waitlist />
      </main>
      <Footer />
    </>
  )
}
