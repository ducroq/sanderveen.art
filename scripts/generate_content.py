"""
Generate Hugo content files from scraped manifest.

Usage:
    python scripts/generate_content.py

Reads: scripts/manifest.json
Output: content/schilderijen/*.md and content/en/paintings/*.md
"""

import json
import re
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPTS_DIR.parent
MANIFEST_PATH = SCRIPTS_DIR / "manifest.json"

NL_PAINTINGS_DIR = PROJECT_DIR / "content" / "schilderijen"
EN_PAINTINGS_DIR = PROJECT_DIR / "content" / "en" / "paintings"

CATEGORY_MAP = {
    "abstract": {"nl": "Abstract", "en": "Abstract"},
    "magisch-realisme": {"nl": "Magisch Realisme", "en": "Magical Realism"},
}


def slugify(text):
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def format_price(price):
    """Format price for front matter."""
    if not price:
        return ""
    if isinstance(price, (int, float)):
        if price == int(price):
            return str(int(price))
        return f"{price:.2f}"
    return str(price)


def generate_nl_md(painting, weight):
    """Generate Dutch .md content file."""
    slug = painting["slug"]
    title_nl = painting["title_nl"]
    image = painting.get("local_image", "")
    price = format_price(painting.get("price", ""))
    dimensions = painting.get("dimensions", "")
    medium = painting.get("medium", "")
    description = painting.get("description", "")
    category = painting.get("category", "")

    # Determine if featured (higher-priced works)
    price_val = painting.get("price", 0) or 0
    featured = "true" if price_val >= 900 else "false"

    content = f"""---
title: "{title_nl}"
date: 2025-01-01
draft: false
translationKey: "{slug}"
type: "schilderijen"
medium: "{medium}"
dimensions: "{dimensions}"
year: ""
price: "{price}"
status: "available"
featured: {featured}
weight: {weight}
image: "{image}"
---

{description}
"""
    return content


def generate_en_md(painting, weight):
    """Generate English .md content file."""
    slug = painting["slug"]
    title_en = painting["title_en"]
    image = painting.get("local_image", "")
    price = format_price(painting.get("price", ""))
    dimensions = painting.get("dimensions", "")
    medium = painting.get("medium", "")
    description = painting.get("description", "")

    price_val = painting.get("price", 0) or 0
    featured = "true" if price_val >= 900 else "false"

    content = f"""---
title: "{title_en}"
date: 2025-01-01
draft: false
translationKey: "{slug}"
type: "schilderijen"
medium: "{medium}"
dimensions: "{dimensions}"
year: ""
price: "{price}"
status: "available"
featured: {featured}
weight: {weight}
image: "{image}"
---

{description}
"""
    return content


def main():
    if not MANIFEST_PATH.exists():
        print(f"Manifest not found at {MANIFEST_PATH}")
        print("Run scrape.py first: python scripts/scrape.py")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        paintings = json.load(f)

    print(f"Loaded {len(paintings)} paintings from manifest")

    # Create directories
    NL_PAINTINGS_DIR.mkdir(parents=True, exist_ok=True)
    EN_PAINTINGS_DIR.mkdir(parents=True, exist_ok=True)

    for i, painting in enumerate(paintings):
        slug = painting["slug"]
        weight = (i + 1) * 10

        # Dutch version
        nl_path = NL_PAINTINGS_DIR / f"{slug}.md"
        nl_content = generate_nl_md(painting, weight)
        nl_path.write_text(nl_content, encoding="utf-8")
        print(f"  NL: {nl_path.name}")

        # English version
        en_path = EN_PAINTINGS_DIR / f"{slug}.md"
        en_content = generate_en_md(painting, weight)
        en_path.write_text(en_content, encoding="utf-8")
        print(f"  EN: {en_path.name}")

    # Create section index files
    nl_index = NL_PAINTINGS_DIR / "_index.md"
    nl_index.write_text("""---
title: "Schilderijen"
description: "Bekijk het volledige portfolio van schilderijen. Olieverf, acryl en mixed media op paneel en doek."
translationKey: "paintings"
---
""", encoding="utf-8")

    en_index = EN_PAINTINGS_DIR / "_index.md"
    en_index.write_text("""---
title: "Paintings"
description: "Browse the full portfolio of paintings. Oil, acrylic and mixed media on panel and canvas."
translationKey: "paintings"
---
""", encoding="utf-8")

    print(f"\nGenerated {len(paintings) * 2} content files + 2 index files")


if __name__ == "__main__":
    main()
