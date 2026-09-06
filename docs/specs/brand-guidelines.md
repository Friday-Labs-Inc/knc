# Draft. — Complete Brand & Website Guidelines
### Single source of truth · v1.0

> Feed this entire document to any AI coding tool, design tool, or developer.
> It covers everything: philosophy, colors, typography, components, interactions,
> and the full page — section by section, element by element.

---

## 0. What This Company Is

**Draft.** is an AI-guided branding and web design studio for early-stage startups.

- **Price:** $700 flat
- **Delivery:** 10 days
- **What's included:** Logo, brand identity kit, digital mockups, and a website (single landing page or 5-page site)
- **How it works:** Client fills a questionnaire → AI generates creative directions → expert team refines and delivers
- **Positioning:** Fast, focused, premium — not cheap, not slow

The website must feel like the product is already world-class. It earns trust through restraint, not decoration.

---

## 1. Design Philosophy

**Dark. Minimal. Editorial.**

The entire visual language is modeled on openai.com:
- True black canvas. Everything lives on darkness.
- Content is the design. No decoration fills the silence.
- Large, light-weight type. Scale and restraint replace visual noise.
- The interaction — the input bar — is the hero. Everything else supports it.
- Premium is expressed through what is removed, not what is added.

One rule: if you're about to add something, ask if removing it makes the page better. It usually does.

---

## 2. Color System

### Core Palette

| Token | Name | Hex | Use |
|---|---|---|---|
| `--bg` | True Black | `#0A0A0A` | Page background — everything |
| `--surface-1` | Card Black | `#111111` | Cards, elevated surfaces |
| `--surface-2` | Lifted | `#181818` | Inputs, hovered cards |
| `--border` | Dark Border | `#242424` | All borders, dividers |
| `--border-hover` | Hover Border | `#383838` | Hovered inputs, focused cards |
| `--text-primary` | White | `#FFFFFF` | Headlines, active elements |
| `--text-secondary` | Soft White | `#C0C0C0` | Body text, descriptions |
| `--text-muted` | Dim | `#707070` | Labels, captions, placeholders, meta |
| `--text-faint` | Ghost | `#404040` | Disabled, very secondary |
| `--btn-primary-bg` | White | `#FFFFFF` | Primary button background |
| `--btn-primary-text` | Black | `#0A0A0A` | Primary button text |
| `--input-bg` | Input Dark | `#141414` | Input/textarea background |
| `--input-border` | Input Border | `#2E2E2E` | Input border default |
| `--input-border-focus`| Input Focus | `#505050` | Input border on focus |

### Rules
- Zero color anywhere. No accent tones. No blue, green, purple — nothing. Black, white, gray only.
- No gradients on UI elements.
- No box-shadows. Depth = background-color steps.
- One and only one light section exists on the entire page (the footer strip), purely for copyright text.
- Imagery is the only visual texture in the card grid below the fold.

---

## 3. Typography

### Font

OpenAI uses **Söhne** by Klim Type Foundry (licensed). Mirror it exactly with this stack:

```css
font-family: 'Söhne', 'Inter', ui-sans-serif, -apple-system, BlinkMacSystemFont, sans-serif;
```

**For production:** License Söhne at klim.co.nz — it's the correct choice.
**Free fallback:** Inter from Google Fonts.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
```

Single typeface. No mixing. No serif. No decorative font.

### Weights — Only Three

| Weight | Value | Used for |
|---|---|---|
| Light | `300` | All headlines, hero text, section titles, card titles |
| Regular | `400` | All body copy, descriptions, nav links, input text, captions |
| Medium | `500` | Buttons, labels, eyebrows, tags, icon buttons, nav CTA |

**Hard rule:** 600, 700, 900 are banned. Italic is banned.
The entire brand personality lives in the contrast between Light headlines on black. A heavier weight destroys it.

### Type Scale

| Role | Size | Weight | Line-height | Letter-spacing |
|---|---|---|---|---|
| Hero — wordmark | 18px | 500 | 1 | -0.01em |
| Hero — tagline | 52–64px | 300 | 1.06 | -0.035em |
| Section headline | 40–48px | 300 | 1.1 | -0.025em |
| Card title | 20–24px | 300 | 1.2 | -0.015em |
| Sub-headline | 18–20px | 400 | 1.4 | -0.01em |
| Body | 16px | 400 | 1.75 | 0 |
| Input placeholder | 16px | 400 | 1 | 0 |
| Label / Eyebrow | 11px | 500 | 1.4 | 0.12em + uppercase |
| Tag / Badge | 11px | 500 | 1 | 0.06em + uppercase |
| Button | 14px | 500 | 1 | 0.01em |
| Caption / meta | 13px | 400 | 1.5 | 0 |
| Footer / legal | 13px | 400 | 1.6 | 0 |

### Typography Rules
- Headlines must feel slightly too large. That's the whole move.
- Tight letter-spacing on large text (`-0.03em` to `-0.04em`). This is what separates premium from generic.
- Body text: `#C0C0C0` on dark. Never pure white — it's harsh.
- Labels/eyebrows: uppercase, `#707070`, 11px. Tiny and controlled.
- Never underline anything except actual hyperlinks.
- Never bold within a paragraph. No `<strong>` in body copy.

