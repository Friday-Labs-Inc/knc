import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

// The hero interaction — the page's single most important element, modelled on
// the ChatGPT input bar. What the visitor types becomes the opening of their
// brief; submitting carries it into the /start wizard.
export default function HeroInput() {
  const [value, setValue] = useState('')
  const ref = useRef<HTMLTextAreaElement>(null)
  const navigate = useNavigate()

  const grow = () => {
    const el = ref.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`
  }

  const submit = () => navigate('/start', { state: { intro: value.trim() } })

  const active = value.trim().length > 0

  return (
    <div className="mx-auto w-full max-w-narrow rounded-input border border-input-border bg-input-bg p-4 pl-5 transition-colors duration-150 focus-within:border-input-focus">
      <textarea
        ref={ref}
        rows={1}
        value={value}
        onChange={(e) => {
          setValue(e.target.value)
          grow()
        }}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            submit()
          }
        }}
        placeholder="Tell us about your brand…"
        className="block max-h-[200px] min-h-[24px] w-full resize-none bg-transparent text-base leading-relaxed text-ink caret-white outline-none placeholder:text-input-focus"
      />

      <div className="mt-2.5 flex items-center justify-between">
        <span className="text-xs text-ink-faint">Press Enter to begin</span>
        <button
          type="button"
          onClick={submit}
          aria-label="Start a project"
          className={`flex h-[34px] w-[34px] items-center justify-center rounded-full transition-colors duration-150 ${
            active ? 'bg-white text-bg hover:bg-[#E8E8E8]' : 'bg-surface-2 text-input-focus'
          }`}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
            <path d="M12 19V5M5 12l7-7 7 7" />
          </svg>
        </button>
      </div>
    </div>
  )
}
