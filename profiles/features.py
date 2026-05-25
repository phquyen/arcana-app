"""
Builds the full AstroFeatures object from a birthday.

This is the public interface of the astro branch. Other parts of the
pipeline import only `extract_astro_features` and don't care how it works.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from birthday_sign_connect import sun_sign_from_birthday
from data import SIGNS_DATA
from schema import AstroFeatures


def extract_astro_features(birthday: str) -> AstroFeatures:
    """
    Run the full astrology analysis for a given birthday.
    
    Args:
        birthday: ISO date "YYYY-MM-DD"
    
    Returns:
        Populated AstroFeatures object.
    """
    # Step 1: birthday -> sign name
    sign_name = sun_sign_from_birthday(birthday)
    
    # Step 2: sign name -> raw data from dataset
    sign_data = SIGNS_DATA[sign_name]
    
    # Step 3: build the numeric feature vector for downstream ML
    feature_vector = _build_feature_vector(sign_data)
    
    # Step 4: assemble the AstroFeatures object
    return AstroFeatures(
        sun_sign=sign_name,
        element=sign_data["element"],
        modality=sign_data["modality"],
        polarity=sign_data["polarity"],
        ruling_planet=sign_data["ruling_planet"],
        ruling_house=sign_data["ruling_house"],
        symbol=sign_data["symbol"],
        season=sign_data["season"],
        core_traits=sign_data["core_traits"],
        shadow_traits=sign_data["shadow_traits"],
        approach_to_decisions=sign_data["approach_to_decisions"],
        emotional_style=sign_data["emotional_style"],
        stress_response=sign_data["stress_response"],
        feature_vector=feature_vector,
    )


def _build_feature_vector(sign_data: dict) -> dict[str, float]:
    """
    Convert categorical sign attributes into a numeric feature vector
    suitable for similarity computations and downstream ML.
    
    Uses one-hot encoding: each possible value becomes its own dimension
    with value 1.0 if present, 0.0 otherwise.
    """
    vector = {}
    
    # One-hot encode element
    for element in ["fire", "earth", "air", "water"]:
        vector[f"element_{element}"] = 1.0 if sign_data["element"] == element else 0.0
    
    # One-hot encode modality
    for modality in ["cardinal", "fixed", "mutable"]:
        vector[f"modality_{modality}"] = 1.0 if sign_data["modality"] == modality else 0.0
    
    # One-hot encode polarity
    for polarity in ["yin", "yang"]:
        vector[f"polarity_{polarity}"] = 1.0 if sign_data["polarity"] == polarity else 0.0
    
    # Season as one-hot
    for season in ["spring", "summer", "autumn", "winter"]:
        vector[f"season_{season}"] = 1.0 if sign_data["season"] == season else 0.0
    
    return vector