---

## 4. Spacing System

Base unit: **8px**. Every value is a multiple of 8.

```
8 · 16 · 24 · 32 · 40 · 48 · 64 · 80 · 96 · 128 · 160px
```

### Layout Tokens

| Token | Value |
|---|---|
| Max page width | `1120px` |
| Narrow content width | `680px` |
| Page horizontal padding | `40px` desktop · `20px` mobile |
| Section vertical padding | `96px` desktop · `64px` mobile |
| Card padding | `28–32px` |
| Grid gap | `16px` |
| Nav height | `60px` |
| Input bar height | `56px` |
| Border radius — page cards | `12px` |
| Border radius — input bar | `16px` |
| Border radius — buttons (pill) | `999px` |
| Border radius — tags | `6px` |
| Border radius — icon buttons | `50%` (circle) |

---

## 5. Components

### 5.1 Navigation

Modeled on openai.com — logo left, nav links center, single CTA right.

```
Position:       fixed, top 0, full viewport width, z-index 100
Height:         60px
Background:     rgba(10, 10, 10, 0.85)
Backdrop:       blur(20px) saturate(160%)
Border-bottom:  1px solid #242424
Inner layout:   max-width 1120px · margin 0 auto · padding 0 40px
                display: flex · align-items: center · justify-content: space-between

─────────────────────────────────────────────────────────────────
LEFT — Logo
  "Draft."
  Font:           16px · weight 500 · #FFFFFF · letter-spacing -0.01em
  Link:           href="/" (reloads/scrolls to top)
  No icon. Text only.

CENTER — Navigation links
  Three links, displayed inline, gap: 36px

  Link 1: "Process"
    Scrolls to #timeline section
    OR opens a dropdown on hover (see dropdown spec below)

  Link 2: "Pricing"
    Scrolls to #deliverables section

  Link 3: "About"
    Scrolls to #about section (add this section — see Section 9.7 below)

  Link styling:
    Font:         14px · weight 400 · color #767676
    Hover:        color #FFFFFF
    Transition:   color 150ms ease
    No underline. No border. No background.
    Active state: color #FFFFFF (when that section is in viewport — use
                  IntersectionObserver to detect and apply .nav-active class)

  Dropdown (for "Process" — optional enhancement):
    Trigger:      hover on "Process" link
    Panel:        background #111111 · border 1px solid #242424
                  border-radius 10px · padding 8px · min-width 200px
                  position absolute · top calc(100% + 8px) · left 50%
                  transform translateX(-50%)
                  box-shadow: none

    Items inside panel:
      "How it works"     → scrolls to #timeline
      "What's included"  → scrolls to #deliverables
      "10-day delivery"  → scrolls to #timeline

    Item styling:
      padding: 10px 14px · border-radius 6px
      font: 14px · 400 · #C0C0C0
      hover: background #1A1A1A · color #FFFFFF
      transition: 100ms ease

RIGHT — CTA button
  "Start a project"
  Style:          pill · background #FFFFFF · color #0A0A0A
  Font:           14px · weight 500
  Padding:        10px 20px · border-radius 999px
  Border:         none
  Hover:          background #E8E8E8
  Transition:     150ms ease
  Action:         scrolls to hero input bar AND focuses the textarea
                  (same as clicking into the ChatGPT input)

─────────────────────────────────────────────────────────────────
MOBILE (max-width 640px):
  LEFT:   Logo "Draft."
  RIGHT:  Hamburger icon (≡ · 20px · #FFFFFF) — no center links visible

  Hamburger opens full-screen overlay:
    background: #0A0A0A · z-index 200 · position fixed · inset 0
    display: flex · flex-direction: column · align-items: center
    justify-content: center · gap: 32px

    Links (stacked, centered):
      Process · Pricing · About
      font: 24px · 300 · #FFFFFF
      hover: color #707070

    CTA button below links:
      "Start a project" — white pill · same spec as desktop

    Close button:
      top-right corner · ✕ icon · 20px · #707070
      hover: color #FFFFFF

  Overlay open/close: fade transition 200ms ease
─────────────────────────────────────────────────────────────────
```

