"""
Clean up painting content files:
- Remove prices (inquiry-only approach)
- Remove scraped body text (just price lines)
- Split bilingual medium fields into NL-only and EN-only
- Fix dimension formatting errors (missing decimal points)
- Fix title casing for Dutch
- Mark featured paintings
- Set status to "available" for all (no price display)
"""

import json
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
NL_DIR = PROJECT_DIR / "content" / "schilderijen"
EN_DIR = PROJECT_DIR / "content" / "en" / "paintings"
MANIFEST_PATH = PROJECT_DIR / "scripts" / "manifest.json"

# Medium translations: Dutch -> English
MEDIUM_TRANSLATIONS = {
    "olieverf": "oil paint",
    "oilieverf": "oil paint",
    "acrylverf": "acrylic",
    "acryl": "acrylic",
    "bladgoud": "gold leaf",
    "spuitlak": "spray paint",
    "pigment": "pigment",
    "pigment poeder": "pigment powder",
    "poeder": "powder",
    "epoxy": "epoxy",
    "structuur": "texture paste",
    "hout": "wood",
    "textiel": "textile",
    "mica plaatjes": "mica flakes",
    "op paneel": "on panel",
    "op doek": "on canvas",
    " en ": " and ",
}

# Dimension fixes (scraped values missing decimal points)
DIMENSION_FIXES = {
    "113x805 cm": "113 x 80,5 cm",       # onomkeerbaar
    "2575x43 cm": "75 x 43 cm",          # aan-welke-kant-sta-je (likely 75x43)
    "255x16 cm": "25,5 x 16 cm",         # ijle-lucht
    "755x62 cm": "75,5 x 62 cm",         # de-groep
    "355x255 cm": "35,5 x 25,5 cm",      # missie-volbracht
    "675x40 cm": "67,5 x 40 cm",         # herboren, tweeluik-voor-verzoening
    "60x425 cm": "60 x 42,5 cm",         # toro
    "775x445 cm": "77,5 x 44,5 cm",      # het-beloofde-land
    "675x45 cm": "67,5 x 45 cm",         # het-getal-14
    "775x625 cm": "77,5 x 62,5 cm",      # het-meer-uit-de-hemel
    # Fix formatting on ones that are correct but need spaces
    "57x48 cm": "57 x 48 cm",
    "100x84 cm": "100 x 84 cm",
    "74x61 cm": "74 x 61 cm",
    "85x53 cm": "85 x 53 cm",
    "120x60 cm": "120 x 60 cm",
    "75x75 cm": "75 x 75 cm",
    "60,5x53 cm": "60,5 x 53 cm",
    "74x48 cm": "74 x 48 cm",
    "58,5x48,5 cm": "58,5 x 48,5 cm",
    "60x50 cm": "60 x 50 cm",
    "62x43 cm": "62 x 43 cm",
    "77x45 cm": "77 x 45 cm",
    "67x48 cm": "67 x 48 cm",
    "76x57 cm": "76 x 57 cm",
    "125x100 cm": "125 x 100 cm",
    "76x51 cm": "76 x 51 cm",
    "42x31 cm": "42 x 31 cm",
    "86x70 cm": "86 x 70 cm",
    "61x50 cm": "61 x 50 cm",
    "122,5x52,5 cm": "122,5 x 52,5 cm",
}

# Featured paintings (larger/notable works)
FEATURED_SLUGS = [
    "de-pelgrimstocht",
    "onomkeerbaar",
    "verdreven-tirannie",
    "de-vorst-en-het-volk-the-power-and-the-people",
    "de-kloof-van-welvaart",
    "de-passie-van-de-samenleving",
]

# Dutch title casing fixes (Dutch doesn't capitalize articles/prepositions)
def fix_dutch_title(title):
    """Fix Dutch title casing: only capitalize first word and proper nouns."""
    # Words that should be lowercase in Dutch titles (unless first word)
    lowercase_words = {"is", "in", "de", "het", "van", "voor", "op", "uit",
                       "en", "een", "naar", "tot", "die", "dat"}
    words = title.split()
    result = []
    for i, word in enumerate(words):
        if i == 0:
            result.append(word.capitalize())
        elif word.lower() in lowercase_words:
            result.append(word.lower())
        else:
            result.append(word.capitalize())
    return " ".join(result)


