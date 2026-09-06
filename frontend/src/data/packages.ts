// The pricing ladder: $699 → $4,999. Same pipeline, scaled by depth and how much
// of the expert gate you get. Identity is the anchor (most chosen). DRAFT — prices
// and scope are the business-head proposal; the backend (install.py RP-ESSENTIALS)
// still seeds the single $4,800 item until these are blessed.
export type Pkg = {
  name: string
  price: string
  cadence: string
  tagline: string
  includes: string[]
  for: string
  featured?: boolean
}

export const PACKAGES: Pkg[] = [
  {
    name: 'Mark',
    price: '$699',
    cadence: '5 days · one gate',
    tagline: 'The fastest path to a real identity.',
    includes: [
      'Primary logo, wordmark, monogram',
      'Core colour + type pairing',
      'One-page usage sheet',
      'Source files',
    ],
    for: 'Founders who need to look credible now.',
  },
  {
    name: 'Identity',
    price: '$2,499',
    cadence: '10 days · two gates',
    tagline: 'The full brand system — the complete machine.',
    includes: [
      'Positioning + naming territory',
      'Three creative directions — you pick one',
      'Full logo suite',
      'Complete colour, type & core system',
      'Brand guidelines',
      'All source files',
    ],
    for: 'Startups committing to a brand that lasts.',
    featured: true,
  },
  {
    name: 'Launch',
    price: '$4,999',
    cadence: '14 days · two gates + build',
    tagline: 'Everything to go to market — brand and website.',
    includes: [
      'Everything in Identity',
      'A designed, built website (landing or up to 5 pages)',
      'Launch mockups — social, card, email signature',
      'Brand guidelines PDF',
    ],
    for: 'Teams who want one studio to take them live.',
  },
]
