import { useEffect, useRef, useState } from 'react'
import Squircle from './Squircle.jsx'
import { Tick } from './icons.jsx'

// §3.1 waitlist form + done card + note; §7 closing variant.
// The original POSTs {email} to /api/waitlist. Per the brief this clone must
// NOT hit the real API, so submission goes through a local stub that resolves
// like an ok Response.
const STUB_LATENCY_MS = 600 // not in spec: stand-in for network time
async function submitWaitlist(email) {
  await new Promise((r) => setTimeout(r, STUB_LATENCY_MS))
  console.info('[waitlist stub] would POST /api/waitlist', { email })
  return { ok: true }
}

const EMAIL_RE = /^[^\s@]+@[^\s@.]+(\.[^\s@.]+)+$/
const LABEL = 'Join waitlist'

export default function WaitlistForm({ id, variant }) {
  const hero = variant === 'hero'
  const inputRef = useRef(null)
  const [valid, setValid] = useState(false)
  const [busy, setBusy] = useState(false)
  const [note, setNote] = useState(null)
  const [done, setDone] = useState(false)
  const [doneIn, setDoneIn] = useState(false)

  const check = () => {
    const n = inputRef.current
    if (!n) return
    setValid(n.checkValidity() && EMAIL_RE.test(n.value.trim()))
  }
  useEffect(check, [])

  const onSubmit = async (e) => {
    e.preventDefault()
    const n = inputRef.current
    if (!n) return
    const email = n.value.trim()
    if (!EMAIL_RE.test(email)) return
    setBusy(true)
    setNote(null)
    try {
      const res = await submitWaitlist(email)
      if (res.ok) {
        setDone(true)
        requestAnimationFrame(() => requestAnimationFrame(() => setDoneIn(true)))
        return
      }
      setNote('That did not go through. Try again in a moment.')
    } catch {
      setNote('That did not go through. Check your connection and try again.')
    } finally {
      setBusy(false)
      check()
    }
  }

  const center = hero ? 'mx-auto' : ''
  const formChrome = hero
    ? 'border border-border focus-within:border-text-muted'
    : 'focus-within:ring-1 focus-within:ring-text/60'

  return (
    <>
      <form
        id={id}
        data-waitlist=""
        hidden={done}
        onSubmit={onSubmit}
        className={`flex w-full max-w-[460px] items-center gap-2 rounded-[1rem] bg-surface-raised p-2 transition-colors ${formChrome} ${center}`}
      >
        <label className="sr-only" htmlFor={`${id}-email`}>
          Your email address
        </label>
        <input
          ref={inputRef}
          id={`${id}-email`}
          name="email"
          type="email"
          required
          autoComplete="email"
          placeholder="Enter your email"
          onInput={check}
          className="min-w-0 flex-1 bg-transparent px-4 py-3 text-base placeholder:text-text-faint focus:[outline-style:none]"
        />
        <Squircle
          as="button"
          type="submit"
          disabled={busy || !valid}
          className="shrink-0 whitespace-nowrap rounded-[0.7rem] bg-text px-6 py-3 text-base font-medium text-surface-raised transition-colors hover:brightness-125 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-text disabled:bg-surface disabled:text-text-faint disabled:hover:brightness-100"
        >
          {busy ? 'One moment' : LABEL}
        </Squircle>
      </form>

      <div
        id={`${id}-done`}
        data-waitlist-done=""
        hidden={!done}
        role="status"
        className={`done w-full max-w-[460px] items-center gap-3.5 rounded-[1rem] bg-surface-raised p-3 ${center} ${doneIn ? 'is-in' : ''}`}
      >
        <Squircle as="span" className="grid size-11 shrink-0 place-items-center rounded-[13px] bg-accent text-text">
          <Tick className="size-6" />
        </Squircle>
        <span className="min-w-0">
          <span className="block text-[15px] font-medium leading-snug">You are on the list</span>
          <span className="mt-0.5 block text-[14px] leading-snug text-text-muted">Check your inbox, a confirmation is on its way.</span>
        </span>
      </div>

      <p id={`${id}-note`} data-waitlist-note="" role="status" className={`mt-3 text-sm text-text/70 ${note === null ? 'hidden' : ''}`}>
        {note}
      </p>
    </>
  )
}
