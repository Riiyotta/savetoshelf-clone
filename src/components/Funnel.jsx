import Eyebrow from './Eyebrow.jsx'
import {
  Ask,
  TagInstagram,
  TagLinkedIn,
  TagGlobe,
  TagMic,
  TagDocument,
  TagScreenshot,
  TagX,
  TagYouTube,
  TagNewsletter,
  TagFigma,
} from './icons.jsx'

// §3.4 Funnel: sticky "Why Shelf" title + the 12 physics tags.
// Rendered inside header[data-bookmark]; the clip-path/physics JS lives in
// src/lib/bookmark.js and is started by Hero.jsx.

const ICON = 'size-[1.15em] shrink-0'

// DOM order per spec
const TAGS = [
  ['Instagram', <TagInstagram className={`${ICON} text-brand-instagram`} />],
  ['LinkedIn', <TagLinkedIn className={`${ICON} text-source-linkedin`} />],
  ['Web page', <TagGlobe className={`${ICON} text-swatch-web`} />],
  ['Voice note', <TagMic className={`${ICON} text-text-muted`} />],
  ['Note', <TagDocument className={`${ICON} text-text-muted`} />],
  ['Screenshot', <TagScreenshot className={`${ICON} text-text-muted`} />],
  ['PDF', <TagDocument className={`${ICON} text-text-muted`} />],
  ['X post', <TagX className={`${ICON} text-brand-x`} />],
  ['YouTube', <TagYouTube className={`${ICON} text-brand-youtube`} />],
  ['Newsletter', <TagNewsletter className={`${ICON} text-text-muted`} />],
  ['Article', <TagDocument className={`${ICON} text-swatch-web`} />],
  ['Figma file', <TagFigma className={`${ICON} text-brand-figma`} />],
]

export default function Funnel() {
  return (
    <>
      <div data-funnel="" className="funnel">
        <div className="funnel-stick">
          <div data-funnel-trigger="" className="sticky top-[40%] -translate-y-1/2 px-6 text-center">
            <p className="reveal mx-auto w-fit">
              <Eyebrow tone="accent" icon={<Ask className="ask size-[18px] shrink-0" />}>
                Why Shelf
              </Eyebrow>
            </p>
            <p className="reveal mx-auto mt-5 max-w-3xl text-balance font-display text-4xl font-semibold sm:text-5xl">
              <span className="inline-block">You save all over the place</span>
            </p>
            <p className="reveal mx-auto mt-5 max-w-xl text-pretty text-[17px] leading-relaxed text-text-muted">
              <span className="inline-block">
                Every app has its own save button, and none of them talks to the next. What you keep ends up scattered over a dozen of them.
              </span>
            </p>
          </div>
        </div>
      </div>

      <div data-tags="" className="tags pointer-events-none absolute inset-0" aria-hidden="true">
        {TAGS.map(([label, icon]) => (
          <span
            key={label}
            data-tag=""
            className="tag flex items-center gap-1.5 whitespace-nowrap rounded-full border border-border bg-surface px-3 py-2 text-[0.8rem] text-text-muted sm:gap-2.5 sm:px-6 sm:py-3.5 sm:text-[1.375rem]"
          >
            {icon} {label}
          </span>
        ))}
      </div>
    </>
  )
}
