import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import HeroInput from '../components/HeroInput'
import Work from '../components/sections/Work'

// Home — the front door. Hero, a short teaser of the work, and a closing CTA.
// The depth (full work, services, about) lives on the dedicated pages.
const CHIPS = [
  { label: 'See the work', to: '/work' },
  { label: 'How it works', to: '/services' },
  { label: 'Read the journal', to: '/journal' },
]

export default function Home() {
  return (
    <Layout>
      <section className="flex min-h-[calc(100vh-60px)] flex-col items-center justify-center px-5 pb-20 pt-16 text-center md:px-10">
        <p className="mb-8 text-lg font-medium tracking-[-0.01em] text-ink">KNC</p>
        <h1 className="mx-auto mb-10 max-w-[600px] text-4xl font-light leading-[1.08] tracking-hero text-ink md:text-[52px]">
          Your brand, built in ten days.
        </h1>
        <p className="mb-10 text-base text-ink-muted">AI-guided. Expert-directed.</p>
        <HeroInput />
        <div className="mt-5 flex flex-wrap justify-center gap-2">
          {CHIPS.map((c) => (
            <Link
              key={c.to}
              to={c.to}
              className="rounded-pill border border-line bg-surface-1 px-3.5 py-2 text-[13px] text-ink-soft transition-colors duration-150 hover:border-line-hover hover:text-ink"
            >
              {c.label}
            </Link>
          ))}
        </div>
      </section>

      <Work limit={3} />

      <section className="border-t border-line px-5 py-28 text-center md:px-10">
        <h2 className="mx-auto mb-8 max-w-[480px] text-3xl font-light tracking-head text-ink md:text-[40px]">
          Ready when you are.
        </h2>
        <Link
          to="/start"
          className="inline-block rounded-pill bg-white px-6 py-3 text-sm font-medium text-bg transition-colors duration-150 hover:bg-[#E8E8E8]"
        >
          Start a project
        </Link>
      </section>
    </Layout>
  )
}
