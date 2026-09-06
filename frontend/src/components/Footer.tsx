import { Link } from 'react-router-dom'

const PAGES = [
  { label: 'Work', to: '/work' },
  { label: 'Services', to: '/services' },
  { label: 'About', to: '/about' },
  { label: 'Journal', to: '/journal' },
  { label: 'Contact', to: '/contact' },
]

// Minimal dark footer. The only quiet, secondary band on the site.
export default function Footer() {
  return (
    <footer className="border-t border-line px-5 py-12 md:px-10">
      <div className="mx-auto flex max-w-page flex-col gap-8 md:flex-row md:items-end md:justify-between">
        <div>
          <span className="text-sm font-medium text-ink">KNC</span>
          <p className="mt-2 max-w-[260px] text-[13px] text-ink-faint">Your brand, built in ten days. AI-guided, expert-directed.</p>
        </div>
        <div className="flex flex-wrap gap-x-6 gap-y-2 text-[13px] text-ink-muted">
          {PAGES.map((p) => (
            <Link key={p.to} to={p.to} className="transition-colors duration-150 hover:text-ink">
              {p.label}
            </Link>
          ))}
          <a href="mailto:hello@knc.studio" className="transition-colors duration-150 hover:text-ink">
            hello@knc.studio
          </a>
        </div>
      </div>
      <div className="mx-auto mt-10 max-w-page border-t border-[#1A1A1A] pt-6">
        <p className="text-xs text-ink-faint">© 2026 KNC. All rights reserved.</p>
      </div>
    </footer>
  )
}
