import { useEffect, useRef } from 'react'
import Palette from './Palette.jsx'

// §3.2 Demo app mockup: fixed 1440×820 canvas scaled to the container width.

const LABEL =
  'The Shelf app. A sidebar lists collections, sources and tags with the number saved in each. The main panel offers a box to paste a link into and shows recent saves, each with the note written at the time. A search field, opened over the top, takes a question in plain language, shows the filters it read out of that question, and lists the saves that match.'

const row = 'flex items-center justify-between rounded-lg px-3 text-[15px]'

const collections = [
  ['Website redesign', 23],
  ['Brand refresh', 11],
  ['New pitch', 38],
]
const sources = [
  ['LinkedIn', 'bg-source-linkedin', 41],
  ['Instagram', 'bg-source-instagram', 27],
  ['Web', 'bg-swatch-web', 60],
]
const cards = [
  ['Web', 'Today', 'How Linear writes its changelog', 'The tone we want for release notes', 'bg-swatch-ink'],
  ['Other', 'Mon', 'Neue Haas Grotesk specimen', 'The weights actually worth licensing', 'bg-surface-sunken'],
  ['LinkedIn', 'Tue', 'Why retainers beat project fees', 'Saved for the anchoring argument', 'bg-source-linkedin'],
  ['Web', 'Wed', 'Stripe docs, the sidebar pattern', 'Three levels deep without getting lost', 'bg-swatch-steel'],
]

export default function HeroMockup() {
  const demoRef = useRef(null)
  const scaleRef = useRef(null)

  useEffect(() => {
    const e = demoRef.current
    const t = scaleRef.current
    if (!e || !t) return
    const r = () => {
      t.style.transform = `scale(${e.clientWidth / 1440})`
    }
    r()
    const ro = new ResizeObserver(r)
    ro.observe(e)
    return () => ro.disconnect()
  }, [])

  return (
    <div className="px-4 pb-4 sm:px-8 sm:pb-8">
      <div
        ref={demoRef}
        data-demo=""
        className="relative aspect-[1440/820] overflow-hidden rounded-xl border border-border bg-surface-raised"
        role="img"
        aria-label={LABEL}
      >
        <div ref={scaleRef} data-demo-scale="" className="h-[820px] w-[1440px] origin-top-left">
          {/* Top bar */}
          <div className="flex h-[64px] items-center justify-between border-b border-border px-7">
            <img src="/assets/logo.svg" alt="" width="30" height="30" className="size-[30px]" />
            <div className="flex items-center gap-2.5">
              <span className="grid size-8 place-items-center rounded-lg bg-surface-sunken text-[13px] font-medium text-text-muted" aria-hidden="true">
                S
              </span>
              <span className="text-[13px] text-text-faint" aria-hidden="true">
                ▾
              </span>
            </div>
          </div>

          <div className="flex h-[756px]">
            {/* Sidebar */}
            <aside className="w-[264px] shrink-0 border-r border-border px-4 py-6">
              <ul className="space-y-1">
                <li className={`${row} py-2.5 text-text-muted`}>
                  <span className="flex items-center gap-3">
                    <span className="size-[18px] rounded bg-border-strong/50" /> Today
                  </span>
                </li>
                <li className={`${row} bg-surface-sunken py-2.5 font-medium`}>
                  <span className="flex items-center gap-3">
                    <span className="size-[18px] rounded bg-border-strong/50" /> My shelf
                  </span>
                  <span className="text-[13px] text-text-faint">128</span>
                </li>
                <li className={`${row} py-2.5 text-text-muted`}>
                  <span className="flex items-center gap-3">
                    <span className="size-[18px] rounded bg-border-strong/50" /> Favourites
                  </span>
                  <span className="text-[13px] text-text-faint">14</span>
                </li>
              </ul>

              <div className="mt-8">
                <p className="px-3 text-[12px] uppercase tracking-wider text-text-faint">Collections</p>
                <ul className="mt-2.5 space-y-1">
                  {collections.map(([name, n]) => (
                    <li key={name} className={`${row} py-2 text-text-muted`}>
                      <span className="flex min-w-0 items-center gap-3">
                        <span className="truncate">{name}</span>
                      </span>
                      <span className="shrink-0 text-[13px] text-text-faint">{n}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-8">
                <p className="px-3 text-[12px] uppercase tracking-wider text-text-faint">Source</p>
                <ul className="mt-2.5 space-y-1">
                  {sources.map(([name, dot, n]) => (
                    <li key={name} className={`${row} py-2 text-text-muted`}>
                      <span className="flex min-w-0 items-center gap-3">
                        <span className={`size-2 shrink-0 rounded-full ${dot}`} />
                        <span className="truncate">{name}</span>
                      </span>
                      <span className="shrink-0 text-[13px] text-text-faint">{n}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </aside>

            {/* Main */}
            <div className="min-w-0 flex-1 px-10 py-9">
              <p className="font-display text-[30px] font-semibold leading-tight">Good morning</p>
              <p className="mt-2 text-[16px] text-text-muted">Nine new saves this week, and four things came back from May.</p>
              <p className="mt-8 flex w-[560px] items-center gap-3.5 rounded-xl border border-dashed border-border-strong px-5 py-4 text-[16px] text-text-faint">
                <span aria-hidden="true">+</span>
                <span className="flex-1">Paste a link, or drop it here</span>
                <kbd className="text-[13px]">⌘V</kbd>
              </p>

              <div className="mt-10">
                <p className="font-display text-[20px] font-semibold">Your last saves</p>
                <p className="mt-1 text-[14px] text-text-faint">The most recent, straight from the extension</p>
                <ul className="mt-5 flex gap-4">
                  {cards.map(([src, day, title, note, thumb]) => (
                    <li key={title} className="w-[318px] shrink-0 rounded-2xl bg-surface p-4">
                      <p className="flex items-center justify-between text-[12px] uppercase tracking-wider text-text-faint">
                        {src} <span className="normal-case tracking-normal">{day}</span>
                      </p>
                      <p className="mt-3 text-[16px] font-medium leading-snug">{title}</p>
                      <p className="mt-3 border-l-2 border-accent pl-3 text-[14px] leading-snug text-text-muted">{note}</p>
                      <p className={`mt-4 h-[132px] rounded-lg ${thumb}`} />
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Scrim: never activated by any script (§3.2), kept inert. */}
          <div data-demo-scrim="" className="pointer-events-none absolute inset-0 bg-surface-raised/45 opacity-0 transition-opacity duration-300" />

          <div data-demo-palette="" className="pointer-events-none absolute left-1/2 top-[60px] w-[845px] -translate-x-1/2">
            <Palette
              variant="hero"
              question="typography I saved about two weeks ago for the redesign"
              chips={['tag: typography', 'saved 8 to 20 Aug', 'Website redesign']}
              hits={[
                { title: 'Neue Haas Grotesk specimen', sub: 'The weights actually worth licensing', date: '28 Jul', thumb: 'bg-swatch-linen' },
                { title: 'Blocky display type on a phone', sub: 'Still readable at the smallest size', date: '4 Aug', thumb: 'bg-swatch-lilac' },
                { title: 'Type scale for the redesign', sub: 'Two sizes fewer than we have now, cleaner', date: '11 Aug', thumb: 'bg-swatch-steel' },
              ]}
              total={12}
            />
          </div>
        </div>

      </div>
    </div>
  )
}
