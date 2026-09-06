import { Link, NavLink } from 'react-router-dom'

// Route-based nav for the multipage site. Wordmark left, page links centre,
// the single white CTA right. The active page reads in full white.
const LINKS = [
  { label: 'Work', to: '/work' },
  { label: 'Services', to: '/services' },
  { label: 'About', to: '/about' },
  { label: 'Journal', to: '/journal' },
]

export default function Nav() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 h-[60px] border-b border-line bg-bg/85 backdrop-blur-xl backdrop-saturate-150">
      <nav className="mx-auto flex h-full max-w-page items-center justify-between px-5 md:px-10">
        <Link to="/" className="text-base font-medium tracking-[-0.01em] text-ink">
          KNC
        </Link>

        <div className="hidden items-center gap-9 md:flex">
          {LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `text-sm transition-colors duration-150 ${isActive ? 'text-ink' : 'text-ink-muted hover:text-ink'}`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </div>

        <div className="flex items-center gap-5">
          <Link to="/login" className="hidden text-sm text-ink-muted transition-colors duration-150 hover:text-ink sm:block">
            Log in
          </Link>
          <Link
            to="/start"
            className="rounded-pill bg-white px-5 py-2.5 text-sm font-medium text-bg transition-colors duration-150 hover:bg-[#E8E8E8]"
          >
            Start a project
          </Link>
        </div>
      </nav>
    </header>
  )
}
