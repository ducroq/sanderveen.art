# Runbook — sanderveen.art

Operational guide for developing and maintaining the sanderveen.art Hugo site.

## Principles

1. **Inquiry over commerce** — the site invites visitors to contact Sander directly; never add carts, checkout flows, or displayed prices
2. **Dutch is primary** — NL content lives at root (`/schilderijen/`), EN lives under `/en/`; Dutch is the source of truth
3. **Accessibility** — WCAG AA minimum; semantic HTML, focus traps in lightbox, keyboard navigation, sufficient contrast
4. **Performance** — no JS frameworks, no CDN, self-hosted fonts, Hugo image processing for responsive images
5. **Simplicity** — custom theme from scratch, no npm, no external Hugo themes

## Local Development

### Prerequisites
- Hugo v0.147.0+ (Chocolatey: `choco install hugo-extended` or `choco install hugo`)
- Git
- Python 3.x (only for scraping/content-generation scripts)

### Setup
```bash
git clone https://github.com/ducroq/sanderveen.art.git
cd sanderveen.art
hugo server -D
```

### Running Locally
```bash
# Dev server with drafts, hot reload on http://localhost:1313/
hugo server -D

# Build to ./public/
hugo --minify
```

**Note**: Local Windows Hugo (non-extended) cannot produce WebP images. This is expected — CI uses extended Hugo. See `memory/gotcha-log.md` for details.

## Deployment

The site deploys to **GitHub Pages** automatically on push to `main`.

### How It Works
1. Push to `main` triggers `.github/workflows/hugo.yml`
2. CI installs **Hugo Extended** v0.147.0 (required for image processing / WebP)
3. `actions/configure-pages@v5` provides the correct `baseURL` (overrides `hugo.toml`)
4. Hugo builds with `--minify --baseURL "$BASE_URL/"`
5. Artifact uploaded and deployed to GitHub Pages

### Manual Deploy
Not needed — everything goes through CI. If you must test the CI locally:
```bash
hugo --minify --baseURL "https://ducroq.github.io/sanderveen.art/"
```

## Adding a New Painting

This is the most common content operation. Follow these steps:

### 1. Add the Image
Place the painting image in `assets/images/paintings/`:
```
assets/images/paintings/my-painting-name.jpg
```
Use lowercase, hyphenated filenames. Prefer high-resolution source files — Hugo generates responsive sizes.

### 2. Create NL Content
Create `content/schilderijen/my-painting-name.md`:
```yaml
---
title: "Titel van het Schilderij"
translationKey: "my-painting-name"
image: "images/paintings/my-painting-name.jpg"
date: 2024-01-01
categories: ["abstract"]       # or "magisch-realisme"
featured: false                # true for homepage display (max ~6)
dimensions: "100 × 80 cm"
medium: "Olieverf op doek"
year: "2024"
draft: false
---

Beschrijving van het schilderij.
```

### 3. Create EN Content
Create `content/en/paintings/my-painting-name.md`:
```yaml
---
title: "Painting Title"
translationKey: "my-painting-name"    # must match NL
type: "schilderijen"                  # reuse NL layouts
image: "images/paintings/my-painting-name.jpg"
date: 2024-01-01
categories: ["abstract"]
featured: false
dimensions: "100 × 80 cm"
medium: "Oil on canvas"
year: "2024"
draft: false
---

Description of the painting.
```

### Key Points
- `translationKey` **must match** between NL and EN versions
- EN files need `type: "schilderijen"` to reuse the Dutch layout templates
- `image` path is relative to `assets/` (Hugo resource pipeline)
- Categories: `abstract` or `magisch-realisme`
- Set `featured: true` on ≤6 paintings for homepage display

## Adding a Workshop

1. Create NL file in `content/workshops/my-workshop.md`:
```yaml
---
title: "Workshop Titel"
translationKey: "workshop-my-workshop"
type: "workshops"
workshop_date: "Zaterdagen 10:00–12:00"
location: "Atelier Sander Veen, Eenvoudlaan 6A, Veenendaal"
price: "40 per les"
weight: 60
---
```
2. Create EN file in `content/en/workshops/my-workshop.md` with same `translationKey` and `type: "workshops"`

## Adding an Exhibition

1. Place photos in `assets/images/exhibitions/`
2. Create NL file in `content/exposities/my-exhibition.md`:
```yaml
---
title: "Expositie Titel"
translationKey: "expo-my-exhibition"
type: "exposities"
date: 2025-01-01
start_date: "1 januari 2025"
end_date: "5 januari 2025"
location: "Locatie"
image: "images/exhibitions/my-exhibition-1.jpg"
gallery:
  - "images/exhibitions/my-exhibition-2.jpg"
  - "images/exhibitions/my-exhibition-3.jpg"
weight: 60
---
```
3. Create EN file in `content/en/exhibitions/my-exhibition.md` with same `translationKey` and `type: "exposities"`
4. The `image` field is the hero image; `gallery` is an array of additional photos rendered as a grid

## Adding a New Section

To add a section beyond paintings, workshops, and exhibitions:

1. Add content in `content/<section>/` (NL) and `content/en/<section>/` (EN)
2. Create layouts if the default `_default/list.html` + `_default/single.html` aren't sufficient
3. Add menu entries in `hugo.toml` under both `[languages.nl.menus.main]` and `[languages.en.menus.main]`
4. Add any new i18n keys to both `i18n/nl.toml` and `i18n/en.toml`

## Common Problems

| Problem | Cause | Fix |
|---------|-------|-----|
| Fonts not loading on GH Pages | CSS @font-face paths wrong | Use `../fonts/` (relative to CSS output path) |
| No WebP in local build | Non-extended Hugo on Windows | Expected; CI uses extended Hugo |
| Build fails in CI, works locally | Hugo version mismatch or missing extended | Check `HUGO_VERSION` in workflow matches local |
| baseURL wrong in production | Hardcoded in `hugo.toml` | CI overrides via `configure-pages@v5` — don't hardcode the GH Pages URL |
| i18n key shows `[i18n] ...` | Missing key in one language file | Add the key to both `i18n/nl.toml` and `i18n/en.toml` |
| EN painting uses wrong layout | Missing `type: "schilderijen"` | Add `type: "schilderijen"` to EN front matter |
| Language switcher 404s | `translationKey` mismatch | Ensure both NL and EN files share the same `translationKey` |
| Images not processed | Image path doesn't resolve | Path must be relative to `assets/`, e.g. `images/paintings/foo.jpg` |

## Documentation Practices

| Document | Location | Purpose | When to update |
|----------|----------|---------|----------------|
| `CLAUDE.md` | Project root | Quick orientation, architecture, constraints | Architecture changes, new key paths |
| `docs/RUNBOOK.md` | `docs/` | How-to procedures, troubleshooting | New workflows, new problems solved |
| `memory/MEMORY.md` | Claude memory | Session-persistent state, discoveries | New findings, decisions, status changes |
| `memory/gotcha-log.md` | Claude memory | Pitfalls and surprises | Every time you hit an unexpected issue |