### 5.2 Input Bar (Hero — primary interaction element)

This is the most important component on the page. It mirrors the ChatGPT input bar exactly.

```
Container:
  width:          100% · max-width: 680px · margin: 0 auto
  background:     #141414
  border:         1px solid #2E2E2E
  border-radius:  16px
  padding:        16px 16px 12px 20px
  display:        flex · flex-direction: column
  transition:     border-color 150ms ease

  On focus-within:
    border-color: #505050

Textarea (inside):
  width:          100%
  min-height:     24px · max-height: 200px (auto-grows)
  background:     transparent
  border:         none
  outline:        none
  resize:         none
  font:           16px, weight 400, #FFFFFF, font-family inherited
  line-height:    1.6
  caret-color:    #FFFFFF

  Placeholder text: "Tell us about your startup..."
  Placeholder color: #505050

Bottom row (inside, below textarea):
  display:        flex
  justify-content: space-between
  align-items:    center
  margin-top:     10px

  LEFT side — icon buttons (gap: 4px):

    Mic button:
      icon: microphone SVG (outline, 18px, stroke-width 1.5)
      size: 34px × 34px circle
      background: transparent
      border: none
      color: #707070
      hover: color #FFFFFF, background #1F1F1F, border-radius 50%
      transition: 150ms ease
      tooltip: "Record your brief"

      Active (recording) state:
        color: #FFFFFF
        background: #2A2A2A
        Pulsing ring animation: 
          box-shadow: 0 0 0 4px rgba(255,255,255,0.08)
          animation: pulse 1.5s ease-in-out infinite

    Attach button (optional, secondary):
      icon: paperclip SVG (outline, 18px, stroke-width 1.5)
      same styling as mic button
      color: #707070

  RIGHT side — Submit button:
    shape:          circle · 34px × 34px
    background:     #FFFFFF (active) · #2A2A2A (empty/disabled)
    border:         none
    border-radius:  50%
    icon:           arrow-up SVG · 16px · color #0A0A0A (active) · #505050 (disabled)
    transition:     background 150ms ease

    Enabled when:   textarea has content (length > 0)
    On click:       redirect to Google Form URL (new tab)
    
    Hover (enabled): background #E8E8E8

Behavior:
  - Textarea auto-expands as user types (up to max-height 200px, then scrolls internally)
  - Enter key submits (same as clicking arrow button)
  - Shift+Enter = new line
  - Mic button activates browser speech recognition API (Web Speech API)
    On recognition result: fills textarea with transcribed text
    Error fallback: show tooltip "Mic not supported in this browser"
```

### 5.3 Quick-Link Chips (below input bar)

Horizontal row of suggestion chips — exactly like OpenAI's quick-action links below the chat bar.

```
Container:
  display:        flex
  gap:            8px
  flex-wrap:      wrap
  justify-content: center
  margin-top:     16px

Each chip:
  display:        inline-flex · align-items: center · gap: 6px
  padding:        8px 14px
  background:     #111111
  border:         1px solid #242424
  border-radius:  999px
  font:           13px, weight 400, #C0C0C0
  cursor:         pointer
  transition:     border-color 150ms, color 150ms ease

  Hover:
    border-color: #383838
    color:        #FFFFFF

  Icon (optional, left):
    16px · stroke-width 1.5 · color: #707070 (inherits on hover)
```

**Four chips to show:**
1. `↗ See what's included` — scrolls to deliverables
2. `◷ How 10 days works` — scrolls to timeline
3. `⬡ View past work` — scrolls to case studies
4. `$ $700 flat rate` — scrolls to pricing

### 5.4 Project Cards (case study grid)

