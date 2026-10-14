import Squircle from './Squircle.jsx'
import Eyebrow from './Eyebrow.jsx'
import { InboxTray } from './icons.jsx'

// §5 section#saving

const FEED = [
  ['bg-swatch-peach', 'w-full', 'w-3/5'],
  ['bg-swatch-mist', 'w-4/5', 'w-2/5'],
  ['bg-swatch-sand', 'w-full', 'w-1/2'],
]

const visual = 'h-24 w-full shrink-0 rounded-2xl bg-surface-raised sm:w-44'

function FeedVisual() {
  return (
    <div className={`feed overflow-hidden ${visual}`} aria-hidden="true">
      <span className="feed-strip block space-y-2 px-3 py-3">
        {[...FEED, ...FEED].map(([sq, a, b], i) => (
          <span key={i} className="flex items-center gap-2">
            <span className={`size-7 shrink-0 rounded-md ${sq}`} />
            <span className="min-w-0 flex-1 space-y-1.5">
              <span className={`block h-1.5 ${a} rounded-full bg-border-strong/60`} />
              <span className={`block h-1.5 ${b} rounded-full bg-border-strong/40`} />
            </span>
          </span>
        ))}
      </span>
    </div>
  )
}

function TapVisual() {
  return (
    <div className={`grid place-items-center ${visual}`} aria-hidden="true">
      <span className="relative grid place-items-center">
        <span className="tap absolute size-14 rounded-full bg-accent/45" />
        <Squircle as="span" className="relative grid size-12 place-items-center rounded-[11px] bg-text">
          <img src="/assets/logo.svg" alt="" width="24" height="24" className="size-6 brightness-0 invert" />
        </Squircle>
      </span>
    </div>
  )
}

function WhyVisual() {
  return (
    <div className={`flex flex-col justify-center px-3.5 ${visual}`} aria-hidden="true">
      <span className="block text-[10px] uppercase tracking-wider text-text-faint">Why this</span>
      <span className="mt-1.5 block border-l-2 border-accent pl-2.5 text-[13px] leading-snug">
        The empty state does the teaching
        <span className="caret" />
      </span>
    </div>
  )
}

const STEPS = [
  [1, 'You find a gem', 'Halfway down a feed, in a message, or an idea that turns up on the walk home.', <FeedVisual />],
  [2, 'One tap to save', 'The browser button, or Shelf in the share sheet.', <TapVisual />],
  [3, 'One line about why', 'Written while it is still in your head. That line is what finds it back.', <WhyVisual />],
]

export default function Saving() {
  return (
    <section id="saving" className="px-2 sm:px-3">
      <Squircle className="mx-auto max-w-[1440px] rounded-[2rem] bg-surface-raised px-6 py-20 sm:px-10 sm:py-24">
        <div className="mx-auto grid max-w-6xl items-center gap-14 lg:grid-cols-2 lg:gap-20">
          <div>
            <p className="flex">
              <Eyebrow tone="accent" icon={<InboxTray className="size-[18px] shrink-0" />}>
                Getting things in
              </Eyebrow>
            </p>
            <h2 className="mt-6 text-balance font-display text-4xl font-semibold leading-[1.08] sm:text-[3.25rem]">Save it where you found it.</h2>
            <p className="mt-6 max-w-lg text-pretty text-[17px] leading-relaxed text-text-muted">
              A button in your browser for the web, the share sheet on your phone. Three seconds, and you are back to what you were doing.
            </p>
            <p className="mt-4 max-w-lg text-pretty text-[17px] leading-relaxed text-text-muted">
              What you already have comes along too. Your bookmarks and saved posts import in one go, so you are not starting from an empty shelf.
            </p>
          </div>

          <ol className="space-y-3">
            {STEPS.map(([n, title, desc, vis]) => (
              <Squircle
                as="li"
                key={n}
                className="flex flex-col items-start gap-4 rounded-[1.5rem] bg-surface p-4 sm:flex-row sm:items-center sm:gap-6 sm:p-5"
              >
                {vis}
                <div className="min-w-0">
                  <p className="flex items-center gap-2.5">
                    <Squircle
                      as="span"
                      className="grid size-[30px] shrink-0 place-items-center rounded-[10px] bg-text text-[14px] font-semibold tabular-nums text-surface"
                      aria-hidden="true"
                    >
                      {n}
                    </Squircle>
                    <span className="text-[20px] font-medium leading-snug">{title}</span>
                  </p>
                  <p className="mt-2.5 text-pretty text-[14px] leading-relaxed text-text-muted">{desc}</p>
                </div>
              </Squircle>
            ))}
          </ol>
        </div>
      </Squircle>
    </section>
  )
}
