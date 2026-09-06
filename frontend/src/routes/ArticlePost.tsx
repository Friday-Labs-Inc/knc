import { useParams, Link } from 'react-router-dom'
import { useFrappeGetCall } from 'frappe-react-sdk'
import Layout from '../components/Layout'

// /journal/<slug> — one post. Body is rendered as paragraphs (split on blank
// lines); proper Markdown is a later polish. Content is desk-managed (Article).
type Article = {
  title: string
  excerpt?: string
  cover_image?: string | null
  author?: string
  category?: string
  published_on?: string
  body?: string
}

export default function ArticlePost() {
  const { slug } = useParams()
  const { data, isLoading, error } = useFrappeGetCall<{ message: Article }>(
    'knc.api.v1.get_article',
    { slug },
  )
  const a = (data?.message ?? (data as unknown)) as Article | undefined

  if (isLoading) {
    return (
      <Layout>
        <div className="px-5 py-40 text-center text-sm text-ink-muted">Loading…</div>
      </Layout>
    )
  }
  if (error || !a?.title) {
    return (
      <Layout>
        <div className="mx-auto max-w-narrow px-5 py-40 md:px-8">
          <Link to="/journal" className="text-sm text-ink-muted transition-colors duration-150 hover:text-ink">
            ← Journal
          </Link>
          <p className="mt-10 text-ink-muted">Post not found.</p>
        </div>
      </Layout>
    )
  }

  const meta = [a.category, a.published_on].filter(Boolean).join(' · ')

  return (
    <Layout>
      <article className="mx-auto max-w-narrow px-5 py-24 md:px-8">
        <Link to="/journal" className="text-sm text-ink-muted transition-colors duration-150 hover:text-ink">
          ← Journal
        </Link>
        {meta && <p className="mb-4 mt-10 text-xs font-medium uppercase tracking-[0.14em] text-ink-muted">{meta}</p>}
        <h1 className="mb-8 text-4xl font-light leading-[1.1] tracking-head text-ink md:text-5xl">{a.title}</h1>

        {a.cover_image && (
          <div className="mb-12 aspect-[16/9] overflow-hidden rounded-card border border-line bg-[#1A1A1A]">
            <img src={a.cover_image} alt={a.title} className="h-full w-full object-cover" />
          </div>
        )}

        <div className="space-y-6">
          {(a.body ?? '')
            .split('\n\n')
            .filter(Boolean)
            .map((para, i) => (
              <p key={i} className="whitespace-pre-line text-lg leading-relaxed text-ink-soft">
                {para}
              </p>
            ))}
        </div>

        {a.author && (
          <p className="mt-12 border-t border-line pt-6 text-[13px] text-ink-muted">By {a.author}</p>
        )}
      </article>
    </Layout>
  )
}
