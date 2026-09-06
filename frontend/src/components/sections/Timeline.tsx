// Ten days, every step visible. Mirrors the production pipeline (the install.py
// project template). The two client gates (◆) are the only points we need you.
const PHASES = [
  { day: 'Day 0–1', title: 'Brief & intake', tasks: ['You share the brief', 'We review and confirm', 'Project starts within 24h'] },
  { day: 'Day 1–4', title: 'Strategy & naming', tasks: ['Positioning and tone', 'Naming territory', 'The brief becomes a direction'] },
  { day: 'Day 4–6', title: 'Three directions', tasks: ['AI generates, experts refine', 'Three distinct, coherent systems'] },
  { day: 'Day 5', title: 'Gate 1 — you choose', tasks: ['Pick a direction', 'Leave notes'], gate: true },
  { day: 'Day 6–9', title: 'Build the system', tasks: ['Logo, colour, type, core system', 'Guidelines and source files'] },
  { day: 'Day 9', title: 'Gate 2 — final review', tasks: ['Approve, or one round of notes'], gate: true },
  { day: 'Day 10', title: 'Delivery', tasks: ['Everything handed over', 'Ready to launch'] },
]

export default function Timeline() {
  return (
    <section id="timeline" className="mx-auto max-w-page border-t border-line px-5 py-24 md:px-10">
      <p className="mb-4 text-xs font-medium uppercase tracking-[0.14em] text-ink-muted">How it works</p>
      <h2 className="mb-12 max-w-[420px] text-3xl font-light tracking-head text-ink md:text-[44px]">
        Ten days. Every step visible.
      </h2>

      <div className="grid grid-cols-1 gap-px overflow-hidden rounded-card border border-line bg-line sm:grid-cols-2 lg:grid-cols-4">
        {PHASES.map((p) => (
          <div key={p.title} className="bg-bg p-7">
            <p className="mb-3 text-[11px] font-medium uppercase tracking-[0.1em] text-ink-faint">{p.day}</p>
            <h3 className="mb-4 text-[15px] font-medium text-ink">
              {p.gate && <span className="text-ink-soft">◆ </span>}
              {p.title}
            </h3>
            <ul className="space-y-1.5">
              {p.tasks.map((t) => (
                <li key={t} className="text-[13px] leading-relaxed text-ink-muted">
                  <span className="text-[#303030]">— </span>
                  {t}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  )
}
