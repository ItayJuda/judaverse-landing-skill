# judaverse-landing-skill

A Claude Code skill for building premium landing pages using 21st.dev MCP components and data-driven design decisions.

---

## Project Structure

```
judaverse-landing-skill/
├── CLAUDE.md                          ← you are here
├── README.md                          ← GitHub overview
├── .claude/
│   └── skills/
│       └── landing-builder/
│           └── SKILL.md               ← the skill Claude reads and follows
├── scripts/
│   └── search.py                      ← BM25 search over design data
└── data/
    ├── animations.csv                  ← animation options + implementation hints
    ├── components.csv                  ← section components + Tailwind hints
    ├── layouts.csv                     ← page layouts by business type
    └── stacks.csv                      ← framework setup instructions
```

---

## Search Command

The search script uses BM25 ranking to find the most relevant design data for any query.

```bash
# Search by domain
python3 scripts/search.py "dark AI agency"        --domain layout
python3 scripts/search.py "particles"             --domain animation
python3 scripts/search.py "hero section dark"     --domain component
python3 scripts/search.py "nextjs tailwind"       --domain stack

# Auto-detect domain (omit --domain)
python3 scripts/search.py "SaaS product dark"

# Return more results
python3 scripts/search.py "creative studio" --domain layout -n 5
```

### Domains

| Domain      | File                | What it contains                          |
|-------------|---------------------|-------------------------------------------|
| `layout`    | `layouts.csv`       | Page structures by business type          |
| `animation` | `animations.csv`    | Background animation options + code hints |
| `component` | `components.csv`    | Section specs and Tailwind class hints    |
| `stack`     | `stacks.csv`        | Framework setup commands and file paths   |

---

## Data Format

All CSV files use `|` as the delimiter. Never use commas inside values.

To add a new layout:

```
id|name|best_for|sections_order|conversion_pattern|headline_style
my-layout|My Layout|startups; B2B|hero,services,cta,footer|Value-first then urgency|Direct claim - "X solves Y"
```

---

## Skill Installation

Copy `.claude/skills/landing-builder/` into your project's `.claude/skills/` directory.

**Requirement:** 21st.dev MCP must be configured in Claude Code settings.

---

## How the Skill Works

When activated, the skill runs a 5-step workflow:

1. Gather requirements (business type, language, style, animation, stack)
2. Run `search.py` to pull relevant layouts, animations, and stack instructions
3. Fetch premium components from 21st.dev MCP
4. Build the full page (navbar → hero → marquee → services → stats → CTA → footer)
5. Enforce design rules: real copy, no placeholders, no generic AI look
