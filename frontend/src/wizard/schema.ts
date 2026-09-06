// The /start wizard, transcribed from ONBOARDING-BRIEF-SPEC.md. Six steps, each
// auto-saves a Draft brief via api/v1.save_step. Field names match the Onboarding
// Brief doctype exactly; types/options match its Select fields.
export type FieldType =
  | 'text'
  | 'email'
  | 'textarea'
  | 'select'
  | 'date'
  | 'check'
  | 'country'
  | 'personality'
  | 'references'

export interface Field {
  name: string
  label: string
  type: FieldType
  required?: boolean
  placeholder?: string
  options?: string[]
  help?: string
  showIf?: (data: Record<string, unknown>) => boolean
}

export interface Step {
  eyebrow: string
  title: string
  fields: Field[]
}

// Curated list of valid Frappe Country names (the field is a Link to Country).
// Keeps the brief saving without shipping all ~250 — full list is a later polish.
export const COUNTRIES = [
  'United States', 'United Kingdom', 'India', 'United Arab Emirates', 'Canada',
  'Australia', 'Germany', 'France', 'Netherlands', 'Singapore', 'Other',
]

export const STEPS: Step[] = [
  {
    eyebrow: 'Step 1 of 6',
    title: 'Tell us who you are.',
    fields: [
      { name: 'full_name', label: 'Full name', type: 'text', required: true },
      { name: 'email', label: 'Email', type: 'email', required: true, help: 'This becomes your portal login.' },
      { name: 'company_name', label: 'Company name', type: 'text', required: true },
      { name: 'website_or_social', label: 'Website or social', type: 'text', placeholder: 'optional' },
      { name: 'country', label: 'Country', type: 'country' },
      { name: 'lead_source', label: 'How did you hear about us?', type: 'select', options: ['Search', 'YouTube', 'Instagram', 'LinkedIn', 'Twitter / X', 'Referral', 'Other'] },
    ],
  },
  {
    eyebrow: 'Step 2 of 6',
    title: 'The business.',
    fields: [
      { name: 'what_you_do', label: 'What do you do?', type: 'textarea', required: true, placeholder: 'Explain it like you would to a friend.' },
      { name: 'category', label: 'Category', type: 'select', options: ['SaaS', 'Fintech', 'D2C', 'Skincare', 'Media', 'Agency', 'Other'] },
      { name: 'stage', label: 'Stage', type: 'select', options: ['Idea', 'Pre-launch', 'Launched', 'Rebranding'] },
    ],
  },
  {
    eyebrow: 'Step 3 of 6',
    title: 'Audience & edge.',
    fields: [
      { name: 'target_audience', label: 'Target audience', type: 'textarea', placeholder: 'Who buys, who decides.' },
      { name: 'competitors', label: 'Competitors', type: 'textarea', placeholder: '2–3 names or links.' },
      { name: 'differentiator', label: 'What makes you different?', type: 'textarea', required: true },
    ],
  },
  {
    eyebrow: 'Step 4 of 6',
    title: 'Naming.',
    fields: [
      { name: 'naming_status', label: 'Where are you with a name?', type: 'select', options: ['Name is locked', 'Open to exploring', 'Need a name'] },
      { name: 'current_name', label: 'Current name', type: 'text', showIf: (d) => d.naming_status !== 'Need a name' && !!d.naming_status },
      { name: 'name_meaning', label: 'What does it mean?', type: 'textarea', placeholder: 'optional' },
    ],
  },
  {
    eyebrow: 'Step 5 of 6',
    title: 'Taste & tone.',
    fields: [
      { name: 'personality', label: 'Pick three words for the brand', type: 'personality' },
      { name: 'brands_admired', label: 'Brands you admire', type: 'textarea', placeholder: '2–3 brands, and why.' },
      { name: 'avoid', label: 'Anything to avoid?', type: 'textarea', placeholder: 'Colours, styles, clichés.' },
      { name: 'references', label: 'References', type: 'references' },
    ],
  },
  {
    eyebrow: 'Step 6 of 6',
    title: 'Logistics.',
    fields: [
      { name: 'preferred_start', label: 'Preferred start date', type: 'date' },
      { name: 'gate_commitment', label: 'I’ll respond within 24 hours at the two gates.', type: 'check', required: true },
      { name: 'terms_accepted', label: 'I accept the terms.', type: 'check', required: true },
      { name: 'notes', label: 'Anything else?', type: 'textarea', placeholder: 'optional' },
    ],
  },
]
