import { Link } from 'react-router-dom'
import Layout from '../components/Layout'

// /contact — start a project, or reach us directly.
export default function Contact() {
  return (
    <Layout>
      <section className="mx-auto max-w-page px-5 py-32 md:px-10">
        <p className="mb-4 text-xs font-medium uppercase tracking-[0.14em] text-ink-muted">Contact</p>
        <h1 className="mb-8 max-w-[600px] text-4xl font-light tracking-head text-ink md:text-[52px]">
          Start something.
        </h1>
        <p className="mb-10 max-w-[440px] text-base text-ink-soft">
          Tell us about your brand and we’ll take it from there — or email us directly.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link
            to="/start"
            className="rounded-pill bg-white px-6 py-3 text-sm font-medium text-bg transition-colors duration-150 hover:bg-[#E8E8E8]"
          >
            Start a project
          </Link>
          <a
            href="mailto:hello@knc.studio"
            className="rounded-pill border border-line px-6 py-3 text-sm font-medium text-ink transition-colors duration-150 hover:border-line-hover"
          >
            hello@knc.studio
          </a>
        </div>
      </section>
    </Layout>
  )
}
