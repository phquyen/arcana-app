# HF Dataset Ingestion Report

_Generated: 2026-05-27T13:54:43_

**Source:** `jtatman/tarot_dataset` on Hugging Face

## Pipeline summary

- Rows in source dataset: **1120**
- Rows processed: **1120**
- Rows with unresolvable card names: **932**
- Rows mapped but outside canonical deck: **0**
- Readings rejected on quality filter: **5**
- Images saved (new this run): **0**
- Images skipped (already present): **183**

## Coverage

- Canonical cards in deck: **22**
- Canonical cards with HF readings: **22** (100%)

## Readings per card

| Card | Readings kept |
|------|---------------|
| Death | 5 |
| Judgement | 5 |
| Justice | 5 |
| Strength | 5 |
| Temperance | 5 |
| The Chariot | 5 |
| The Devil | 5 |
| The Emperor | 5 |
| The Empress | 5 |
| The Fool | 5 |
| The Hanged Man | 5 |
| The Hermit | 5 |
| The Hierophant | 5 |
| The High Priestess | 5 |
| The Lovers | 5 |
| The Magician | 5 |
| The Moon | 5 |
| The Star | 5 |
| The Sun | 5 |
| The Tower | 5 |
| The World | 5 |
| Wheel of Fortune | 5 |

## Unresolved card names

Names that appeared in HF data but couldn't be mapped to our canonical deck.

| Raw name | Count |
|----------|-------|
| ` ace of cups` | 9 |
| ` two of cups` | 9 |
| ` three of cups` | 9 |
| ` four of cups` | 9 |
| ` five of cups` | 9 |
| ` six of cups` | 9 |
| ` seven of cups` | 9 |
| ` eight of cups` | 9 |
| ` ten of cups` | 9 |
| ` knight of cups` | 9 |
| ` queen of cups` | 9 |
| ` king of cups` | 9 |
| ` ace of swords` | 9 |
| ` two of swords` | 9 |
| ` three of swords` | 9 |
| ` four of swords` | 9 |
| ` five of swords` | 9 |
| ` six of swords` | 9 |
| ` seven of swords` | 9 |
| ` eight of swords` | 9 |
| ` nine of swords` | 9 |
| ` ten of swords` | 9 |
| ` knight of swords` | 9 |
| ` queen of swords` | 9 |
| ` king of swords` | 9 |
| ` nine of cups` | 8 |
| ` ace of pentacles` | 8 |
| ` two of pentacles` | 8 |
| ` three of pentacles` | 8 |
| ` four of pentacles` | 8 |

_(showing top 30 of 487)_

## Notes on data quality

- Source readings appear to be LLM-generated; many begin with formulaic phrases 
  like "Based on the context and the description of the card...". These are kept 
  as supplementary samples but should not be treated as authoritative interpretations.
- Source uses Marseille-tradition card names (e.g. "the popess" rather than 
  "The High Priestess"). Normalization is handled by `name_normalization.json`.
- Only Major Arcana are currently covered in our canonical `deck.json`. Minor 
  Arcana rows from the HF dataset are skipped at the canonical-match step until 
  `deck.json` is extended.
