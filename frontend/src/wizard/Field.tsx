import { COUNTRIES, type Field as FieldDef } from './schema'

// Shared input look — the Draft. dark input style, reused across the wizard.
const inputCls =
  'w-full rounded-xl border border-input-border bg-input-bg px-4 py-3 text-base text-ink outline-none transition-colors duration-150 placeholder:text-input-focus focus:border-input-focus'

export function Field({
  field,
  value,
  onChange,
}: {
  field: FieldDef
  value: unknown
  onChange: (v: unknown) => void
}) {
  const id = field.name
  const v = (value ?? '') as string

  if (field.type === 'check') {
    return (
      <label htmlFor={id} className="flex cursor-pointer items-start gap-3">
        <input
          id={id}
          type="checkbox"
          checked={!!value}
          onChange={(e) => onChange(e.target.checked)}
          className="mt-1 h-4 w-4 accent-white"
        />
        <span className="text-sm text-ink-soft">{field.label}</span>
      </label>
    )
  }

  return (
    <div>
      <label htmlFor={id} className="mb-2 block text-sm text-ink-soft">
        {field.label}
        {field.required && <span className="text-ink-faint"> *</span>}
      </label>

      {field.type === 'textarea' ? (
        <textarea
          id={id}
          value={v}
          onChange={(e) => onChange(e.target.value)}
          placeholder={field.placeholder}
          rows={3}
          className={`${inputCls} resize-none`}
        />
      ) : field.type === 'select' || field.type === 'country' ? (
        <select id={id} value={v} onChange={(e) => onChange(e.target.value)} className={inputCls}>
          <option value="">Select…</option>
          {(field.type === 'country' ? COUNTRIES : field.options ?? []).map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>
      ) : (
        <input
          id={id}
          type={field.type === 'email' ? 'email' : field.type === 'date' ? 'date' : 'text'}
          value={v}
          onChange={(e) => onChange(e.target.value)}
          placeholder={field.placeholder}
          className={inputCls}
        />
      )}

      {field.help && <p className="mt-1.5 text-[13px] text-ink-faint">{field.help}</p>}
    </div>
  )
}