```
Card container:
  background:     #111111
  border:         1px solid #242424
  border-radius:  12px
  overflow:       hidden
  cursor:         default (or pointer if card is clickable)
  transition:     border-color 200ms ease

  Hover:
    border-color: #383838

Image area (top):
  width:          100%
  aspect-ratio:   16 / 10
  background:     #1A1A1A
  border-bottom:  1px solid #242424
  overflow:       hidden

  Real image: object-fit cover, width 100%, height 100%
  Placeholder (no image): background #1A1A1A, centered label
    "[ Project visual ]" · 11px · 500 · #303030 · uppercase

Card body (bottom):
  padding:        24px 28px 28px

  Tag row:
    font: 11px · 500 · uppercase · #707070 · letter-spacing 0.1em
    margin-bottom: 10px
    example: "FINTECH · LANDING PAGE"

  Title:
    font: 22px · 300 · #FFFFFF · letter-spacing -0.015em · line-height 1.2
    margin-bottom: 10px

  Description:
    font: 14px · 400 · #9A9A9A · line-height 1.65
    margin-bottom: 20px

  Meta row:
    border-top: 1px solid #1E1E1E
    padding-top: 16px
    font: 12px · 400 · #505050
    example: "Logo + brand kit  ·  Single landing page"
```

### 5.5 Buttons

**Primary pill (dark backgrounds):**
```
background:     #FFFFFF
color:          #0A0A0A
font:           14px · 500
border-radius:  999px
padding:        12px 24px
border:         none
hover:          background #E8E8E8
transition:     150ms ease
```

**Ghost pill (dark backgrounds):**
```
background:     transparent
color:          #FFFFFF
border:         1px solid #333333
border-radius:  999px
padding:        12px 24px
font:           14px · 500
hover:          border-color #606060
transition:     150ms ease
```

**Icon circle button:**
```
width/height:   34px
border-radius:  50%
background:     transparent
border:         none
color:          #707070
hover:          background #1F1F1F, color #FFFFFF
transition:     150ms ease
```

### 5.6 Dividers

```
Dark section: border-top: 1px solid #242424
Used only between major page sections. Never decorative.
```

### 5.7 Tags / Eyebrows

```
Eyebrow (above section headlines):
  font:           11px · 500 · uppercase · letter-spacing 0.14em
  color:          #707070
  margin-bottom:  16px
  display:        block

Inline tag / chip:
  background:     #161616
  border:         1px solid #242424
  border-radius:  6px
  padding:        3px 8px
  font:           11px · 500 · uppercase · letter-spacing 0.06em
  color:          #707070
```

---

## 6. Imagery

- No stock photography.
- Card image areas: abstract art, typographic compositions, dark geometric forms, or real project screenshots.
- Real project screenshots: desaturate to 20% saturation + dark overlay (`rgba(0,0,0,0.3)`) to integrate with the dark aesthetic.
- Placeholder: `background: #1A1A1A`, no text, or very faint label.
- Icons: outline style, `stroke-width: 1.5`, no fill, sized 18–20px inline.
- Icon set: Lucide Icons or Phosphor Icons (outline variant).
- No illustrations. No mascots. No emoji in UI.

---

## 7. Motion & Interaction

```
Default:          No animation. Stillness is the premium signal.

Hover transitions: color, background, border-color only
Duration:          150ms ease (UI elements) · 200ms ease (cards)

Scroll reveal (optional, tasteful):
  Property:       opacity 0→1 + translateY 16px→0
  Duration:       500ms ease-out
  Trigger:        IntersectionObserver, threshold 0.1
  Apply to:       card grid only (not hero)

Input bar focus:  border-color transition 150ms ease (no glow, no shadow)

Mic pulse animation (recording state only):
  @keyframes pulse {
    0%   { box-shadow: 0 0 0 0 rgba(255,255,255,0.12); }
    70%  { box-shadow: 0 0 0 8px rgba(255,255,255,0); }
    100% { box-shadow: 0 0 0 0 rgba(255,255,255,0); }
  }
  animation: pulse 1.5s ease-in-out infinite

NEVER:
  - Parallax
  - Scroll-jacking
  - Entrance animations on nav or hero text
  - Bounces or spring physics
  - Looping background animations
  - Auto-playing anything
```

---

## 8. Voice & Tone

