import { useState } from 'react'
import { useFrappePostCall, useFrappeGetCall } from 'frappe-react-sdk'
import { STEPS } from './schema'
import { Field } from './Field'
import { PersonalityPicker } from './PersonalityPicker'
import { ReferenceRepeater } from './ReferenceRepeater'

type Data = Record<string, unknown>

// The onboarding wizard. Each "Next" auto-saves that step's fields to a Draft
// KNC Brief (api/v1.save_step), persisting {brief, token} so a refresh
// resumes. The final step submits → Stripe checkout.
export default function Wizard({ intro }: { intro?: string }) {
  const [step, setStep] = useState(0) // 0..5 = steps; STEPS.length = review
  const [data, setData] = useState<Data>(() => (intro ? { what_you_do: intro } : {}))
  const [brief, setBrief] = useState<string | null>(() => localStorage.getItem('knc_brief'))
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('knc_token'))
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { call: saveStep } = useFrappePostCall('knc.api.v1.save_step')
  const { call: submitBrief } = useFrappePostCall('knc.api.v1.submit_brief')
  const { data: capRaw } = useFrappeGetCall<{ message: { available: boolean; message?: string } }>(
    'knc.api.v1.check_capacity',
  )
  const capacity = (capRaw as { message?: unknown })?.message ?? capRaw

  const isReview = step === STEPS.length
  const current = STEPS[step]
  const set = (name: string, v: unknown) => setData((d) => ({ ...d, [name]: v }))

  const collectStep = (s: number): Data => {
    const out: Data = {}
    for (const f of STEPS[s].fields) if (f.name in data) out[f.name] = data[f.name]
    return out
  }

  const validateStep = (s: number): string | null => {
    for (const f of STEPS[s].fields) {
      if (f.showIf && !f.showIf(data)) continue
      if (f.required && !data[f.name]) return `${f.label} is required.`
    }
    if (s === 4 && ((data.personality as string[])?.length ?? 0) !== 3)
      return 'Pick exactly three words for the brand.'
    return null
  }

  const next = async () => {
    setError(null)
    const v = validateStep(step)
    if (v) return setError(v)
    setBusy(true)
    try {
      const res = await saveStep({
        step: step + 1,
        data: JSON.stringify(collectStep(step)),
        brief,
        token,
      })
      const out = (res?.message ?? res) as { brief: string; token: string }
      setBrief(out.brief)
      setToken(out.token)
      localStorage.setItem('knc_brief', out.brief)
      localStorage.setItem('knc_token', out.token)
      setStep((s) => s + 1)
      window.scrollTo({ top: 0 })
    } catch (e) {
      setError((e as Error)?.message || 'Could not save — check the required fields.')
    } finally {
      setBusy(false)
    }
  }

  const submit = async () => {
    setBusy(true)
    setError(null)
    try {
      const res = await submitBrief({ brief, token })
      const out = (res?.message ?? res) as { payment_url: string }
      localStorage.removeItem('knc_brief')
      localStorage.removeItem('knc_token')
      window.location.href = out.payment_url
    } catch (e) {
      setError(
        (e as Error)?.message ||
          'Could not start checkout — payment isn’t configured on this site yet.',
      )
      setBusy(false)
    }
  }

  return (
    <div>
      {/* progress */}
      <div className="mb-10 flex gap-1.5">
        {STEPS.map((_, i) => (
          <span key={i} className={`h-0.5 flex-1 rounded-full ${i <= step ? 'bg-ink-muted' : 'bg-line'}`} />
        ))}
      </div>

      {isReview ? (
        <div>
          <p className="mb-3 text-xs font-medium uppercase tracking-[0.14em] text-ink-muted">Review</p>
          <h1 className="mb-8 text-3xl font-light tracking-head text-ink md:text-4xl">One last look.</h1>
          <dl className="space-y-3 border-y border-line py-6">
            {STEPS.flatMap((s) => s.fields)
              .filter((f) => f.type !== 'check' && data[f.name] && (data[f.name] as unknown[]).length !== 0)
              .map((f) => (
                <div key={f.name} className="flex gap-6 text-sm">
                  <dt className="w-44 shrink-0 text-ink-muted">{f.label}</dt>
                  <dd className="text-ink-soft">
                    {Array.isArray(data[f.name])
                      ? (data[f.name] as { url?: string }[]).map((r) => r.url ?? r).join(', ')
                      : String(data[f.name])}
                  </dd>
                </div>
              ))}
          </dl>
          <p className="mt-6 text-[13px] text-ink-muted">
            Submitting takes you to secure checkout. Your brief is saved as a draft until payment.
          </p>
        </div>
      ) : (
        <div>
          <p className="mb-3 text-xs font-medium uppercase tracking-[0.14em] text-ink-muted">{current.eyebrow}</p>
          <h1 className="mb-8 text-3xl font-light tracking-head text-ink md:text-4xl">{current.title}</h1>

          <div className="space-y-6">
            {current.fields.map((f) => {
              if (f.showIf && !f.showIf(data)) return null
              if (f.type === 'personality')
                return (
                  <PersonalityPicker
                    key={f.name}
                    value={data.personality as string[] | undefined}
                    onChange={(v) => set('personality', v)}
                  />
                )
              if (f.type === 'references')
                return (
                  <ReferenceRepeater
                    key={f.name}
                    value={data.references as { type: 'URL'; url: string }[] | undefined}
                    onChange={(v) => set('references', v)}
                  />
                )
              return <Field key={f.name} field={f} value={data[f.name]} onChange={(v) => set(f.name, v)} />
            })}

            {step === 5 && capacity && !(capacity as { available?: boolean }).available && (
              <p className="text-[13px] text-ink-muted">
                {(capacity as { message?: string }).message || 'We’re near capacity — we’ll confirm your start date.'}
              </p>
            )}
          </div>
        </div>
      )}

      {error && <p className="mt-6 text-sm text-ink-soft">{error}</p>}

      {/* nav */}
      <div className="mt-10 flex items-center justify-between">
        <button
          type="button"
          onClick={() => {
            setError(null)
            setStep((s) => Math.max(0, s - 1))
          }}
          className={`text-sm text-ink-muted transition-colors duration-150 hover:text-ink ${step === 0 ? 'invisible' : ''}`}
        >
          ← Back
        </button>

        {isReview ? (
          <button
            type="button"
            disabled={busy}
            onClick={submit}
            className="rounded-pill bg-white px-6 py-3 text-sm font-medium text-bg transition-colors duration-150 hover:bg-[#E8E8E8] disabled:opacity-50"
          >
            {busy ? 'Starting…' : 'Pay & start project'}
          </button>
        ) : (
          <button
            type="button"
            disabled={busy}
            onClick={next}
            className="rounded-pill bg-white px-6 py-3 text-sm font-medium text-bg transition-colors duration-150 hover:bg-[#E8E8E8] disabled:opacity-50"
          >
            {busy ? 'Saving…' : step === STEPS.length - 1 ? 'Review' : 'Continue'}
          </button>
        )}
      </div>
    </div>
  )
}
