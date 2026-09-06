import { Link } from 'react-router-dom'
import { useFrappeGetCall } from 'frappe-react-sdk'
import Layout from '../components/Layout'

// /journal — the post list, loaded from the backend (Article via
// api/v1.get_articles). Desk-managed; studio writes real posts there.
type Article = {
  title: string
  slug: string
  excerpt?: string
  cover_image?: string | null
  author?: string
  category?: string
  published_on?: string
}

export default function Journal() {
  const { data, isLoading } = useFrappeGetCall<{ message: Article[] }>('knc.api.v1.get_articles')
  const articles: Article[] = Array.isArray(data) ? data : (data?.message ?? [])

  return (
    <Layout>
      <section className="mx-auto max-w-page px-5 py-24 md:px-10">
        <p className="mb-4 text-xs font-medium uppercase tracking-[0.14em] text-ink-muted">Journal</p>
        <h1 className="mb-14 max-w-[600px] text-3xl font-light tracking-head text-ink md:text-[44px]">
          Notes on brand, built fast.
        </h1>

        {isLoading && <p className="text-sm text-ink-muted">Loading…</p>}

        <div className="border-t border-line">
          {articles.map((a) => (
            <Link
              key={a.slug}
              to={`/journal/${a.slug}`}
              className="group flex flex-col gap-2 border-b border-line py-8 md:flex-row md:items-baseline md:justify-between"
            >
              <div className="max-w-[640px]">
                <h2 className="mb-2 text-2xl font-light tracking-tightish text-ink">{a.title}</h2>
                {a.excerpt && <p className="text-sm leading-relaxed text-ink-muted">{a.excerpt}</p>}
              </div>
              <div className="shrink-0 text-[13px] text-ink-faint md:pl-8 md:text-right">
                {[a.category, a.published_on].filter(Boolean).join(' · ')}
              </div>
            </Link>
          ))}
        </div>

        {!isLoading && articles.length === 0 && (
          <p className="border-t border-line pt-8 text-sm text-ink-muted">No posts yet.</p>
        )}
      </section>
    </Layout>
  )
}
