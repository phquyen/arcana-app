from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Input ────────────────────────────────────────────────────────────────────

class InputRecord(BaseModel):
    name: str = Field(..., description="The person's name")
    birthday: str = Field(..., description="The person's birthday (YYYY-MM-DD)")
    card_name: str = Field(..., description="The tarot card drawn")
    card_orientation: str = Field("upright", description="upright or reversed")
    question_text: Optional[str] = Field(None, description="Optional question from the user")
    context: str = Field("general", description="general | work | family | health | finance | education | travel | entertainment")


# ── Astrology branch ──────────────────────────────────────────────────────────

class AstroFeatures(BaseModel):
    """Output of the astrology branch."""
    sun_sign: str

    # categorical features (from signs.json)
    element: str          # fire, earth, air, water
    modality: str         # cardinal, fixed, mutable
    polarity: str         # yin, yang
    ruling_planet: str    # planet that rules the sun sign
    ruling_house: str | int  # house that rules the sun sign
    symbol: str           # symbol of the sun sign
    season: str           # spring, summer, autumn, winter

    # descriptive features
    core_traits: str
    shadow_traits: str
    approach_to_decisions: str
    emotional_style: str
    stress_response: str

    # numeric feature vector for downstream ML
    feature_vector: dict[str, float] = Field(default_factory=dict)


# ── Card branch (Phase 3 placeholder) ────────────────────────────────────────

class PositionedCard(BaseModel):
    """A single card in a specific position in the spread."""
    
    # Identity
    card_id: str  # e.g. "major_16"
    name: str  # canonical name, e.g. "The Tower"
    arcana: str  # "major" or "minor"
    orientation: str  # "upright" or "reversed"
    
    # Position in spread
    position: str  # "past", "present", or "future"
    position_index: int  # 0, 1, or 2
    user_picked_slot: int  # which of the 10 face-down slots the user clicked (1-10)
    
    # Interpretation (filled by extract_card_features)
    keywords: list[str] = Field(default_factory=list)
    core_meaning: str = ""
    context_meaning: str = ""  # the meaning interpreted for the user's context


class SpreadFeatures(BaseModel):
    """Output of the cards branch — a three-card past/present/future spread."""
    
    cards: list[PositionedCard]  # always length 3, in order: past, present, future
    
    # Provenance — for reproducibility
    shuffle_seed: int  # the random seed used; lets you reproduce the shuffle
    layout: list[str]  # the 10 card names that were laid out (in order)
    user_picks: list[int]  # the 3 slot numbers the user picked (1-10)

# ── Question / NLP branch (Phase 2 placeholder) ──────────────────────────────

class QuestionFeatures(BaseModel):
    """Output of the NLP branch."""
    pass  # populated in Phase 2


# ── Derived traits (Phase 4 placeholder) ─────────────────────────────────────

class DerivedTraits(BaseModel):
    """Cross-branch derived features."""
    pass  # populated in Phase 4


# ── Top-level profile ─────────────────────────────────────────────────────────

class Profile(BaseModel):
    """A complete reading profile assembled from all branches."""
    run_id: str
    timestamp: datetime
    inputs: InputRecord
    astro: AstroFeatures
    card: SpreadFeatures
    question: Optional[QuestionFeatures] = None
    derived: DerivedTraits
