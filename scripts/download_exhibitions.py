"""Download exhibition photos from sanderveen-artshop.nl."""

import os
import urllib.request
import time
from pathlib import Path

BASE_URL = "https://sanderveen-artshop.nl"
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "images" / "exhibitions"

EXHIBITIONS = {
    "expo-veenendaal-2024": [
        "/data/upload/images/sander-en-sander.jpg",
        "/data/upload/images/expo-2024.jpg",
        "/data/upload/images/expo-2024-2.jpg",
        "/data/upload/images/expo-2024-1.jpg",
        "/data/upload/images/img-20241109-wa0007.jpg",
    ],
    "keesart-ede-2024": [
        "/data/upload/images/img-20240901-wa0001.jpg",
        "/data/upload/images/img-20240901-wa0004.jpg",
        "/data/upload/images/img-20240901-wa0000.jpg",
    ],
    "klompenpad-wageningen-2023": [
        "/data/upload/images/kahk-2024.jpg",
        "/data/upload/images/img-20230521-wa0005.jpg",
        "/data/upload/images/img-20230521-wa0006.jpg",
        "/data/upload/images/img-20240608-wa0004.jpeg",
    ],
    "aalsmeer-2025": [
        "/data/upload/images/img-20250920-wa0000.jpeg",
        "/data/upload/images/img-20250920-wa0002.jpeg",
        "/data/upload/images/img-20250920-wa0004.jpeg",
    ],
    "kunstdagen-gorinchem-2025": [
        "/data/upload/images/img-20251116-wa0000.jpg",
        "/data/upload/images/img-20251116-wa0005.jpg",
        "/data/upload/images/img-20251116-wa0007.jpg",
    ],
}


def download(url, dest):
    if dest.exists():
        print(f"  Already exists: {dest.name}")
        return True
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (sanderveen.art migration script)"
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            dest.write_bytes(resp.read())
            print(f"  Downloaded: {dest.name}")
            return True
    except Exception as e:
        print(f"  FAILED {url}: {e}")
        return False


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    ok = 0

    for expo_slug, images in EXHIBITIONS.items():
        print(f"\n--- {expo_slug} ---")
        for i, img_path in enumerate(images):
            total += 1
            ext = os.path.splitext(img_path)[1] or ".jpg"
            filename = f"{expo_slug}-{i+1}{ext}"
            dest = OUTPUT_DIR / filename
            url = BASE_URL + img_path
            if download(url, dest):
                ok += 1
            time.sleep(0.3)

    print(f"\nDone: {ok}/{total} images downloaded to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