- Declarative. Short. No adjectives that aren't specific.
- Sentence case. Always. Never Title Case on body. Never ALL CAPS on headlines.
- No exclamation marks.
- No buzzwords: powerful, seamless, revolutionary, game-changing, cutting-edge.
- Say exactly what happens — not how great it is.

| ❌ | ✅ |
|---|---|
| "Supercharge your startup's brand!" | "Your brand, ready in ten days." |
| "Leveraging cutting-edge AI technology" | "AI builds it. Experts direct it." |
| "World-class design at an unbeatable price" | "$700. Ten days. Everything to launch." |
| "We're passionate about helping startups" | "Built for founders who move fast." |
| "Seamless, powerful, intuitive experience" | "Answer a form. Get a brand." |

---

## 9. Full Page — Section by Section

The website is a **single page**. No routing. No sub-pages. One scrollable experience.

Page structure:
```
1. Nav (fixed) — Draft. · Process · Pricing · About · [Start a project]
2. Hero — wordmark + tagline + input bar + chips
3. What's included (#deliverables) — deliverables + price
4. Timeline (#timeline) — 10-day breakdown
5. Work (#work) — case study card grid
6. About (#about) — who we are + stats
7. Footer — minimal dark strip
```

All sections: `background: #0A0A0A`. No section breaks by color except footer.

---

### Section 1 — Navigation

```
DESKTOP:
┌──────────────────────────────────────────────────────────────────┐
│  Draft.          Process   Pricing   About        [Start a project]│
└──────────────────────────────────────────────────────────────────┘

MOBILE:
┌──────────────────────────────────────────────────────────────────┐
│  Draft.                                                       ☰  │
└──────────────────────────────────────────────────────────────────┘

Specs:
  position: fixed · top: 0 · width: 100% · z-index: 100
  height: 60px
  background: rgba(10,10,10,0.85) + backdrop-filter: blur(20px)
  border-bottom: 1px solid #242424
  inner max-width: 1120px · margin: 0 auto · padding: 0 40px
  display: flex · align-items: center · justify-content: space-between

LEFT:   "Draft." — 16px · 500 · #FFFFFF · href="/"

CENTER: Three nav links — gap 36px
  "Process"  → scrolls to #timeline
  "Pricing"  → scrolls to #deliverables
  "About"    → scrolls to #about
  Font: 14px · 400 · #767676 · hover #FFFFFF · transition 150ms
  Active (section in viewport): color #FFFFFF via IntersectionObserver

RIGHT:  "Start a project" — white pill button
  On click: scrolls to hero input bar AND focuses the textarea
  (mirrors the feel of clicking into ChatGPT)

See Component 5.1 for full nav spec including dropdown and mobile overlay.
```

---

### Section 2 — Hero

This is the entire above-the-fold experience. Center-aligned. Spacious.

```
LAYOUT:
  min-height:     100vh
  display:        flex · flex-direction: column
  align-items:    center · justify-content: center
  padding:        140px 40px 80px  (top accounts for fixed nav)
  text-align:     center
  background:     #0A0A0A

CONTENT ORDER (top to bottom):

① Wordmark / product name
  "Draft."
  font: 18px · 500 · #FFFFFF · letter-spacing -0.01em
  margin-bottom: 32px

② Tagline headline
  "Kickstart your startup
  with a brand and website
  in ten days."
  
  font: 52px (desktop) · 36px (mobile) · weight 300 · #FFFFFF
  line-height: 1.08 · letter-spacing: -0.03em
  max-width: 600px · margin: 0 auto 40px

  Line breaks are intentional — set as written above.

③ Sub-tagline
  "AI-guided. Expert-directed. $700 flat."
  
  font: 16px · 400 · #707070
  letter-spacing: 0
  margin-bottom: 40px

④ Input bar  [see Component 5.2 for full spec]
  max-width: 640px · width: 100% · margin: 0 auto

  Placeholder: "Tell us about your startup..."
  Mic button (left of submit)
  Submit button (arrow-up icon, right)

  On submit:
    → Opens Google Form URL in new tab
    → Pass textarea content as a URL param if possible:
      [GOOGLE_FORM_URL]?entry.XXXXX={encodeURIComponent(userText)}

⑤ Quick-link chips  [see Component 5.3 for full spec]
  margin-top: 20px

  Chips (left to right):
  · "See what's included"    → scrolls to #deliverables
  · "How 10 days works"      → scrolls to #timeline
  · "View past work"         → scrolls to #work
  · "$700 flat rate"         → scrolls to #deliverables (anchors to price block)

⑥ Scroll indicator (optional, very subtle)
  At bottom center: small downward chevron icon · 16px · #404040
  Fades in after 2s delay · gentle bob animation (translateY 0→4px, 1.5s infinite)
  Clicking scrolls to next section
```

