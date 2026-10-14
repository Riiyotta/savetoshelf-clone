import Squircle from './Squircle.jsx'

// §3.1 / §3.4: eyebrow pill. padding 6/14/6/10, radius 10, gap 6,
// 14px/21px, 600, ls -0.01em. `tone` = sunken (hero) or accent.
export default function Eyebrow({ as = 'span', tone = 'accent', icon, children }) {
  const bg = tone === 'sunken' ? 'bg-surface-sunken' : 'bg-accent'
  return (
    <Squircle
      as={as}
      className={`inline-flex items-center gap-1.5 rounded-[10px] ${bg} py-1.5 pr-3.5 pl-2.5 text-[14px] font-semibold tracking-[-0.01em] text-text`}
    >
      {icon}
      {children}
    </Squircle>
  )
}
