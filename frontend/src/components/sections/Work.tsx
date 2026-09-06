import { Link } from 'react-router-dom'
import { useFrappeGetCall } from 'frappe-react-sdk'

// Work grid — loaded from the backend (KNC Portfolio Project via api/v1.get_portfolio).
// `limit` trims it for the home teaser; each card links to its case study.
type Project = { title: string; tag: string; description: string; image?: string | null }

export const slugify = (t: string) =>
  t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')

export default function Work({ limit }: { limit?: number }) {
  const { data, isLoading } = useFrappeGetCall<{ message: Project[] }>('knc.api.v1.get_portfolio')
  const all: Project[] = Array.isArray(data) ? data : (data?.message ?? [])
  const projects = limit ? all.slice(0, limit) : all

  return (
    <section id="work" className="mx-auto max-w-page border-t border-line px-5 py-24 md:px-10">
      <div className="mb-12 flex items-end justify-between">
        <div>
          <p className="mb-4 text-xs font-medium uppercase tracking-[0.14em] text-ink-muted">Selected work</p>
          <h2 className="max-w-[520px] text-3xl font-light tracking-head text-ink md:text-[44px]">
            Brands shaped, end to end.
          </h2>
        </div>
        {limit && all.length > limit && (
          <Link to="/work" className="hidden shrink-0 text-sm text-ink-muted transition-colors duration-150 hover:text-ink md:block">
            View all work →
          </Link>
        )}
      </div>

      {isLoading && <p className="text-sm text-ink-muted">Loading work…</p>}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {projects.map((p) => (
          <Link
            key={p.title}
            to={`/work/${slugify(p.title)}`}
            className="group overflow-hidden rounded-card border border-line bg-surface-1 transition-colors duration-200 hover:border-line-hover"
          >
            <div className="aspect-[16/10] border-b border-line bg-[#1A1A1A]">
              {p.image ? (
                <img src={p.image} alt={p.title} className="h-full w-full object-cover" />
              ) : (
                <div className="flex h-full items-center justify-center">
                  <span className="text-[11px] font-medium uppercase tracking-[0.1em] text-[#303030]">{p.title}</span>
                </div>
              )}
            </div>
            <div className="p-6">
              <p className="mb-2.5 text-[11px] font-medium uppercase tracking-[0.1em] text-ink-muted">{p.tag}</p>
              <h3 className="mb-2.5 text-xl font-light tracking-tightish text-ink">{p.title}</h3>
              <p className="text-sm leading-relaxed text-ink-muted">{p.description}</p>
            </div>
          </Link>
        ))}
      </div>
    </section>
  )
}
