"""
Content validation for sanderveen.art

Validates all Hugo content files against the CMS schema (Sveltia CMS config.yml).
Checks bilingual parity, front matter schema, enums, image paths, and cross-references.

Usage:
    python scripts/validate_content.py          # Run all checks
    python scripts/validate_content.py --json   # Output results as JSON
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# --- Configuration ---

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "images"

# Content collection definitions (mirrors CMS config.yml)
COLLECTIONS = {
    "paintings": {
        "nl": {
            "folder": ROOT / "content" / "schilderijen",
            "required_fields": ["title", "date", "draft", "translationKey", "type", "medium", "dimensions", "status", "featured", "image", "category"],
            "optional_fields": ["year"],
            "type_value": "schilderijen",
            "category_options": ["Abstract", "Surrealistisch"],
            "status_options": ["available", "sold", "not-for-sale"],
        },
        "en": {
            "folder": ROOT / "content" / "en" / "paintings",
            "required_fields": ["title", "date", "draft", "translationKey", "type", "medium", "dimensions", "status", "featured", "image", "category"],
            "optional_fields": ["year"],
            "type_value": "schilderijen",
            "category_options": ["Abstract", "Surrealist"],
            "status_options": ["available", "sold", "not-for-sale"],
        },
    },
    "workshops": {
        "nl": {
            "folder": ROOT / "content" / "workshops",
            "required_fields": ["title", "description", "translationKey", "type", "workshop_date", "location", "price", "weight"],
            "optional_fields": [],
            "type_value": "workshops",
        },
        "en": {
            "folder": ROOT / "content" / "en" / "workshops",
            "required_fields": ["title", "description", "translationKey", "type", "workshop_date", "location", "price", "weight"],
            "optional_fields": [],
            "type_value": "workshops",
        },
    },
    "exhibitions": {
        "nl": {
            "folder": ROOT / "content" / "exposities",
            "required_fields": ["title", "description", "translationKey", "type", "date", "start_date", "location", "weight"],
            "optional_fields": ["end_date", "image", "gallery"],
            "type_value": "exposities",
        },
        "en": {
            "folder": ROOT / "content" / "en" / "exhibitions",
            "required_fields": ["title", "description", "translationKey", "type", "date", "start_date", "location", "weight"],
            "optional_fields": ["end_date", "image", "gallery"],
            "type_value": "exposities",
        },
    },
}


@dataclass
class Issue:
    severity: str  # ERROR, WARNING
    collection: str
    lang: str
    file: str
    field: str
    message: str


@dataclass
class ValidationResult:
    issues: list = field(default_factory=list)
    files_checked: int = 0
    collections_checked: int = 0

    @property
    def errors(self):
        return [i for i in self.issues if i.severity == "ERROR"]

    @property
    def warnings(self):
        return [i for i in self.issues if i.severity == "WARNING"]


def parse_front_matter(filepath: Path) -> Optional[dict]:
    """Parse YAML front matter from a Hugo content file."""
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None

    fm = {}
    current_list_key = None
    for raw_line in match.group(1).splitlines():
        # Detect indented list item: "  - value" (must check before strip)
        list_item_m = re.match(r'^\s+-\s+(.+)$', raw_line)
        if current_list_key and list_item_m:
            val = list_item_m.group(1).strip()
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            fm[current_list_key].append(val)
            continue

        line = raw_line.strip()
        if not line or line.startswith("#"):
            current_list_key = None
            continue

        m = re.match(r'^(\w[\w_]*)\s*:\s*(.*)$', line)
        if m:
            key = m.group(1)
            val = m.group(2).strip()

            if val == "":
                # Empty value — start of a list (or genuinely empty); subsequent "  - x" lines populate it
                fm[key] = []
                current_list_key = key
                continue

            current_list_key = None
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            if val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
            fm[key] = val
    return fm


def validate_collection(collection_name: str, lang: str, config: dict, result: ValidationResult):
    """Validate all content files in a collection."""
    folder = config["folder"]
    if not folder.exists():
        result.issues.append(Issue("ERROR", collection_name, lang, str(folder), "-", f"Content folder missing: {folder}"))
        return {}

    translation_keys = {}  # translationKey -> filepath

    for md_file in sorted(folder.glob("*.md")):
        if md_file.name == "_index.md":
            continue

        result.files_checked += 1
        relpath = md_file.relative_to(ROOT)
        fm = parse_front_matter(md_file)

        if fm is None:
            result.issues.append(Issue("ERROR", collection_name, lang, str(relpath), "frontmatter", "Missing or invalid YAML front matter"))
            continue

        # Check required fields
        for field_name in config["required_fields"]:
            if field_name not in fm or fm[field_name] == "" or fm[field_name] is None:
                result.issues.append(Issue("ERROR", collection_name, lang, str(relpath), field_name, f"Required field '{field_name}' missing or empty"))

        # Check type value
        if "type" in fm and fm["type"] != config["type_value"]:
            result.issues.append(Issue("ERROR", collection_name, lang, str(relpath), "type", f"Expected type='{config['type_value']}', got '{fm['type']}'"))

        # Check enum fields
        if "category_options" in config and "category" in fm:
            if fm["category"] not in config["category_options"]:
                result.issues.append(Issue("ERROR", collection_name, lang, str(relpath), "category", f"Invalid category '{fm['category']}', expected one of {config['category_options']}"))

        if "status_options" in config and "status" in fm:
            if fm["status"] not in config["status_options"]:
                result.issues.append(Issue("ERROR", collection_name, lang, str(relpath), "status", f"Invalid status '{fm['status']}', expected one of {config['status_options']}"))

        # Check draft field is boolean
        if "draft" in fm and not isinstance(fm["draft"], bool):
            result.issues.append(Issue("WARNING", collection_name, lang, str(relpath), "draft", f"'draft' should be boolean, got '{fm['draft']}'"))

        # Check featured field is boolean
        if "featured" in fm and not isinstance(fm["featured"], bool):
            result.issues.append(Issue("WARNING", collection_name, lang, str(relpath), "featured", f"'featured' should be boolean, got '{fm['featured']}'"))

        # Check image path exists (resolve from assets/)
        # Strip leading slash: Sveltia CMS writes paths like "/images/..." which would
        # otherwise be treated as absolute by pathlib and discard the assets prefix.
        if "image" in fm and fm["image"]:
            img_value = str(fm["image"]).lstrip("/")
            img_path = ROOT / "assets" / img_value
            if not img_path.exists():
                result.issues.append(Issue("ERROR", collection_name, lang, str(relpath), "image", f"Image not found: {fm['image']}"))

        # Check gallery image paths exist (exhibitions)
        if "gallery" in fm and isinstance(fm["gallery"], list):
            for img_value in fm["gallery"]:
                img_norm = str(img_value).lstrip("/")
                img_path = ROOT / "assets" / img_norm
                if not img_path.exists():
                    result.issues.append(Issue("ERROR", collection_name, lang, str(relpath), "gallery", f"Gallery image not found: {img_value}"))

        # Check translationKey format
        if "translationKey" in fm:
            tk = fm["translationKey"]
            if not re.match(r'^[a-z0-9-]+$', str(tk)):
                result.issues.append(Issue("WARNING", collection_name, lang, str(relpath), "translationKey", f"translationKey '{tk}' should be lowercase with hyphens only"))
            translation_keys[tk] = str(relpath)

        # Check dimensions format (paintings only)
        if collection_name == "paintings" and "dimensions" in fm and fm["dimensions"]:
            dim = str(fm["dimensions"])
            if not re.match(r'^\d+[\d,.]?\d*\s*x\s*\d+[\d,.]?\d*\s*cm$', dim):
                result.issues.append(Issue("WARNING", collection_name, lang, str(relpath), "dimensions", f"Unusual dimensions format: '{dim}' (expected 'N x N cm')"))

        # Check weight is numeric (workshops/exhibitions)
        if "weight" in fm:
            try:
                int(fm["weight"])
            except (ValueError, TypeError):
                result.issues.append(Issue("WARNING", collection_name, lang, str(relpath), "weight", f"'weight' should be numeric, got '{fm['weight']}'"))

    return translation_keys


def check_bilingual_parity(collection_name: str, nl_keys: dict, en_keys: dict, result: ValidationResult):
    """Check that NL and EN collections have matching translationKeys."""
    nl_set = set(nl_keys.keys())
    en_set = set(en_keys.keys())

    for key in nl_set - en_set:
        result.issues.append(Issue("ERROR", collection_name, "parity", nl_keys[key], "translationKey", f"NL has translationKey '{key}' but no EN counterpart"))

    for key in en_set - nl_set:
        result.issues.append(Issue("ERROR", collection_name, "parity", en_keys[key], "translationKey", f"EN has translationKey '{key}' but no NL counterpart"))


def check_status_consistency(result: ValidationResult):
    """Check that NL and EN paintings have matching status values."""
    nl_folder = COLLECTIONS["paintings"]["nl"]["folder"]
    en_folder = COLLECTIONS["paintings"]["en"]["folder"]

    nl_data = {}
    for md_file in nl_folder.glob("*.md"):
        if md_file.name == "_index.md":
            continue
        fm = parse_front_matter(md_file)
        if fm and "translationKey" in fm:
            nl_data[fm["translationKey"]] = fm

    for md_file in en_folder.glob("*.md"):
        if md_file.name == "_index.md":
            continue
        fm = parse_front_matter(md_file)
        if fm and "translationKey" in fm and fm["translationKey"] in nl_data:
            nl_fm = nl_data[fm["translationKey"]]
            relpath = md_file.relative_to(ROOT)

            # Status must match
            if fm.get("status") != nl_fm.get("status"):
                result.issues.append(Issue("ERROR", "paintings", "parity", str(relpath), "status", f"Status mismatch: NL='{nl_fm.get('status')}', EN='{fm.get('status')}' for key '{fm['translationKey']}'"))

            # Featured must match
            if fm.get("featured") != nl_fm.get("featured"):
                result.issues.append(Issue("WARNING", "paintings", "parity", str(relpath), "featured", f"Featured mismatch: NL={nl_fm.get('featured')}, EN={fm.get('featured')} for key '{fm['translationKey']}'"))

            # Image should match (normalize leading slash before compare)
            nl_img = str(nl_fm.get("image") or "").lstrip("/")
            en_img = str(fm.get("image") or "").lstrip("/")
            if nl_img != en_img:
                result.issues.append(Issue("WARNING", "paintings", "parity", str(relpath), "image", f"Image mismatch: NL='{nl_fm.get('image')}', EN='{fm.get('image')}' for key '{fm['translationKey']}'"))

            # Category consistency (Abstract matches, Surrealistisch <-> Surrealist)
            nl_cat = nl_fm.get("category", "")
            en_cat = fm.get("category", "")
            expected_en = {"Abstract": "Abstract", "Surrealistisch": "Surrealist"}.get(nl_cat)
            if expected_en and en_cat != expected_en:
                result.issues.append(Issue("ERROR", "paintings", "parity", str(relpath), "category", f"Category mismatch: NL='{nl_cat}' should map to EN='{expected_en}', got '{en_cat}'"))


def check_cms_config_sync(result: ValidationResult):
    """Check that CMS config.yml collection folders match actual content folders."""
    config_path = ROOT / "static" / "admin" / "config.yml"
    if not config_path.exists():
        result.issues.append(Issue("ERROR", "cms", "-", str(config_path), "-", "CMS config.yml not found"))
        return

    text = config_path.read_text(encoding="utf-8")

    # Extract collection folder paths from config (under collections:)
    folders = re.findall(r'folder:\s*(.+)', text)
    for folder in folders:
        folder = folder.strip().strip('"').strip("'")
        # Skip non-content paths (public_folder, media_folder are not collection folders)
        if not folder.startswith("content"):
            continue
        full_path = ROOT / folder
        if not full_path.exists():
            result.issues.append(Issue("ERROR", "cms", "-", "static/admin/config.yml", "folder", f"CMS references folder '{folder}' which does not exist"))


def check_orphaned_images(result: ValidationResult):
    """Check for painting images not referenced by any content file."""
    paintings_dir = ASSETS / "paintings"
    if not paintings_dir.exists():
        return

    # Collect all referenced images
    referenced = set()
    for collection in ["paintings"]:
        for lang_config in COLLECTIONS[collection].values():
            folder = lang_config["folder"]
            for md_file in folder.glob("*.md"):
                if md_file.name == "_index.md":
                    continue
                fm = parse_front_matter(md_file)
                if fm and "image" in fm:
                    referenced.add(str(fm["image"]).lstrip("/"))

    # Check all images in paintings dir
    for img_file in paintings_dir.rglob("*"):
        if img_file.is_file() and img_file.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            rel = img_file.relative_to(ASSETS)
            img_ref = str(rel).replace("\\", "/")
            prefixed = "images/" + img_ref
            if prefixed not in referenced:
                result.issues.append(Issue("WARNING", "paintings", "-", str(rel), "image", f"Orphaned image not referenced by any content: {img_ref}"))


def run_validation() -> ValidationResult:
    """Run all validation checks."""
    result = ValidationResult()

    all_keys = {}  # collection -> {nl: {keys}, en: {keys}}

    for collection_name, langs in COLLECTIONS.items():
        result.collections_checked += 1
        all_keys[collection_name] = {}

        for lang, config in langs.items():
            keys = validate_collection(collection_name, lang, config, result)
            all_keys[collection_name][lang] = keys

        # Bilingual parity check
        if "nl" in all_keys[collection_name] and "en" in all_keys[collection_name]:
            check_bilingual_parity(
                collection_name,
                all_keys[collection_name]["nl"],
                all_keys[collection_name]["en"],
                result,
            )

    # Cross-collection checks
    check_status_consistency(result)
    check_cms_config_sync(result)
    check_orphaned_images(result)

    return result


def print_results(result: ValidationResult, as_json: bool = False):
    """Print validation results."""
    if as_json:
        output = {
            "files_checked": result.files_checked,
            "collections_checked": result.collections_checked,
            "errors": len(result.errors),
            "warnings": len(result.warnings),
            "issues": [
                {
                    "severity": i.severity,
                    "collection": i.collection,
                    "lang": i.lang,
                    "file": i.file,
                    "field": i.field,
                    "message": i.message,
                }
                for i in result.issues
            ],
        }
        print(json.dumps(output, indent=2))
        return

    print(f"\n{'='*60}")
    print(f"  Content Validation — sanderveen.art")
    print(f"{'='*60}")
    print(f"  Files checked:  {result.files_checked}")
    print(f"  Collections:    {result.collections_checked}")
    print(f"  Errors:         {len(result.errors)}")
    print(f"  Warnings:       {len(result.warnings)}")
    print(f"{'='*60}\n")

    if not result.issues:
        print("  All checks passed!\n")
        return

    # Group by severity
    for severity in ["ERROR", "WARNING"]:
        issues = [i for i in result.issues if i.severity == severity]
        if not issues:
            continue

        label = "ERRORS" if severity == "ERROR" else "WARNINGS"
        print(f"  {label}:")
        print(f"  {'-'*40}")
        for issue in issues:
            print(f"  [{issue.severity}] {issue.file}")
            print(f"    {issue.field}: {issue.message}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Validate sanderveen.art content files")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    result = run_validation()
    print_results(result, as_json=args.json)

    # Exit with error code if there are errors
    sys.exit(1 if result.errors else 0)


if __name__ == "__main__":
    main()
