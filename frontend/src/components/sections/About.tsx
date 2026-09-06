// AI builds it, experts direct it — the studio in two lines, plus the proof stats.
const STATS = [
  { n: '10', label: 'Days from brief to delivery' },
  { n: '2', label: 'Expert gates — the only times we need you' },
  { n: '1', label: 'Revision round, included' },
]

export default function About() {
  return (
    <section id="about" className="mx-auto max-w-page border-t border-line px-5 py-24 md:px-10">
      <p className="mb-4 text-xs font-medium uppercase tracking-[0.14em] text-ink-muted">About</p>
      <h2 className="mb-12 max-w-[480px] text-3xl font-light leading-[1.1] tracking-head text-ink md:text-[44px]">
        AI builds it. Experts direct it.
      </h2>

      <div className="grid grid-cols-1 gap-16 md:grid-cols-2">
        <p className="max-w-[420px] text-base leading-relaxed text-ink-soft">
          KNC is a fast-turnaround branding studio built for early-stage teams. We pair
          AI-generated creative directions with expert oversight to deliver a complete brand in ten
          days. You share a brief; we handle the rest, and you make the calls at two gates.
        </p>
        <div>
          {STATS.map((s, i) => (
            <div
              key={s.label}
              className={`flex items-baseline gap-5 py-6 ${
                i < STATS.length - 1 ? 'border-b border-line' : ''
              }`}
            >
              <span className="text-4xl font-light text-ink">{s.n}</span>
              <span className="text-[13px] text-ink-muted">{s.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
