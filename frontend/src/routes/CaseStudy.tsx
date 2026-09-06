import { useParams, Link } from 'react-router-dom'
import { useFrappeGetCall } from 'frappe-react-sdk'
import Layout from '../components/Layout'

// /work/<slug> — the EXPRESSIVE surface (the studio's range). Loads the full
// case study (api/v1.get_case_study) and frames it with a dramatic header, a
// full-bleed hero, and the challenge/approach/outcome story. Fields are filled
// per-project in the desk; until then it shows the title + description.
type CaseStudyData = {
  title: string
  tag?: string
  description?: string
  image?: string | null
  client?: string
  year?: string
  hero_image?: string | null
  challenge?: string
  approach?: string
  outcome?: string
  body?: string
}

export default function CaseStudy() {
  const { slug } = useParams()
  const { data, isLoading, error } = useFrappeGetCall<{ message: CaseStudyData }>(
    'knc.api.v1.get_case_study',
    { slug },
  )
  const cs = (data?.message ?? (data as unknown)) as CaseStudyData | undefined

  if (isLoading) {
    return (
      <Layout>
        <div className="px-5 py-40 text-center text-sm text-ink-muted">Loading…</div>
      </Layout>
    )
  }

  if (error || !cs?.title) {
    return (
      <Layout>
        <div className="mx-auto max-w-narrow px-5 py-40 md:px-8">
          <Link to="/work" className="text-sm text-ink-muted transition-colors duration-150 hover:text-ink">
            ← Work
          </Link>
          <p className="mt-10 text-ink-muted">Case study not found.</p>
        </div>
      </Layout>
    )
  }

  const hero = cs.hero_image || cs.image
  const meta = [
    cs.client && { label: 'Client', value: cs.client },
    cs.year && { label: 'Year', value: cs.year },
    cs.tag && { label: 'Scope', value: cs.tag },
  ].filter(Boolean) as { label: string; value: string }[]
  const story = [
    { label: 'Challenge', body: cs.challenge },
    { label: 'Approach', body: cs.approach },
    { label: 'Outcome', body: cs.outcome },
  ].filter((s) => s.body)

  return (
    <Layout>
      <header className="px-5 pt-16 md:px-10">
        <div className="mx-auto max-w-page">
          <Link to="/work" className="text-sm text-ink-muted transition-colors duration-150 hover:text-ink">
            ← Work
          </Link>
          <div className="mt-12 flex flex-wrap items-end justify-between gap-8">
            <h1 className="max-w-[16ch] text-5xl font-light leading-[0.95] tracking-hero text-ink md:text-7xl">
              {cs.title}
            </h1>
            {meta.length > 0 && (
              <div className="flex gap-10">
                {meta.map((m) => (
                  <div key={m.label} className="text-[13px]">
                    <p className="mb-1 uppercase tracking-[0.12em] text-ink-faint">{m.label}</p>
                    <p className="text-ink-soft">{m.value}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
          {cs.description && (
            <p className="mt-10 max-w-[680px] text-xl font-light leading-relaxed text-ink-soft md:text-2xl">
              {cs.description}
            </p>
          )}
        </div>
      </header>

      <div className="mt-16 px-5 md:px-10">
        <div className="mx-auto aspect-[16/9] max-w-[1400px] overflow-hidden rounded-card border border-line bg-[#1A1A1A]">
          {hero && <img src={hero} alt={cs.title} className="h-full w-full object-cover" />}
        </div>
      </div>

      {story.length > 0 && (
        <div className="mx-auto max-w-narrow px-5 py-28 md:px-8">
          <div className="space-y-16">
            {story.map((s) => (
              <section key={s.label}>
                <p className="mb-4 text-xs font-medium uppercase tracking-[0.14em] text-ink-muted">{s.label}</p>
                <p className="whitespace-pre-line text-lg leading-relaxed text-ink-soft">{s.body}</p>
              </section>
            ))}
          </div>
        </div>
      )}

      {cs.body && (
        <div className="mx-auto max-w-narrow px-5 pb-28 md:px-8">
          <div className="whitespace-pre-line text-base leading-relaxed text-ink-soft">{cs.body}</div>
        </div>
      )}

      <section className="border-t border-line px-5 py-24 text-center md:px-10">
        <p className="mb-6 text-2xl font-light tracking-head text-ink md:text-3xl">Want work like this?</p>
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
