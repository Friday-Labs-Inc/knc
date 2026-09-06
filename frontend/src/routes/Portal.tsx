import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useFrappeAuth, useFrappeGetCall, useFrappePostCall } from 'frappe-react-sdk'
import Nav from '../components/Nav'

// The customer portal — one project view, wired to api/v1.get_project_state /
// decide_gate / post_comment. Guests are bounced to /login. The two gates are
// the only places the customer acts (pick a direction; approve or refine).
type Task = { name: string; subject: string; status: string; is_gate: number }
type Decision = { gate: string; round: number; decision: string; chosen_direction?: string }
type State = {
  projects: string[]
  project?: { name: string; title: string; status: string; percent_complete: number }
  tasks?: Task[]
  gate?: { open: boolean; task?: string; which?: string; paused?: boolean }
  decisions?: Decision[]
  brief?: { company_name?: string }
}

const card =
  'w-full rounded-xl border border-input-border bg-input-bg px-4 py-3 text-sm text-ink outline-none transition-colors duration-150 placeholder:text-input-focus focus:border-input-focus'

export default function Portal() {
  const navigate = useNavigate()
  const { currentUser, isLoading: authLoading } = useFrappeAuth()
  const { data, isLoading, mutate } = useFrappeGetCall<{ message: State }>(
    'knc.api.v1.get_project_state',
    {},
  )
  const state = (data?.message ?? (data as unknown)) as State | undefined
  const { call: decideGate } = useFrappePostCall('knc.api.v1.decide_gate')
  const { call: postComment } = useFrappePostCall('knc.api.v1.post_comment')

  const [comment, setComment] = useState('')
  const [gateNote, setGateNote] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!authLoading && (!currentUser || currentUser === 'Guest')) navigate('/login')
  }, [authLoading, currentUser, navigate])

  const project = state?.project
  const gate = state?.gate

  const decide = async (which: string, decision: string, direction?: string) => {
    if (!project) return
    setBusy(true)
    try {
      await decideGate({
        project: project.name,
        gate: which,
        decision,
        chosen_direction: direction ?? null,
        comments: gateNote || null,
      })
      setGateNote('')
      mutate()
    } finally {
      setBusy(false)
    }
  }

  const send = async () => {
    if (!project || !comment.trim()) return
    await postComment({ project: project.name, content: comment.trim() })
    setComment('')
    mutate()
  }

  if (authLoading || isLoading) {
    return (
      <>
        <Nav />
        <main className="pt-[140px] text-center text-sm text-ink-muted">Loading…</main>
      </>
    )
  }

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-narrow px-5 pb-24 pt-[100px] md:px-8">
        {!project ? (
          <div className="py-24 text-center">
            <h1 className="mb-4 text-3xl font-light tracking-head text-ink">No active engagement.</h1>
            <p className="text-ink-muted">When your project starts, it shows up here.</p>
          </div>
        ) : (
          <>
            <p className="mb-2 text-xs font-medium uppercase tracking-[0.14em] text-ink-muted">
              {state?.brief?.company_name || 'Your project'}
            </p>
            <h1 className="mb-1 text-4xl font-light tracking-head text-ink">{project.title}</h1>
            <p className="mb-8 text-sm text-ink-muted">{project.status}</p>
            <div className="mb-12 h-1 overflow-hidden rounded-full bg-line">
              <div className="h-full bg-ink-muted" style={{ width: `${project.percent_complete || 0}%` }} />
            </div>

            {gate?.open && (
              <div className="mb-12 rounded-card border border-line-hover bg-surface-1 p-6">
                <p className="mb-1 text-xs font-medium uppercase tracking-[0.12em] text-ink-muted">
                  {gate.which} — your call
                </p>
                <h2 className="mb-4 text-xl font-light text-ink">{gate.task}</h2>
                {gate.paused && <p className="mb-4 text-[13px] text-ink-muted">Timeline paused — waiting on you.</p>}
                <textarea
                  value={gateNote}
                  onChange={(e) => setGateNote(e.target.value)}
                  placeholder="Comments (optional)"
                  rows={2}
                  className={`${card} mb-4 resize-none`}
                />
                {gate.which === 'Gate 1' ? (
                  <div className="flex flex-wrap gap-2">
                    {['A', 'B', 'C'].map((d) => (
                      <button
                        key={d}
                        disabled={busy}
                        onClick={() => decide('Gate 1', 'Direction Selected', d)}
                        className="rounded-pill border border-line px-5 py-2.5 text-sm font-medium text-ink transition-colors duration-150 hover:border-line-hover disabled:opacity-50"
                      >
                        Choose direction {d}
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    <button
                      disabled={busy}
                      onClick={() => decide('Gate 2', 'Approved')}
                      className="rounded-pill bg-white px-5 py-2.5 text-sm font-medium text-bg transition-colors duration-150 hover:bg-[#E8E8E8] disabled:opacity-50"
                    >
                      Approve
                    </button>
                    <button
                      disabled={busy}
                      onClick={() => decide('Gate 2', 'Refinement Requested')}
                      className="rounded-pill border border-line px-5 py-2.5 text-sm font-medium text-ink transition-colors duration-150 hover:border-line-hover disabled:opacity-50"
                    >
                      Request refinements
                    </button>
                  </div>
                )}
              </div>
            )}

            <h2 className="mb-4 text-xs font-medium uppercase tracking-[0.14em] text-ink-muted">Timeline</h2>
            <div className="mb-12">
              {(state?.tasks ?? []).map((t) => {
                const done = t.status === 'Completed'
                const active = t.status === 'Working'
                return (
                  <div key={t.name} className="flex items-center gap-3 border-b border-line py-3">
                    <span className={`text-sm ${done || active ? 'text-ink' : 'text-ink-faint'}`}>
                      {done ? '✓' : active ? '→' : '·'}
                    </span>
                    <span className={`text-sm ${active ? 'text-ink' : done ? 'text-ink-soft' : 'text-ink-muted'}`}>
                      {t.subject}
                    </span>
                    {t.is_gate ? (
                      <span className="ml-auto text-[11px] uppercase tracking-[0.1em] text-ink-faint">Gate</span>
                    ) : null}
                  </div>
                )
              })}
            </div>

            {(state?.decisions?.length ?? 0) > 0 && (
              <div className="mb-12">
                <h2 className="mb-4 text-xs font-medium uppercase tracking-[0.14em] text-ink-muted">Decisions</h2>
                {(state?.decisions ?? []).map((d, i) => (
                  <p key={i} className="border-b border-line py-2 text-sm text-ink-soft">
                    {d.gate} · round {d.round} · {d.decision}
                    {d.chosen_direction ? ` — ${d.chosen_direction}` : ''}
                  </p>
                ))}
              </div>
            )}

            <h2 className="mb-4 text-xs font-medium uppercase tracking-[0.14em] text-ink-muted">Message the team</h2>
            <div className="flex gap-2">
              <input
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Write a message…"
                className={card}
              />
              <button
                onClick={send}
                className="shrink-0 rounded-pill bg-white px-5 text-sm font-medium text-bg transition-colors duration-150 hover:bg-[#E8E8E8]"
              >
                Send
              </button>
            </div>
          </>
        )}
      </main>
    </>
  )
}
