import { useState } from 'react'
import Squircle from './Squircle.jsx'
import { Ask, Plus } from './icons.jsx'

// §6 section#faq

const QA = [
  [
    'Which sources can Shelf pull from?',
    'Bookmarks, LinkedIn saved posts, Instagram collections, X bookmarks and any web page you send it. Your own notes count as a source too, often the most useful one, because that is where the why lives.',
  ],
  [
    'Do I have to tag everything?',
    'No. Tagging is the reason most swipe files die. Shelf reads what you saved and takes the note you wrote at the moment you saved it, and that is enough to find it back later.',
  ],
  [
    'What happens to the archive I already have?',
    'You import it. The point of Shelf is not to start a sixth silo. It is to make the five you already have searchable from one field.',
  ],
  ['Who can see what I save?', 'Only you. A swipe file is competitive material, and a private one is the only kind worth keeping.'],
  [
    'What will it cost?',
    'Not settled yet. Shelf is built for people who save professionally, and the price will reflect that rather than chase the free-app crowd. Waitlist members hear it first.',
  ],
  ['When can I use it?', 'Shelf is in private testing. The waitlist is in order, and we widen it as fast as the import can keep up.'],
]

export default function Faq() {
  // at most one open; clicking the open item closes it
  const [open, setOpen] = useState(null)

  return (
    <section id="faq" className="faq mx-auto max-w-3xl px-6 py-20 sm:py-28">
      <div className="flex items-center justify-center gap-3">
        <Squircle
          as="span"
          className="grid size-11 shrink-0 place-items-center rounded-[13px] bg-accent text-text sm:size-13 sm:rounded-[15px]"
          aria-hidden="true"
        >
          <Ask className="ask size-6 sm:size-7" />
        </Squircle>
        <h2 className="text-balance font-display text-4xl font-semibold sm:text-5xl">Before you ask</h2>
      </div>
      <p className="mx-auto mt-5 max-w-lg text-pretty text-center text-[17px] leading-relaxed text-text-muted">
        What people want to know before they hand over an archive they spent years building.
      </p>

      <ul className="mt-12 space-y-3">
        {QA.map(([q, a], i) => {
          const isOpen = open === i
          return (
            <Squircle as="li" key={i} className={`item overflow-hidden rounded-[1.25rem] bg-surface-raised ${isOpen ? 'is-open' : ''}`}>
              <h3>
                <button
                  type="button"
                  data-faq=""
                  aria-expanded={isOpen}
                  aria-controls={`faq-${i}`}
                  onClick={() => setOpen(isOpen ? null : i)}
                  className="flex w-full cursor-pointer items-center justify-between gap-6 py-5 pl-6 pr-5 text-left font-display text-base font-medium sm:pl-8 sm:text-lg"
                >
                  {q}
                  <Squircle
                    as="span"
                    className="icon grid size-8 shrink-0 place-items-center rounded-[10px] bg-surface text-text-muted transition-colors"
                    aria-hidden="true"
                  >
                    <Plus className="size-4" />
                  </Squircle>
                </button>
              </h3>
              <div id={`faq-${i}`} className="panel">
                <div>
                  <p className="text-pretty px-6 pb-6 text-[15px] leading-relaxed text-text-muted sm:px-8 sm:text-[16px]">{a}</p>
                </div>
              </div>
            </Squircle>
          )
        })}
      </ul>
    </section>
  )
}
