"""
Scraper for sanderveen-artshop.nl
Crawls all painting detail pages, downloads images, and outputs a JSON manifest.

Usage:
    python scripts/scrape.py

Output:
    scripts/manifest.json
    assets/images/paintings/abstract/*.jpg
    assets/images/paintings/magisch-realisme/*.jpg
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

BASE_URL = "https://sanderveen-artshop.nl"
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "images" / "paintings"
MANIFEST_PATH = Path(__file__).parent / "manifest.json"

CATEGORIES = {
    "abstract": "/webshop/schilderijenpaintings/abstract/",
    "magisch-realisme": "/webshop/schilderijenpaintings/magisch-realisme--reverso-context/",
}


def fetch(url, retries=3):
    """Fetch URL content with retry logic."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (sanderveen.art migration script)"
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < retries - 1:
                time.sleep(2)
    return None


def download_image(url, dest_path):
    """Download an image file."""
    if dest_path.exists():
        print(f"  Image already exists: {dest_path.name}")
        return True
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (sanderveen.art migration script)"
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_bytes(resp.read())
            print(f"  Downloaded: {dest_path.name}")
            return True
    except Exception as e:
        print(f"  Failed to download {url}: {e}")
        return False


class LinkExtractor(HTMLParser):
    """Extract product detail links from category pages."""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs_dict = dict(attrs)
            href = attrs_dict.get("href", "")
            if "/detail/" in href and href.endswith(".html"):
                if href not in self.links:
                    self.links.append(href)


class ProductPageParser(HTMLParser):
    """Extract metadata from a product detail page."""

    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_price = False
        self.in_description = False
        self.title = ""
        self.images = []
        self.description_parts = []
        self.current_tag = ""
        self.price_text = ""
        self.meta_content = {}
        self._tag_stack = []
        self._capture_text = False
        self._text_parts = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self._tag_stack.append(tag)

        # Look for product images
        if tag == "img":
            src = attrs_dict.get("src", "")
            if "/data/upload/Shop/images/" in src:
                if src not in self.images:
                    self.images.append(src)

        # Look for og:image
        if tag == "meta":
            prop = attrs_dict.get("property", "")
            name = attrs_dict.get("name", "")
            content = attrs_dict.get("content", "")
            if prop == "og:image" and content:
                if content not in self.images:
                    self.images.append(content)
            if prop == "og:title" and content:
                self.meta_content["og_title"] = content

    def handle_endtag(self, tag):
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        # Capture price patterns
        if "€" in text or "EUR" in text:
            self.price_text = text


def extract_product_data(html, url):
    """Extract structured data from a product page HTML."""
    data = {}

    # Extract title from URL slug
    slug = url.rstrip(".html").split("/")[-1]

    # Split NL/EN title from slug (format: "dutch-title--english-title")
    if "--" in slug:
        parts = slug.split("--", 1)
        data["title_nl"] = parts[0].replace("-", " ").strip().title()
        data["title_en"] = parts[1].replace("-", " ").strip().title()
    else:
        data["title_nl"] = slug.replace("-", " ").strip().title()
        data["title_en"] = data["title_nl"]

    # Extract product ID from URL
    match = re.search(r"/detail/(\d+)/", url)
    data["id"] = int(match.group(1)) if match else 0

    # Extract price
    price_match = re.search(r'€\s*([\d.,]+)', html)
    if price_match:
        price_str = price_match.group(1).replace(".", "").replace(",", ".")
        try:
            data["price"] = float(price_str)
        except ValueError:
            data["price"] = 0

    # Extract images from /data/upload/Shop/images/
    image_matches = re.findall(r'(?:src|href)=["\']([^"\']*?/data/upload/Shop/images/[^"\']+)["\']', html)
    data["images"] = list(dict.fromkeys(image_matches))  # deduplicate, preserve order

    # Also check for og:image
    og_match = re.search(r'property="og:image"\s+content="([^"]+)"', html)
    if og_match:
        og_img = og_match.group(1)
        if og_img not in data["images"]:
            data["images"].insert(0, og_img)

    # Extract description - look for text content near the product
    # Try to find description in product detail area
    desc_match = re.search(
        r'<div[^>]*class="[^"]*(?:description|product-text|detail)[^"]*"[^>]*>(.*?)</div>',
        html, re.DOTALL | re.IGNORECASE
    )
    if desc_match:
        desc_html = desc_match.group(1)
        # Strip HTML tags
        desc_text = re.sub(r'<[^>]+>', ' ', desc_html)
        desc_text = re.sub(r'\s+', ' ', desc_text).strip()
        data["description"] = desc_text
    else:
        data["description"] = ""

    # Try to extract medium/dimensions from page text
    # Common patterns: "Olie op paneel", "130 x 80 cm", etc.
    dim_match = re.search(r'(\d+(?:[.,]\d+)?\s*x\s*\d+(?:[.,]\d+)?)\s*cm', html)
    if dim_match:
        data["dimensions"] = dim_match.group(1).strip() + " cm"
    else:
        data["dimensions"] = ""

    # Extract medium - look for common Dutch art terms
    medium_patterns = [
        r'(Olie(?:verf)?[^<.]{0,60}(?:paneel|doek|canvas|panel))',
        r'(Oil[^<.]{0,60}(?:panel|canvas))',
        r'(Acryl[^<.]{0,60}(?:paneel|doek|canvas|panel))',
        r'(Mixed media[^<.]{0,60})',
    ]
    data["medium"] = ""
    for pattern in medium_patterns:
        m = re.search(pattern, html, re.IGNORECASE)
        if m:
            medium_text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            # Clean up
            medium_text = re.sub(r'\s+', ' ', medium_text)
            if len(medium_text) < 100:
                data["medium"] = medium_text
                break

    return data


def slugify(text):
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def main():
    paintings = []

    for category, cat_path in CATEGORIES.items():
        print(f"\n--- Category: {category} ---")
        cat_url = BASE_URL + cat_path
        html = fetch(cat_url)
        if not html:
            print(f"Failed to fetch category page: {cat_url}")
            continue

        # Extract detail links
        parser = LinkExtractor()
        parser.feed(html)
        detail_links = parser.links
        print(f"Found {len(detail_links)} paintings in {category}")

        cat_dir = OUTPUT_DIR / category
        cat_dir.mkdir(parents=True, exist_ok=True)

        for link in detail_links:
            full_url = link if link.startswith("http") else BASE_URL + link
            print(f"\nProcessing: {link.split('/')[-1]}")

            detail_html = fetch(full_url)
            if not detail_html:
                print(f"  Failed to fetch detail page")
                continue

            data = extract_product_data(detail_html, link)
            data["category"] = category
            data["url"] = link

            # Generate slug from Dutch title
            data["slug"] = slugify(data["title_nl"])

            # Download primary image
            if data["images"]:
                img_url = data["images"][0]
                if not img_url.startswith("http"):
                    img_url = BASE_URL + img_url

                # Determine file extension
                ext = os.path.splitext(urllib.parse.urlparse(img_url).path)[1] or ".jpg"
                img_filename = data["slug"] + ext
                img_path = cat_dir / img_filename
                data["local_image"] = f"images/paintings/{category}/{img_filename}"

                download_image(img_url, img_path)
            else:
                data["local_image"] = ""
                print("  No image found!")

            paintings.append(data)
            time.sleep(0.5)  # Be polite

    # Sort by ID
    paintings.sort(key=lambda p: p.get("id", 0), reverse=True)

    # Write manifest
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(paintings, f, indent=2, ensure_ascii=False)

    print(f"\n\nDone! Scraped {len(paintings)} paintings.")
    print(f"Manifest written to: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
