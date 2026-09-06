import { useFrappeGetCall } from 'frappe-react-sdk'

// Pick exactly three KNC Brand Attributes — rendered as toggle chips. Options come
// from api/v1.get_brand_attributes (the 12 seeded attributes).
export function PersonalityPicker({
  value,
  onChange,
}: {
  value: string[] | undefined
  onChange: (v: string[]) => void
}) {
  const { data } = useFrappeGetCall<{ message: string[] }>('knc.api.v1.get_brand_attributes')
  const attrs: string[] = Array.isArray(data) ? data : (data?.message ?? [])
  const selected = value ?? []

  const toggle = (a: string) => {
    if (selected.includes(a)) onChange(selected.filter((x) => x !== a))
    else if (selected.length < 3) onChange([...selected, a])
  }

  return (
    <div>
      <p className="mb-3 text-sm text-ink-soft">
        Pick three words for the brand <span className="text-ink-faint">({selected.length}/3)</span>
      </p>
      <div className="flex flex-wrap gap-2">
        {attrs.map((a) => {
          const on = selected.includes(a)
          return (
            <button
              key={a}
              type="button"
              onClick={() => toggle(a)}
              className={`rounded-pill border px-4 py-2 text-sm transition-colors duration-150 ${
                on
                  ? 'border-white bg-white text-bg'
                  : 'border-line bg-surface-1 text-ink-soft hover:border-line-hover hover:text-ink'
              }`}
            >
              {a}
            </button>
          )
        })}
      </div>
    </div>
  )
}
