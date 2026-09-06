// References — up to 10 links to work you like. File uploads are deferred to
// after checkout (per the spec, brief uploads are copied to Drive at kickoff),
// so the wizard captures URLs here.
type Ref = { type: 'URL'; url: string }

export function ReferenceRepeater({
  value,
  onChange,
}: {
  value: Ref[] | undefined
  onChange: (v: Ref[]) => void
}) {
  const rows = value ?? []
  const setRow = (i: number, url: string) =>
    onChange(rows.map((r, idx) => (idx === i ? { type: 'URL', url } : r)))
  const add = () => rows.length < 10 && onChange([...rows, { type: 'URL', url: '' }])
  const remove = (i: number) => onChange(rows.filter((_, idx) => idx !== i))

  return (
    <div>
      <p className="mb-3 text-sm text-ink-soft">
        References <span className="text-ink-faint">links to work you like</span>
      </p>
      <div className="space-y-2">
        {rows.map((r, i) => (
          <div key={i} className="flex gap-2">
            <input
              value={r.url}
              onChange={(e) => setRow(i, e.target.value)}
              placeholder="https://…"
              className="w-full rounded-xl border border-input-border bg-input-bg px-4 py-3 text-base text-ink outline-none transition-colors duration-150 placeholder:text-input-focus focus:border-input-focus"
            />
            <button
              type="button"
              onClick={() => remove(i)}
              className="shrink-0 rounded-xl border border-line px-4 text-sm text-ink-muted transition-colors duration-150 hover:border-line-hover hover:text-ink"
            >
              Remove
            </button>
          </div>
        ))}
      </div>
      {rows.length < 10 && (
        <button type="button" onClick={add} className="mt-3 text-[13px] text-ink-muted transition-colors duration-150 hover:text-ink">
          + Add a reference
        </button>
      )}
    </div>
  )
}
