"""
Ingest the jtatman/tarot_dataset from Hugging Face.

Steps:
  1. Download the dataset (cached on first run)
  2. For each row:
       - Normalize the card name to canonical RWS form
       - Extract & save the card image to cards/images/{card_id}.jpg
       - Extract the reading text for supplementary samples
  3. Deduplicate readings per card (keep up to N per card)
  4. Validate against our canonical deck.json
  5. Save outputs:
       - cards/images/*.jpg
       - cards/hf_readings.json
       - cards/ingestion_report.md

Run from project root with:
    python scripts/ingest_hf_dataset.py

Idempotent: re-running won't redownload images that already exist locally.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

from datasets import load_dataset
from PIL import Image
from tqdm import tqdm


# ─────────────────────────────────────────────────────────
# CONFIG — paths and tuning knobs
# ─────────────────────────────────────────────────────────

# Where this script lives (cards/scripts/) → go up two levels to the project root (arcana/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Source data
HF_DATASET_ID = "jtatman/tarot_dataset"

# Our canonical sources — all under cards/
DECK_PATH = PROJECT_ROOT / "cards" / "deck.json"
NAME_MAP_PATH = PROJECT_ROOT / "cards" / "name_normalization.json"

# Output locations — also under cards/
IMAGES_DIR = PROJECT_ROOT / "cards" / "images"
READINGS_OUT = PROJECT_ROOT / "cards" / "hf_readings.json"
REPORT_OUT = PROJECT_ROOT / "cards" / "ingestion_report.md"

# Quality filters
MAX_READINGS_PER_CARD = 5       # keep at most N reading samples per card
MIN_READING_LENGTH = 100         # reject readings shorter than this (chars)
MAX_READING_LENGTH = 3000        # reject suspiciously long readings (likely junk)


# ─────────────────────────────────────────────────────────
# Loading our canonical references
# ─────────────────────────────────────────────────────────

def load_canonical_deck() -> dict:
    """Load our hand-curated deck.json. The set of canonical card names."""
    with open(DECK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_name_map() -> dict[str, str]:
    """Load the variant → canonical name mapping. Lowercase keys."""
    with open(NAME_MAP_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["mappings"]


# ─────────────────────────────────────────────────────────
# Normalization
# ─────────────────────────────────────────────────────────

def normalize_card_name(raw_name: str, name_map: dict[str, str]) -> str | None:
    """
    Convert a raw card name from HF data into our canonical RWS form.
    Returns None if the name can't be resolved.
    """
    if not raw_name:
        return None
    cleaned = re.sub(r"\s+", " ", raw_name.strip().lower())
    return name_map.get(cleaned)


# ─────────────────────────────────────────────────────────
# Reading text quality checks
# ─────────────────────────────────────────────────────────

def is_reading_acceptable(text: str) -> tuple[bool, str]:
    """Decide whether a reading is good enough to keep."""
    if not text or not text.strip():
        return False, "empty"
    n = len(text)
    if n < MIN_READING_LENGTH:
        return False, f"too short ({n} chars)"
    if n > MAX_READING_LENGTH:
        return False, f"too long ({n} chars)"
    return True, ""


# ─────────────────────────────────────────────────────────
# Image handling
# ─────────────────────────────────────────────────────────

def save_card_image(image, card_id: str) -> Path | None:
    """Save a card image to disk. Skips if already exists (idempotent)."""
    out_path = IMAGES_DIR / f"{card_id}.jpg"
    if out_path.exists():
        return out_path
    try:
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(out_path, format="JPEG", quality=90)
        return out_path
    except Exception as e:
        print(f"  Warning: failed to save image for {card_id}: {e}")
        return None


# ─────────────────────────────────────────────────────────
# The main ingestion loop
# ─────────────────────────────────────────────────────────

def main():
    print("-" * 60)
    print(" HF dataset ingestion - jtatman/tarot_dataset")
    print("-" * 60)
    
    # Make sure output directories exist
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    READINGS_OUT.parent.mkdir(parents=True, exist_ok=True)
    
    # Load canonical references
    print("\nLoading canonical references...")
    deck = load_canonical_deck()
    canonical_names = {card["name"] for card in deck["cards"]}
    canonical_by_name = {card["name"]: card for card in deck["cards"]}
    name_map = load_name_map()
    print(f"  Canonical deck: {len(canonical_names)} cards")
    print(f"  Name variants mapped: {len(name_map)}")
    
    # Download / load the HF dataset
    print(f"\nLoading {HF_DATASET_ID}...")
    print("  (downloads on first run; cached after that)")
    ds = load_dataset(HF_DATASET_ID, split="train")
    print(f"  Loaded {len(ds)} rows")
    
    # Stats trackers
    stats = {
        "rows_total": len(ds),
        "rows_processed": 0,
        "name_unresolved": 0,
        "name_not_in_deck": 0,
        "reading_rejected_quality": 0,
        "image_saved": 0,
        "image_skipped_existing": 0,
        "image_failed": 0,
        "readings_kept_per_card": defaultdict(int),
    }
    unresolved_names = defaultdict(int)
    readings_by_card = defaultdict(list)
    
    # Main loop
    print("\nProcessing rows...")
    for idx, row in enumerate(tqdm(ds, desc="  rows")):
        stats["rows_processed"] += 1
        
        raw_name = row.get("card_name", "")
        canonical = normalize_card_name(raw_name, name_map)
        
        if canonical is None:
            stats["name_unresolved"] += 1
            unresolved_names[raw_name] += 1
            continue
        
        if canonical not in canonical_names:
            stats["name_not_in_deck"] += 1
            continue
        
        reading_text = row.get("card_reading", "") or ""
        accepted, reason = is_reading_acceptable(reading_text)
        if not accepted:
            stats["reading_rejected_quality"] += 1
            continue
        
        card_id = canonical_by_name[canonical]["id"]
        image = row.get("image")
        if image is not None:
            if (IMAGES_DIR / f"{card_id}.jpg").exists():
                stats["image_skipped_existing"] += 1
            else:
                if save_card_image(image, card_id):
                    stats["image_saved"] += 1
                else:
                    stats["image_failed"] += 1
        
        if stats["readings_kept_per_card"][canonical] < MAX_READINGS_PER_CARD:
            readings_by_card[canonical].append({
                "text": reading_text.strip(),
                "source_dataset": HF_DATASET_ID,
                "source_row_index": idx,
                "source_raw_name": raw_name,
            })
            stats["readings_kept_per_card"][canonical] += 1
    
    # Save outputs
    print("\nWriting outputs...")
    
    readings_payload = {
        "metadata": {
            "source_dataset": HF_DATASET_ID,
            "ingested_at": datetime.now().isoformat(),
            "max_readings_per_card": MAX_READINGS_PER_CARD,
            "total_cards_covered": len(readings_by_card),
            "total_readings": sum(len(v) for v in readings_by_card.values()),
        },
        "readings": dict(readings_by_card),
    }
    with open(READINGS_OUT, "w", encoding="utf-8") as f:
        json.dump(readings_payload, f, indent=2, ensure_ascii=False)
    print(f"  Wrote {READINGS_OUT}")
    
    report = generate_report(stats, unresolved_names, readings_by_card, canonical_names)
    with open(REPORT_OUT, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  Wrote {REPORT_OUT}")
    
    # Print summary
    print("\n" + "-" * 60)
    print(" Summary")
    print("-" * 60)
    print(f"  Rows processed:           {stats['rows_processed']}")
    print(f"  Names unresolved:         {stats['name_unresolved']}")
    print(f"  Names not in canonical:   {stats['name_not_in_deck']}")
    print(f"  Readings rejected:        {stats['reading_rejected_quality']}")
    print(f"  Images saved (new):       {stats['image_saved']}")
    print(f"  Images already present:   {stats['image_skipped_existing']}")
    print(f"  Cards with readings:      {len(readings_by_card)} / {len(canonical_names)}")
    
    cards_missing = canonical_names - set(readings_by_card.keys())
    if cards_missing:
        print(f"\n  Warning: no readings ingested for: {sorted(cards_missing)}")
    else:
        print("\n  OK: every canonical card has at least one reading.")
    print()


# ─────────────────────────────────────────────────────────
# Report generation
# ─────────────────────────────────────────────────────────

def generate_report(stats, unresolved_names, readings_by_card, canonical_names) -> str:
    timestamp = datetime.now().isoformat(timespec="seconds")
    
    lines = []
    lines.append(f"# HF Dataset Ingestion Report")
    lines.append(f"\n_Generated: {timestamp}_")
    lines.append(f"\n**Source:** `{HF_DATASET_ID}` on Hugging Face")
    
    lines.append("\n## Pipeline summary")
    lines.append(f"\n- Rows in source dataset: **{stats['rows_total']}**")
    lines.append(f"- Rows processed: **{stats['rows_processed']}**")
    lines.append(f"- Rows with unresolvable card names: **{stats['name_unresolved']}**")
    lines.append(f"- Rows mapped but outside canonical deck: **{stats['name_not_in_deck']}**")
    lines.append(f"- Readings rejected on quality filter: **{stats['reading_rejected_quality']}**")
    lines.append(f"- Images saved (new this run): **{stats['image_saved']}**")
    lines.append(f"- Images skipped (already present): **{stats['image_skipped_existing']}**")
    
    lines.append("\n## Coverage")
    cards_present = set(readings_by_card.keys())
    cards_missing = canonical_names - cards_present
    coverage_pct = 100 * len(cards_present) / len(canonical_names) if canonical_names else 0
    lines.append(f"\n- Canonical cards in deck: **{len(canonical_names)}**")
    lines.append(f"- Canonical cards with HF readings: **{len(cards_present)}** ({coverage_pct:.0f}%)")
    if cards_missing:
        lines.append(f"- Canonical cards missing HF data:")
        for c in sorted(cards_missing):
            lines.append(f"  - {c}")
    
    lines.append("\n## Readings per card")
    lines.append("\n| Card | Readings kept |")
    lines.append("|------|---------------|")
    for card in sorted(canonical_names):
        n = len(readings_by_card.get(card, []))
        lines.append(f"| {card} | {n} |")
    
    if unresolved_names:
        lines.append("\n## Unresolved card names")
        lines.append("\nNames that appeared in HF data but couldn't be mapped to our canonical deck.\n")
        lines.append("| Raw name | Count |")
        lines.append("|----------|-------|")
        for name, count in sorted(unresolved_names.items(), key=lambda x: -x[1])[:30]:
            lines.append(f"| `{name}` | {count} |")
        if len(unresolved_names) > 30:
            lines.append(f"\n_(showing top 30 of {len(unresolved_names)})_")
    
    lines.append("\n## Notes on data quality")
    lines.append("""
- Source readings appear to be LLM-generated; many begin with formulaic phrases 
  like "Based on the context and the description of the card...". These are kept 
  as supplementary samples but should not be treated as authoritative interpretations.
- Source uses Marseille-tradition card names (e.g. "the popess" rather than 
  "The High Priestess"). Normalization is handled by `name_normalization.json`.
- Only Major Arcana are currently covered in our canonical `deck.json`. Minor 
  Arcana rows from the HF dataset are skipped at the canonical-match step until 
  `deck.json` is extended.
""")
    
    return "\n".join(lines)


if __name__ == "__main__":
    main()