---

### Section 3 — What's Included

**Anchor:** `id="deliverables"`

```
LAYOUT:
  padding: 96px 40px · max-width 1120px · margin: 0 auto
  border-top: 1px solid #242424

CONTENT:

① Eyebrow
  "WHAT'S INCLUDED"
  11px · 500 · uppercase · #707070 · letter-spacing 0.14em
  margin-bottom: 20px

② Headline
  "Everything to launch.
  Nothing extra."
  
  font: 44px · 300 · #FFFFFF · letter-spacing -0.025em · line-height 1.1
  max-width: 480px · margin-bottom: 64px

③ Price + deliverables — single large dark card
  background: #111111 · border: 1px solid #242424 · border-radius: 12px
  padding: 48px

  Top row:
    Left:  "$700"   — 56px · 300 · #FFFFFF · letter-spacing -0.03em
    Right: "One-time. Delivered in 10 days." — 14px · 400 · #707070

  Divider: border-top 1px solid #242424, margin: 32px 0

  Deliverables grid (2 columns, separated by dividers):
  
  ┌──────────────────────────┬──────────────────────────┐
  │ Logo & brand mark        │ Brand identity kit        │
  │ Primary logo, alternate  │ Color palette, type       │
  │ versions, monogram.      │ system, and usage guide.  │
  │ All formats.             │                           │
  ├──────────────────────────┼──────────────────────────┤
  │ Digital mockups          │ Website                   │
  │ Business card, social    │ Your choice: single       │
  │ profile, email signature.│ landing page or 5 pages.  │
  ├──────────────────────────┼──────────────────────────┤
  │ Source files             │ One revision round        │
  │ All design files.        │ Notes incorporated within │
  │ You own everything.      │ the 10-day window.        │
  └──────────────────────────┴──────────────────────────┘

  Cell styling:
    padding: 24px 0
    title: 15px · 500 · #FFFFFF
    desc: 13px · 400 · #707070 · line-height 1.6 · margin-top 4px
    left-column cells: padding-right 32px · border-right: 1px solid #242424
    right-column cells: padding-left 32px
    all cells: border-bottom: 1px solid #242424
    last row: no border-bottom

  Add-on row (below grid, inside card):
    border-top: 1px solid #242424 · padding-top: 24px · margin-top: 8px
    display: flex · justify-content: space-between · align-items: center

    Left text (13px · 400 · #707070 · max-width 480px):
      "Need more pages, custom illustrations, or ongoing support?
      Add-ons available at a transparent per-item rate — ask us in the form."

    Right: ghost pill button — "Start a project →" → Google Form
```

---

### Section 4 — Timeline

**Anchor:** `id="timeline"`

```
LAYOUT:
  padding: 96px 40px · max-width 1120px · margin: 0 auto
  border-top: 1px solid #242424

CONTENT:

① Eyebrow: "HOW IT WORKS"

② Headline:
  "Ten days.
  Every step visible."
  font: 44px · 300 · #FFFFFF · letter-spacing -0.025em · max-width 400px
  margin-bottom: 64px

③ 5-column timeline grid
  display: grid · grid-template-columns: repeat(5, 1fr)
  border: 1px solid #242424 · border-radius: 12px · overflow: hidden

  Each column (phase card):
    padding: 28px 24px
    border-right: 1px solid #242424
    last column: border-right: none

    Day label:    11px · 500 · uppercase · #505050 · letter-spacing 0.1em · margin-bottom 12px
    Phase title:  15px · 500 · #FFFFFF · margin-bottom 16px
    Task list:    13px · 400 · #707070 · line-height 1.7
                  Each task on own line, preceded by "—" in #303030

FIVE PHASES:

Phase 1 — Day 1–2 — "Brief & direction"
  — Fill out the questionnaire
  — We review your brief
  — Creative direction is set
  — Project confirmed in 24h

Phase 2 — Day 3–4 — "Brand identity"
  — AI generates directions
  — Expert refines and selects
  — Logo concepts drafted
  — Color and type system set

Phase 3 — Day 5–6 — "Your feedback"
  — Brand presented to you
  — One round of your notes
  — Revisions incorporated
  — Brand locked

Phase 4 — Day 7–9 — "Website build"
  — Site designed to brand
  — Content placed and refined
  — Mobile-ready
  — Preview link shared

Phase 5 — Day 10 — "Delivery"
  — All files handed over
  — Site ready to publish
  — Brand guidelines PDF
  — Done.

MOBILE: timeline becomes horizontally scrollable
  each card: min-width 200px · display flex in row · overflow-x auto
  hide scrollbar: scrollbar-width none
```