def split_medium_nl(medium_raw):
    """Extract Dutch-only medium from potentially bilingual field."""
    # Special case: field is already English-only (goud-verenigd)
    if medium_raw.startswith("Oil paint"):
        # Reverse-translate to Dutch
        nl = medium_raw
        for en, nl_word in [("Oil paint", "Olieverf"), ("gold leaf", "bladgoud"),
                            ("pigment", "pigment"), ("on panel", "op paneel"),
                            ("on canvas", "op doek")]:
            nl = nl.replace(en, nl_word)
        return nl.strip()
    # Many fields have "Dutch/ English" format
    if "/" in medium_raw:
        nl_part = medium_raw.split("/")[0].strip()
    else:
        nl_part = medium_raw.strip()
    # Fix "Oilieverf" typo
    nl_part = nl_part.replace("Oilieverf", "Olieverf")
    # Normalize capitalization: first letter cap, rest lowercase
    if nl_part:
        nl_part = nl_part[0].upper() + nl_part[1:]
    return nl_part


def translate_medium(medium_nl):
    """Translate Dutch medium to English."""
    result = medium_nl.lower()
    # Sort by length (longest first) to handle multi-word terms first
    for nl, en in sorted(MEDIUM_TRANSLATIONS.items(), key=lambda x: -len(x[0])):
        # Use regex word boundaries for short terms to avoid partial matches
        if len(nl) <= 6:
            result = re.sub(r'\b' + re.escape(nl) + r'\b', en, result)
        else:
            result = result.replace(nl, en)
    # Capitalize first letter
    if result:
        result = result[0].upper() + result[1:]
    return result


def generate_md(title, slug, medium, dimensions, image, featured, category, body=""):
    """Generate a painting .md file content."""
    featured_str = "true" if featured else "false"
    lines = [
        "---",
        f'title: "{title}"',
        "date: 2025-01-01",
        "draft: false",
        f'translationKey: "{slug}"',
        'type: "schilderijen"',
        f'medium: "{medium}"',
        f'dimensions: "{dimensions}"',
        'year: ""',
        f'status: "available"',
        f"featured: {featured_str}",
        f'image: "{image}"',
        f'category: "{category}"',
        "---",
        "",
    ]
    if body:
        lines.append(body)
        lines.append("")
    return "\n".join(lines)


def main():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        paintings = json.load(f)

    print(f"Processing {len(paintings)} paintings...\n")

    for p in paintings:
        slug = p["slug"]
        medium_raw = p.get("medium", "")
        dimensions_raw = p.get("dimensions", "")
        image = p.get("local_image", "")
        category = p.get("category", "")
        title_nl = p.get("title_nl", "")
        title_en = p.get("title_en", "")

        # Fix Dutch title casing
        title_nl = fix_dutch_title(title_nl)

        # Split and clean medium
        medium_nl = split_medium_nl(medium_raw)
        medium_en = translate_medium(medium_nl)

        # Fix dimensions
        dimensions = DIMENSION_FIXES.get(dimensions_raw, dimensions_raw)

        # Featured?
        featured = slug in FEATURED_SLUGS

        # Category label
        cat_nl = "Abstract" if category == "abstract" else "Magisch realisme"
        cat_en = "Abstract" if category == "abstract" else "Magical realism"

        # Generate NL file
        nl_content = generate_md(title_nl, slug, medium_nl, dimensions, image, featured, cat_nl)
        nl_path = NL_DIR / f"{slug}.md"
        nl_path.write_text(nl_content, encoding="utf-8")

        # Generate EN file
        en_content = generate_md(title_en, slug, medium_en, dimensions, image, featured, cat_en)
        en_path = EN_DIR / f"{slug}.md"
        en_path.write_text(en_content, encoding="utf-8")

        status = " *FEATURED*" if featured else ""
        print(f"  {slug}: {medium_nl} | {medium_en} | {dimensions}{status}")

    print(f"\nDone! Updated {len(paintings) * 2} files.")
    print(f"Featured: {len(FEATURED_SLUGS)} paintings")


if __name__ == "__main__":
    main()
