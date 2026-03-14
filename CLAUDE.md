# sanderveen.art — Hugo Portfolio Site

Portfolio website for painter **Sander Veen**. Bilingual (Dutch primary, English at `/en/`). Inquiry-based — visitors contact the artist to purchase, no cart or prices shown.

Built with Hugo, custom theme from scratch. Deployed to **GitHub Pages** via Actions.

Live: https://ducroq.github.io/sanderveen.art/

## Before You Start

| If you are…                        | Read first                          |
|------------------------------------|-------------------------------------|
| Adding/editing a painting          | `docs/RUNBOOK.md` § Adding a Painting |
| Changing CSS or layout             | Architecture below + `assets/css/`  |
| Working on deployment or CI        | `docs/RUNBOOK.md` § Deployment      |
| Adding a new section               | `docs/RUNBOOK.md` § Adding a Section |
| Debugging a build failure          | `docs/RUNBOOK.md` § Common Problems |
| Touching i18n strings              | `i18n/nl.toml`, `i18n/en.toml`     |
| CMS / content management           | `docs/CMS-HANDLEIDING.md`          |

## Hard Constraints

1. **No webshop, no prices** — inquiry-based only (mailto contact form)
2. **Bilingual parity** — every NL page needs an EN counterpart (linked via `translationKey`)
3. **No external dependencies** — no npm, no CDN, no JS frameworks; self-hosted fonts (exception: Sveltia CMS loaded from unpkg)
4. **Extended Hugo in CI** — local Windows build is non-extended (no WebP); CI uses `hugo_extended`
5. **GitHub Pages deployment** — no Netlify, no Vercel
6. **Privacy** — Eenvoudlaan 6A is also Sander's home address; only show full address in workshop pages, not on contact page

## Architecture

```
sanderveen.art/
├── hugo.toml              # Site config, languages, menus, params
├── assets/
│   ├── css/               # 8 CSS files → Hugo Pipes concat+minify+fingerprint
│   │   ├── _reset.css, _typography.css, _layout.css, _navigation.css
│   │   ├── _gallery.css, _components.css, _footer.css, _utilities.css
│   └── images/            # Source paintings (Hugo image processing)
│       ├── paintings/     # Full-size painting images
│       ├── exhibitions/   # Exhibition photos
│       └── workshops/     # Workshop photos
├── content/
│   ├── schilderijen/      # NL painting pages (38 .md files)
│   ├── over/              # NL about
│   ├── contact/           # NL contact
│   ├── workshops/         # NL workshops (5 workshops)
│   ├── exposities/        # NL exhibitions (5 exhibitions)
│   └── en/                # EN mirror (paintings/, about/, contact/, workshops/, exhibitions/)
├── i18n/                  # nl.toml, en.toml — all UI strings
├── layouts/
│   ├── _default/          # baseof.html, list.html, single.html
│   ├── schilderijen/      # Painting-specific layouts (reused by EN via type)
│   ├── workshops/         # Workshop list + single layouts
│   ├── exposities/        # Exhibition list + single layouts (with gallery)
│   ├── contact/           # Contact page layout
│   ├── partials/          # head, header, footer, painting-card, lightbox, etc.
│   └── index.html         # Homepage template
├── static/fonts/          # Self-hosted woff2 (Playfair Display 700, Inter 400/500/600)
├── static/admin/          # Sveltia CMS (index.html + config.yml)
├── scripts/               # Python: scrape.py, generate_content.py, cleanup_content.py, download_exhibitions.py, md_to_pdf.py
├── docs/
│   ├── CMS-HANDLEIDING.md           # Dutch CMS user guide (source)
│   ├── CMS-Handleiding-SanderVeen.pdf  # PDF version for Sander
│   └── RUNBOOK.md                   # Operational runbook
└── .github/workflows/hugo.yml  # CI: build with extended Hugo, deploy to GH Pages
```

### How Pieces Connect

- **CSS**: 8 partials in `assets/css/` concatenated by Hugo Pipes in `layouts/partials/head.html`
- **Images**: stored in `assets/images/`, processed with Hugo's `Fit`/`Fill`/`Resize` in templates
- **Bilingual**: EN content in `content/en/`, separated via Hugo module mounts (`excludeFiles` in `hugo.toml`); linked to NL via `translationKey` in front matter; EN painting pages use `type: "schilderijen"` to reuse NL layouts; EN workshops use `type: "workshops"`, EN exhibitions use `type: "exposities"`
- **Logo**: `assets/images/logo.png` (transparent PNG), used in header and homepage hero; `filter: invert(1)` for dark mode
- **Fonts**: woff2 files in `static/fonts/`, referenced with `../fonts/` in CSS @font-face (required for GH Pages subpath)
- **Contact**: mailto link, no server-side form processing
- **CMS**: Sveltia CMS at `static/admin/`, configured in `static/admin/config.yml`, uses GitHub PAT auth
- **Theme**: dark/light toggle via `body.dark` class, persisted in localStorage

## Key Paths

| Path | Purpose |
|------|---------|
| `hugo.toml` | Site config, languages, menus |
| `layouts/partials/head.html` | CSS pipeline, meta tags, font preloads |
| `layouts/partials/header.html` | Navigation, logo, language switcher |
| `layouts/schilderijen/single.html` | Individual painting page |
| `layouts/schilderijen/list.html` | Gallery grid |
| `layouts/partials/painting-card.html` | Gallery card component |
| `layouts/index.html` | Homepage |
| `assets/css/_gallery.css` | Masonry layout, lightbox styles |
| `assets/css/_layout.css` | Page structure, responsive breakpoints |
| `i18n/nl.toml` | Dutch UI strings |
| `i18n/en.toml` | English UI strings |
| `content/schilderijen/` | Dutch painting content (38 pages) |
| `content/en/paintings/` | English painting content |
| `content/workshops/` | Dutch workshop content (5 workshops) |
| `content/en/workshops/` | English workshop content |
| `content/exposities/` | Dutch exhibition content (5 exhibitions) |
| `content/en/exhibitions/` | English exhibition content |
| `layouts/workshops/single.html` | Workshop detail page |
| `layouts/exposities/single.html` | Exhibition detail page (with gallery) |
| `static/fonts/` | Self-hosted web fonts |
| `static/admin/config.yml` | Sveltia CMS collection config |
| `assets/images/logo.png` | Site logo (transparent PNG) |
| `docs/CMS-HANDLEIDING.md` | Dutch CMS user guide (source) |
| `docs/CMS-Handleiding-SanderVeen.pdf` | PDF version for Sander |
| `scripts/md_to_pdf.py` | Markdown to PDF converter |
| `.github/workflows/hugo.yml` | CI/CD pipeline |

## How to Work Here

```bash
# Local dev server (hot reload)
hugo server -D

# Production build (local, no WebP without extended Hugo)
hugo --minify

# CI build (what GitHub Actions runs)
hugo --minify --baseURL "$BASE_URL/"

# Check Hugo version
hugo version
```

## Design Tokens

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--color-bg` | `#FAF8F5` | `#1A1A1A` | Page background |
| `--color-text` | `#1A1A1A` | `#F0EDE8` | Body text |
| `--color-gold` | `#B8860B` | `#D4A843` | Accent, links, buttons |
| `--color-text-muted` | `#5C5652` | `#A89F96` | Secondary text |
| `--color-white` | `#FFFFFF` | `#2A2725` | Cards, inputs |

Dark theme activated via `body.dark` class, toggled with 🌙 button in header. Sander to choose final preference.
