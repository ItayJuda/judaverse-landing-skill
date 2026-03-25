---
name: landing-builder
description: Use this skill for any frontend landing page or website build request. Triggers on: "build a site", "landing page", "בנה אתר", "דף נחיתה", "website for my business", or any web creation task in Claude Code. Uses 21st.dev MCP for premium components + design data for intelligent style decisions.
---

You are building a premium landing page. Follow this workflow exactly.

## Step 1 — Gather requirements (ask if missing)

- Business name and type
- Language (default: Hebrew)
- Style preference: `dark-minimal` / `glassmorphism` / `brutalist` / `soft-light` / `neon-dark` / `editorial`
- Animation: `particles` / `aurora` / `beam` / `none`
- Stack: `nextjs` (default) / `html` / `react`

---

## Step 2 — Search design data

Run these commands and read every result before writing any code:

```bash
python3 scripts/search.py "<business_type> <style>" --domain layout
python3 scripts/search.py "<animation_choice>" --domain animation
python3 scripts/search.py "<stack>" --domain stack
```

Apply the results to **all** design decisions — colors, fonts, section order, headline formula, animation implementation.

Also use 21st.dev magic MCP to search for ready-made components before building from scratch.
Search 21st for: hero section, navbar, services grid, marquee ticker, stats row, CTA section, footer.
If a component is found in 21st - use it directly.
Build from scratch only if the component is not available in 21st.

---

## Step 3 — Pull components from 21st.dev MCP

Search 21st.dev for: `hero`, `services grid`, `marquee`, `stats`, `cta`, `footer`.

Use what you find. Build from scratch only if a component is not available.

---

## Step 4 — Build the page with this structure

1. **Navbar** — logo left, links center, CTA button right
2. **Hero** — bold headline, subheadline, 2 CTA buttons, availability badge (green pulsing dot), animated background
3. **Marquee** — scrolling services ticker
4. **Services** — 6 cards: number, icon, name, description
5. **Stats** — 4 numbers relevant to business type
6. **CTA** — strong headline + single button
7. **Footer** — logo + copyright

> **Note:** For landing pages: always include a marquee ticker between hero and services,
> and an availability badge (green pulsing dot + 'Available for New Projects' text) in the hero section.

---

## Step 5 — Design rules (strict)

- Generate all copy based on business type — **no placeholder text**
- Background and colors from data search results
- Fonts from data search results
- No generic AI aesthetics (no blue gradients, no San Francisco/Inter as the only font, no shadcn default look)
- After building: run `npm run dev` and confirm it works before declaring done

---

## Anti-Patterns

- Never use generic AI aesthetics (purple gradients on white, Space Grotesk as default font)
- Never build a landing page without an animated hero background (particles, aurora, beam, or orbs)
- Never skip the marquee ticker between hero and first content section
