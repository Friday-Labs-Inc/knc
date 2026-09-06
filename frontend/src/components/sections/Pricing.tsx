import { Link } from 'react-router-dom'
import { PACKAGES } from '../../data/packages'

// Three tiers, $699 → $4,999 — the same pipeline scaled by depth. Identity is the
// anchor (featured). The id doubles as #pricing and the "what's included" target.
export default function Pricing() {
  return (
    <section id="pricing" className="mx-auto max-w-page border-t border-line px-5 py-24 md:px-10">
      <p className="mb-4 text-xs font-medium uppercase tracking-[0.14em] text-ink-muted">
        What’s included
      </p>
      <h2 className="mb-4 max-w-[520px] text-3xl font-light tracking-head text-ink md:text-[44px]">
        Three ways to start. One machine.
      </h2>
      <p className="mb-14 max-w-[480px] text-base text-ink-muted">
        AI generates, experts direct. One-time price, one revision round, you own everything.
      </p>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {PACKAGES.map((pkg) => (
          <div
            key={pkg.name}
            className={`flex flex-col rounded-card border bg-surface-1 p-8 ${
              pkg.featured ? 'border-line-hover' : 'border-line'
            }`}
          >
            <div className="mb-1 flex items-center justify-between">
              <h3 className="text-base font-medium text-ink">{pkg.name}</h3>
              {pkg.featured && (
                <span className="rounded-tag border border-line bg-surface-2 px-2 py-0.5 text-[11px] font-medium uppercase tracking-[0.06em] text-ink-muted">
                  Most chosen
                </span>
              )}
            </div>

            <p className="mb-5 text-[52px] font-light leading-none tracking-hero text-ink">{pkg.price}</p>
            <p className="text-sm text-ink-soft">{pkg.tagline}</p>
            <p className="mb-6 mt-1 text-[13px] text-ink-muted">{pkg.cadence}</p>

            <ul className="mb-8 space-y-2.5 border-t border-line pt-6">
              {pkg.includes.map((item) => (
                <li key={item} className="text-[13px] leading-relaxed text-ink-soft">
                  {item}
                </li>
              ))}
            </ul>

            <div className="mt-auto">
              <p className="mb-4 text-[13px] text-ink-faint">{pkg.for}</p>
              <Link
                to="/start"
                className={`block rounded-pill py-2.5 text-center text-sm font-medium transition-colors duration-150 ${
                  pkg.featured
                    ? 'bg-white text-bg hover:bg-[#E8E8E8]'
                    : 'border border-line text-ink hover:border-line-hover'
                }`}
              >
                Start a project
              </Link>
            </div>
          </div>
        ))}
      </div>

      <p className="mt-6 max-w-[640px] text-[13px] text-ink-muted">
        Add-ons at a transparent per-item rate — extra pages, custom illustration, motion, an
        additional direction, rush delivery. Ask in the brief.
      </p>
    </section>
  )
}
