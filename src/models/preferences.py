from pydantic import BaseModel, Field
from typing import Literal

class UserPreferences(BaseModel):
    location: str = Field(..., min_length=1, description="City or area to search in")
    budget: int = Field(..., description="Desired maximum budget in INR")
    cuisine: str = Field(..., min_length=1, description="Desired cuisine")
    min_rating: float = Field(..., ge=0.0, le=5.0, description="Minimum rating out of 5")
    additional_preferences: str | None = Field(default=None, description="Optional free-text preferences")