---

### Section 5 — Work / Case Studies

**Anchor:** `id="work"`

```
LAYOUT:
  padding: 96px 40px · max-width 1120px · margin: 0 auto
  border-top: 1px solid #242424

CONTENT:

① Eyebrow: "PAST WORK"

② Headline:
  "Startups we've launched."
  font: 44px · 300 · #FFFFFF · letter-spacing -0.025em
  margin-bottom: 48px

③ Card grid
  display: grid
  grid-template-columns: repeat(3, 1fr) [desktop]
  grid-template-columns: 1fr [mobile]
  gap: 16px

[see Component 5.4 for full card spec]

THREE PLACEHOLDER PROJECTS:

Card 1:
  Image:    abstract dark geometric placeholder
  Tag:      "FINTECH · LANDING PAGE"
  Title:    "Volta"
  Desc:     "A payments tool for freelancers. Needed a brand that felt
             trustworthy but approachable — delivered in 9 days."
  Meta:     "Logo + brand kit  ·  Single landing page"

Card 2:
  Image:    abstract typographic placeholder
  Tag:      "SAAS · FIVE-PAGE SITE"
  Title:    "Archiv"
  Desc:     "Document management for small teams, positioning against
             bloated enterprise tools. Minimal and precise."
  Meta:     "Full brand identity  ·  Five-page site"

Card 3:
  Image:    abstract texture placeholder
  Tag:      "D2C · LANDING PAGE"
  Title:    "Grdn"
  Desc:     "A subscription box for home gardeners. Warm but modern —
             a conversion-focused landing page."
  Meta:     "Logo + mockups  ·  Landing page"

Note: Replace these with real projects as they are completed.
Image area background until real images exist: #1A1A1A
```

---

### Section 6 — About

**Anchor:** `id="about"`

```
LAYOUT:
  padding: 96px 40px · max-width 1120px · margin: 0 auto
  border-top: 1px solid #242424

CONTENT:

① Eyebrow: "ABOUT"

② Headline:
  "AI builds it.
  Experts direct it."
  font: 44px · 300 · #FFFFFF · letter-spacing -0.025em · line-height 1.1
  max-width: 480px · margin-bottom: 48px

③ Two-column layout (desktop): left 50% · right 50% · gap 64px

  LEFT COLUMN — What we are:
    Paragraph (16px · 400 · #C0C0C0 · line-height 1.75 · max-width 420px):

    "Draft. is a fast-turnaround branding and web design studio
    built for early-stage startups.

    We combine AI-generated creative directions with expert
    oversight to deliver a complete brand identity and website
    in ten days — for a fixed price of $700.

    You fill out a questionnaire. We handle everything else."

  RIGHT COLUMN — Three stat/fact blocks, stacked:

    Block 1:
      Number:  "10"  — 40px · 300 · #FFFFFF
      Label:   "Days from brief to delivery" — 13px · 400 · #707070
      border-bottom: 1px solid #242424 · padding-bottom: 24px · margin-bottom: 24px

    Block 2:
      Number:  "$700"  — 40px · 300 · #FFFFFF
      Label:   "Flat rate, no hidden fees" — 13px · 400 · #707070
      border-bottom: 1px solid #242424 · padding-bottom: 24px · margin-bottom: 24px

    Block 3:
      Number:  "1"  — 40px · 300 · #FFFFFF
      Label:   "Questionnaire to get started" — 13px · 400 · #707070

④ Subtle note below both columns (margin-top: 48px):
  "We are a small team. We take on a limited number of projects
  each month to ensure quality." — 14px · 400 · #505050

MOBILE:
  Single column. Left column first, right column stats below.
```

---

### Section 7 — Footer

