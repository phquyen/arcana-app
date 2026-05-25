from datetime import datetime
from typing import Optional 
from pydantic import BaseModel, Field

# input personal information
class InputRecord(BaseModel):
    name: str = Field(..., description="The person's name")
    age: int = Field(..., description="The person's age")
    birthday: datetime = Field(..., description="The person's birthday") # format: YYYY-MM-DD
    question_text: Optional[str] = Field(None, description="The question text to ask the person") 
    context: str = "general" # button option general, work, family, health, finance, education, travel, entertainment


# astro feature 
class AstroFeature(BaseModel):
    '''
    Output of the astrology branch 
    '''
    sun_sign: str 

    # categorical features (from signs.json)
    element: str # fire, earch, air, water
    modelity: str # cardinal, fixed, mutable
    polarity: str # yin, yang
    ruling_planet: str # the planet that rules the sun sign
    ruling_house: str # the house that rules the sun sign
    sympoly: str # the symbol of the sun sign
    season: str # the season of the sun sign 

    # descriptive features
    core_straits: str 
    shadow_traits: str
    approach_to_decisions: str
    emotional_style: str 
    stress_response: str

    # numberic feature 
    feature_vector: dict[str, float] = Field(default_factory=dict)


