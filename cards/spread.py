"""
The spread drawing logic.

Two responsibilities:
  1. Lay out 10 face-down cards from a shuffled deck.
  2. Given 3 user picks, turn them into 3 positioned cards (past/present/future)
     each with a random orientation.

This file does NOT load card meanings or do any interpretation — that's the
job of features.py. Spread.py is just about the mechanical act of drawing.
"""

import json
import random
from pathlib import Path


# Path to deck.json — relative to this file
_DECK_PATH = Path(__file__).parent / "deck.json"


def load_deck() -> list[dict]:
    """Load the canonical deck. Returns the list of card dicts."""
    with open(_DECK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["cards"]


def shuffle_and_lay_out(
    deck: list[dict],
    num_cards: int = 10,
    seed: int | None = None,
) -> tuple[list[dict], int]:
    """
    Shuffle the deck and return the first `num_cards` cards as the layout.
    
    Args:
        deck: list of card dicts from deck.json
        num_cards: how many cards to show face-down (default 10)
        seed: if provided, makes shuffle reproducible. If None, generates one.
    
    Returns:
        (layout, used_seed)
        - layout: list of `num_cards` card dicts (the face-down spread)
        - used_seed: the seed that was used (so the result can be reproduced)
    """
    if seed is None:
        seed = random.randint(0, 2**31 - 1)
    
    rng = random.Random(seed)
    shuffled = list(deck)  # copy so we don't mutate the original
    rng.shuffle(shuffled)
    
    layout = shuffled[:num_cards]
    return layout, seed


def apply_user_picks(
    layout: list[dict],
    picks: list[int],
    seed: int,
) -> list[dict]:
    """
    Turn user's slot picks into a structured 3-card past/present/future result.
    
    Args:
        layout: the 10 face-down cards (from shuffle_and_lay_out)
        picks: list of 3 slot numbers picked by user (1-10, in order chosen)
        seed: the shuffle seed (used to also seed orientation randomness deterministically)
    
    Returns:
        List of 3 dicts, one per position. Each contains:
            - card: the card dict from deck.json
            - orientation: "upright" or "reversed"
            - position: "past", "present", or "future"
            - position_index: 0, 1, or 2
            - user_picked_slot: which slot (1-10) the user clicked
    """
    if len(picks) != 3:
        raise ValueError(f"Expected exactly 3 picks, got {len(picks)}")
    
    if len(set(picks)) != 3:
        raise ValueError(f"Picks must be unique, got {picks}")
    
    for p in picks:
        if not (1 <= p <= len(layout)):
            raise ValueError(f"Pick {p} out of range; layout has {len(layout)} slots")
    
    # Orientation randomness uses the same seed so the whole reading is reproducible
    rng = random.Random(seed + 1)  # +1 to decouple from the shuffle randomness
    
    positions = ["past", "present", "future"]
    result = []
    for i, slot in enumerate(picks):
        card = layout[slot - 1]  # slots are 1-indexed for UX
        orientation = "upright" if rng.random() < 0.7 else "reversed"
        # 70% upright, 30% reversed — matches traditional tarot probability
        
        result.append({
            "card": card,
            "orientation": orientation,
            "position": positions[i],
            "position_index": i,
            "user_picked_slot": slot,
        })
    
    return result


def draw_spread(
    picks: list[int] | None = None,
    seed: int | None = None,
) -> dict:
    """
    Top-level helper: do the whole draw in one call.
    
    Args:
        picks: list of 3 slot numbers (1-10). If None, randomly picks 3 slots
               (useful for testing).
        seed: optional seed for reproducibility.
    
    Returns:
        Dict with keys:
            - layout: list of 10 card dicts
            - picks: the 3 slot numbers used
            - cards: list of 3 positioned-card dicts
            - seed: the seed used
    """
    deck = load_deck()
    layout, used_seed = shuffle_and_lay_out(deck, num_cards=10, seed=seed)
    
    if picks is None:
        # For testing: simulate random picks
        rng = random.Random(used_seed + 2)
        picks = rng.sample(range(1, 11), 3)
    
    positioned = apply_user_picks(layout, picks, used_seed)
    
    return {
        "layout": layout,
        "picks": picks,
        "cards": positioned,
        "seed": used_seed,
    }