**Anchor:** `id="footer"`

```
LAYOUT:
  background: #0A0A0A
  border-top: 1px solid #242424
  padding: 32px 40px

CONTENT:
  max-width: 1120px · margin: 0 auto
  display: flex · justify-content: space-between · align-items: center

  Left:
    "Draft." — 14px · 500 · #FFFFFF

  Right:
    Links: hello@draft.co · Instagram · Twitter
    font: 13px · 400 · #505050
    hover: color #C0C0C0 · transition 150ms
    gap: 24px

  Below row (margin-top: 24px, border-top: 1px solid #1A1A1A, padding-top: 20px):
    "© 2025 Draft. All rights reserved." — 12px · 400 · #404040

MOBILE:
  flex-direction: column · align-items: flex-start · gap: 20px
```

---

## 10. Technical Implementation Notes

### Font loading
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
```

### CSS base reset
```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: 'Söhne', 'Inter', ui-sans-serif, -apple-system, sans-serif;
  background: #0A0A0A;
  color: #E8E8E8;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

### Smooth scroll to sections
```js
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    document.querySelector(a.getAttribute('href'))
      ?.scrollIntoView({ behavior: 'smooth' });
  });
});
```

### Textarea auto-grow
```js
const textarea = document.querySelector('textarea');
textarea.addEventListener('input', () => {
  textarea.style.height = 'auto';
  textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
});
```

### Submit button active state
```js
textarea.addEventListener('input', () => {
  submitBtn.disabled = textarea.value.trim().length === 0;
});
```

### Submit action
```js
const FORM_URL = 'https://YOUR_GOOGLE_FORM_URL_HERE';
submitBtn.addEventListener('click', () => {
  const text = textarea.value.trim();
  if (!text) return;
  const url = `${FORM_URL}?entry.FIELD_ID=${encodeURIComponent(text)}`;
  window.open(url, '_blank');
});
```

### Speech recognition (mic button)
```js
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-US';

  micBtn.addEventListener('click', () => {
    if (micBtn.classList.contains('recording')) {
      recognition.stop();
      micBtn.classList.remove('recording');
    } else {
      recognition.start();
      micBtn.classList.add('recording');
    }
  });

  recognition.onresult = (e) => {
    textarea.value = e.results[0][0].transcript;
    textarea.dispatchEvent(new Event('input'));
    micBtn.classList.remove('recording');
  };

  recognition.onerror = () => micBtn.classList.remove('recording');
} else {
  micBtn.title = 'Voice input not supported in this browser';
  micBtn.disabled = true;
}
```

---

## 11. Mobile Breakpoints

```css
/* Tablet */
@media (max-width: 900px) {
  .timeline-grid { display: flex; overflow-x: auto; scrollbar-width: none; }
  .timeline-col  { min-width: 200px; flex-shrink: 0; }
}

/* Mobile */
@media (max-width: 640px) {
  .hero-tagline  { font-size: 36px; }
  .section-headline { font-size: 32px; }
  .case-grid     { grid-template-columns: 1fr; }
  .deliverables-grid { grid-template-columns: 1fr; }
  .deliverable-item:nth-child(odd) { padding-right: 0; border-right: none; }
  .deliverable-item:nth-child(even) { padding-left: 0; }
  .nav-cta       { display: none; } /* hidden — hamburger handles it */
  section        { padding: 64px 20px; }
  .price-card    { padding: 28px 20px; }
  .footer-inner  { flex-direction: column; align-items: flex-start; gap: 20px; }
}
```

---

## 12. Anti-Patterns — Hard Nos

- ❌ Any color that isn't black, white, or gray
- ❌ Gradients on UI elements
- ❌ Box-shadows
- ❌ Font weight 600, 700, or 900 anywhere
- ❌ Italic text
- ❌ Mixed typefaces or a serif font
- ❌ Centered body text longer than 2 lines
- ❌ Pill shape on anything except CTA buttons
- ❌ Emoji in the UI
- ❌ Section background colors that don't bleed full width
- ❌ Card borders thicker than 1px
- ❌ Looping animations or auto-playing content
- ❌ Testimonial carousels or sliders
- ❌ Icons beside section headlines (icons = decoration here)
- ❌ Bold text (`<strong>`) inside paragraphs
- ❌ Hover effects that use scale transform (no zooming)
- ❌ Any text that sells rather than describes

