import uuid
import argparse
import json
from datetime import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import (
    Profile, InputRecord, AstroFeatures, CardFeatures,
    QuestionFeatures, DerivedTraits,
)
from features import extract_astro_features


# ── Core builder ──────────────────────────────────────────────────────────────

def build_profile(
    name: str,
    birthday: str,
    card_name: str,
    card_orientation: str = "upright",
    question_text: str | None = None,
    context: str = "general",
) -> Profile:

    # Step 1: preserve the raw user inputs
    inputs = InputRecord(
        name=name,
        birthday=birthday,
        card_name=card_name,
        card_orientation=card_orientation,
        question_text=question_text,
        context=context,
    )

    # Step 2: run Branch A (astrology) — DONE
    astro = extract_astro_features(birthday)

    # Step 3: run Branch B (cards) — placeholder until Phase 3
    card = CardFeatures(
        name=card_name,
        orientation=card_orientation,
        arcana="PLACEHOLDER",
    )

    # Step 4: run Branch C (text NLP) — placeholder until Phase 2
    question = QuestionFeatures() if question_text else None

    # Step 5: compute derived traits — placeholder until Phase 4
    derived = DerivedTraits()

    # Step 6: assemble and return the Profile
    return Profile(
        run_id=str(uuid.uuid4())[:8],
        timestamp=datetime.now(),
        inputs=inputs,
        astro=astro,
        card=card,
        question=question,
        derived=derived,
    )


# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="builder",
        description="Build an Arcana reading profile from the command line.",
    )
    parser.add_argument("--name",        required=True,  help="Person's name")
    parser.add_argument("--birthday",    required=True,  help="Birthday (YYYY-MM-DD)")
    parser.add_argument("--card",        required=True,  help="Tarot card name, e.g. 'The Moon'")
    parser.add_argument("--orientation", default="upright",
                        choices=["upright", "reversed"],
                        help="Card orientation (default: upright)")
    parser.add_argument("--question",    default=None,   help="Optional question text")
    parser.add_argument("--context",     default="general",
                        choices=["general","work","family","health","finance","education","travel","entertainment"],
                        help="Reading context (default: general)")
    parser.add_argument("--json",        action="store_true",
                        help="Output raw JSON instead of pretty-printed summary")

    args = parser.parse_args()

    profile = build_profile(
        name=args.name,
        birthday=args.birthday,
        card_name=args.card,
        card_orientation=args.orientation,
        question_text=args.question,
        context=args.context,
    )

    if args.json:
        print(profile.model_dump_json(indent=2))
    else:
        a = profile.astro
        sep = "-" * 50
        print(f"\n{sep}")
        print(f"  Arcana Profile  |  run {profile.run_id}")
        print(sep)
        print(f"  Name      : {profile.inputs.name}")
        print(f"  Birthday  : {profile.inputs.birthday}")
        print(f"  Sun Sign  : {a.sun_sign}  ({a.symbol})")
        print(f"  Element   : {a.element}   Modality : {a.modality}   Polarity : {a.polarity}")
        print(f"  Ruling    : {a.ruling_planet} / House {a.ruling_house}")
        print(f"  Season    : {a.season}")
        print(f"\n  Core traits      : {a.core_traits}")
        print(f"  Shadow traits    : {a.shadow_traits}")
        print(f"  Decisions        : {a.approach_to_decisions}")
        print(f"  Emotional style  : {a.emotional_style}")
        print(f"  Stress response  : {a.stress_response}")
        print(f"\n  Card      : {profile.inputs.card_name} ({profile.inputs.card_orientation})")
        print(f"  Context   : {profile.inputs.context}")
        if profile.inputs.question_text:
            print(f"  Question  : {profile.inputs.question_text}")
        print(f"{sep}\n")


if __name__ == "__main__":
    main()
