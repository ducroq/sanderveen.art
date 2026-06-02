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

**Note**: Local Windows Hugo (non-extended) cannot produce WebP images. This is expected — CI uses extended Hugo.

## Deployment

The site deploys to **GitHub Pages** automatically on push to `main`.

### How It Works
1. Push to `main` triggers `.github/workflows/hugo.yml`
2. CI downloads **Hugo Extended** v0.147.0 (required for image processing / WebP) and verifies its SHA-256 against the upstream `hugo_<VERSION>_checksums.txt` before `dpkg -i` — fails closed on a 404 or hash mismatch
3. `actions/configure-pages@v6` provides the correct `baseURL` (overrides `hugo.toml`)
4. Hugo builds with `--minify --baseURL "$BASE_URL/"`. Painting hero images are generated at 600/1200/2000 widths for srcset, so the first build after adding paintings can take noticeably longer (~10× a no-image-change build)
5. Artifact uploaded and deployed to GitHub Pages

### Manual Deploy
Not needed — everything goes through CI. If you must test the CI locally:
```bash
hugo --minify --baseURL "https://ducroq.github.io/sanderveen.art/"
```

## Adding a New Painting

This is the most common content operation. Follow these steps:

### 1. Add the Image
Place the painting image directly in `assets/images/paintings/`:
```
assets/images/paintings/my-painting-name.jpg
```
Use lowercase, hyphenated filenames (no subfolders — the CMS image widget expects a flat folder; category is set in front matter). Prefer high-resolution source files — Hugo generates responsive sizes.

### 2. Create NL Content
Create `content/schilderijen/my-painting-name.md`:
```yaml
---
title: "Titel van het Schilderij"
translationKey: "my-painting-name"
image: "images/paintings/my-painting-name.jpg"
date: 2024-01-01
type: "schilderijen"
category: "Abstract"           # or "Surrealistisch"
status: "available"            # available, sold, not-for-sale
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
image: "images/paintings/my-painting-name.jpg"
date: 2024-01-01
type: "schilderijen"                  # reuse NL layouts
category: "Abstract"                  # or "Surrealist"
status: "available"
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
- Category: `"Abstract"` or `"Surrealistisch"` (NL), `"Abstract"` or `"Surrealist"` (EN)
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
5. Optional `videos:` list (same scalar-string shape as `gallery:`) renders short clips between the body and the gallery. See § Adding or Replacing a Video.

## Adding or Replacing a Video

Videos live in `static/videos/` and are served as-is (no Hugo image pipeline). The site uses native HTML5 `<video>` controls — no JS players.

### From the CMS (Sander's path)
- **Studio video** on the About page: Over mij → "Atelier video" field
- **Exhibition videos**: Exposities → expo entry → "Video's" list → Add
- Sander's step-by-step is in `docs/CMS-HANDLEIDING.md` § "Een video toevoegen of vervangen" (includes WhatsApp-shrink tip, Media Library trap, and slug-rename caveat)

### From git (Jeroen's path)
1. Re-encode or remux with ffmpeg first. WhatsApp clips that are already ≤5 MB and H.264/AAC just need a remux for faststart:
   ```bash
   ffmpeg -i input.mp4 -c copy -movflags +faststart -y static/videos/<slug>.mp4
   ```
   Larger or non-web-friendly files: re-encode at CRF 26 + faststart:
   ```bash
   ffmpeg -i input.mp4 -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 96k -movflags +faststart -y static/videos/<slug>.mp4
   ```
2. Generate a poster thumbnail (the partial picks it up automatically if it sits next to the mp4):
   ```bash
   ffmpeg -ss 1 -i static/videos/<slug>.mp4 -frames:v 1 -q:v 3 -y static/videos/<slug>.jpg
   ```
3. Reference the file in front matter:
   - About: `video: "videos/<slug>.mp4"` in `content/over/_index.md` and `content/en/about/_index.md`
   - Exhibition: append to a `videos:` list (same scalar-string shape as `gallery:`) in both the NL and EN entry
4. Run `python scripts/validate_content.py` to confirm the path resolves and doesn't escape `static/`.

### Naming rules
- `.mp4` only (the CMS pattern is `^/?videos/[a-z0-9][a-z0-9-]*\.mp4$`). `.webm` would require pattern relaxation.
- Lowercase letters, digits, hyphens. No spaces, no uppercase, no underscores. Same as the image-widget rules; the CMS error message calls out uppercase/underscore explicitly.

### What renders
- `layouts/partials/video-embed.html` is the single source of truth. Auto-derives a poster path from the src, adds aria-label from the optional `title` param, refuses any path that doesn't start with `videos/`.
- Single-video exhibition pages get a `.exhibition-videos--single` modifier class so the portrait clip is centred at its natural width instead of stretched across an auto-fill grid.

## Adding a New Section

To add a section beyond paintings, workshops, and exhibitions:

1. Add content in `content/<section>/` (NL) and `content/en/<section>/` (EN)
2. Create layouts if the default `_default/list.html` + `_default/single.html` aren't sufficient
3. Add menu entries in `hugo.toml` under both `[languages.nl.menus.main]` and `[languages.en.menus.main]`
4. Add any new i18n keys to both `i18n/nl.toml` and `i18n/en.toml`

## Content Management (CMS)

Sander can manage content via the Sveltia CMS admin panel at `/admin/`.

### How It Works
- **Sveltia CMS** loads from `static/admin/index.html` (single `<script>` tag), pinned to a specific version with a SHA-384 SRI hash. To upgrade, follow the inline `curl + openssl` recipe in that file
- **Config** in `static/admin/config.yml` defines all content collections
- **Auth**: GitHub Personal Access Token (fine-grained, scoped to this repo only, contents read+write)
- On publish, Sveltia commits directly to `main` → triggers GitHub Actions deploy

### Media folder configuration (read this before editing `config.yml`)
- **Global**: `media_folder: assets/images/paintings`, `public_folder: images/paintings` — sets the default for standalone Media Library uploads. Most uploads are paintings, so this routes them correctly by default.
- **Collection-level overrides** are the canonical way to redirect a whole collection's uploads. `exposities` and `exhibitions-en` set `media_folder: "/assets/images/exhibitions"` + `public_folder: "images/exhibitions"` at the collection level, so the Hoofdafbeelding *and* Galerijtje fields both land under `assets/images/exhibitions/`.
- **Field-level overrides** are reserved for fields whose target differs from their collection — e.g. the `videos` `file` widget in `exposities` overrides to `/static/videos`. **Heads up:** Sveltia 0.165 silently ignores a field-level `media_folder` on a *top-level* `image` widget — the file lands in the global default and the regex pattern fires a misleading "filename invalid" error. Field-level overrides do work on nested-list `image` widgets and on `file` widgets. Prefer collection-level for top-level images.
- **Whenever you do set a field-level `media_folder`, always set the matching `public_folder` too.** Without the pair, the CMS writes a broken absolute path (`/assets/images/...`) into content files.
- Painting image fields enforce a filename `pattern` (`^/?images/paintings/[a-z0-9][a-z0-9-]*\.(jpe?g|png|webp)$`) — the form blocks saves with spaces, capitals, or punctuation in the filename. The optional leading `/?` is required: Sveltia's image widget validates the form-displayed value (with leading slash), not the saved value (without). All existing painting images conform; new uploads must too.

### Before committing changes to `static/admin/config.yml`
The CMS form is a different runtime than the saved markdown — patterns and hints can pass code review but still break for the user. **Exercise the form before committing**, either by running `hugo server -D` and using `/admin/` in a browser, or by invoking the local `sander-cms-tester` agent at `.claude/agents/sander-cms-tester.md` (gitignored), which simulates the workflow and runs the validation regexes against both the saved-value form and the form-displayed-value form. Two consecutive CMS regressions in 2026-05 (a6e3e1b deploy break, a20afad pattern false-negative) reached the client because this step was skipped.

### Collections
- Schilderijen / Paintings (NL + EN)
- Workshops (NL + EN)
- Exposities / Exhibitions (NL + EN)
- Over mij / About (NL + EN)

### If the PAT expires or is revoked
Sander can generate a new token himself — see `docs/CMS-HANDLEIDING.md` § "Token verlopen?".

Alternatively:
1. Generate a new fine-grained PAT at https://github.com/settings/tokens?type=beta
2. Scope: repository `ducroq/sanderveen.art`, permission Contents read+write
3. Send the new token to Sander via Signal

### User guide
See `docs/CMS-HANDLEIDING.md` (Dutch) for Sander's step-by-step instructions.
PDF version: `docs/CMS-Handleiding-SanderVeen.pdf` (regenerate with `python scripts/md_to_pdf.py`).

## Content Validation

Run `python scripts/validate_content.py` to check all content files against the CMS schema. This catches issues before they reach production.

### What It Checks
- **Front matter schema** — required fields present and correctly typed
- **Enum validation** — status (`available`/`sold`/`not-for-sale`), category values
- **Bilingual parity** — every NL file has an EN counterpart with matching `translationKey`
- **Cross-language consistency** — status, featured, image, and category match between NL/EN
- **Image paths** — referenced images exist in `assets/images/`
- **Video references** — every `video:` / `videos:` value resolves to a file under `static/`, and refuses paths that escape via `..`
- **CMS config sync** — collection folders in `config.yml` exist on disk
- **Orphaned images** — painting images not referenced by any content

### When to Run
- After editing content manually or via CMS
- After adding new paintings, workshops, or exhibitions
- After running `generate_content.py` or `cleanup_content.py`
- Before committing content changes
- When Sander reports CMS issues

### Usage
```bash
python scripts/validate_content.py          # human-readable report
python scripts/validate_content.py --json   # JSON output for tooling
```

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
| Language switcher shows two buttons | Missing module mounts | `hugo.toml` must have `[module]` mounts with `excludeFiles = ["en/**"]` for NL — without this, Hugo processes `content/en/` as both NL and EN |
| Images not processed | Image path doesn't resolve | Path must be relative to `assets/`, e.g. `images/paintings/foo.jpg` |
| CMS writes `/assets/images/...` (absolute, broken) into content | Field has `media_folder` override but no `public_folder` override | Sveltia/Decap rule: if you override `media_folder` on a field, **always** also override `public_folder`. Without it, the public path falls back to the literal media_folder with a leading slash. |
| CMS standalone "Media Library" uploads land in wrong folder | Global `media_folder` controls Media Library uploads | Set global `media_folder` to wherever the most common collection's media goes (currently `assets/images/paintings`), and give other collections explicit collection-level overrides (see Media folder configuration above). |
| Top-level image-widget upload lands in global folder despite a field-level `media_folder` override | Sveltia 0.165 ignores field-level `media_folder` on top-level `image` widgets | Move the override to *collection* level. Field-level still works for nested-list image widgets and for `file` widgets. |
| CMS form rejects a saved entry with "filename must match..." | Image's stored path doesn't match the field-level `pattern` regex | Either rename the file to match (lowercase-hyphens, no spaces) or relax the pattern. Existing entries with bad filenames will hit this on next edit. |
| Sander reports "kan geen schilderij plaatsen" but his commit is on `main` | CI failed after the commit landed → no deploy. Sander sees no email; Jeroen does. | `gh run list --repo ducroq/sanderveen.art --limit 5` to see the failing run; `gh run view <id> --log-failed` for the cause. The fix is usually a content/validator issue, not a CMS form issue. |
| Failure-email arrives after every painting Sander adds | Sveltia commits NL and EN as two separate pushes; between them `validate_content.py` fails on `bilingual parity` because the second-language file isn't there yet. The second commit clears it. | Expected — accept it as ignorable noise. Do not soften the parity check; protecting Sander's site against single-language paintings outweighs the false-alarm mail. Only investigate if the failure persists after both NL and EN have been committed. |
| `validate_content.py` reports "Image not found" for a CMS-saved entry even though the file exists | Frontmatter has `image: /images/paintings/foo.jpg` (Sveltia leading slash). The validator now strips this; older versions did not. | Make sure `scripts/validate_content.py` does `.lstrip("/")` before joining the path with `ROOT / "assets"` and before adding to the orphan-referenced set — leading slash makes pathlib treat the value as absolute and discard the prefix. |

## Documentation Practices

| Document | Location | Purpose | When to update |
|----------|----------|---------|----------------|
| `CLAUDE.md` | Project root | Quick orientation, architecture, constraints | Architecture changes, new key paths |
| `docs/RUNBOOK.md` | `docs/` | How-to procedures, troubleshooting | New workflows, new problems solved |
| `docs/CMS-HANDLEIDING.md` | `docs/` | Dutch CMS user guide | CMS workflow changes |
