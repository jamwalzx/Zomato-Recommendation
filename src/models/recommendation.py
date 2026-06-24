from pydantic import BaseModel, Field

class Recommendation(BaseModel):
    rank: int = Field(..., description="Rank of the recommendation (1-based)")
    restaurant_name: str = Field(..., description="Name of the restaurant")
    cuisine: str = Field(..., description="Cuisines served")
    rating: float = Field(..., description="Restaurant rating out of 5")
    estimated_cost: str = Field(..., description="Estimated cost display string")
    explanation: str = Field(..., description="AI-generated explanation for why this was recommended")

class RecommendationResponse(BaseModel):
    recommendations: list[Recommendation] = Field(default_factory=list, description="List of ranked recommendations")
    summary: str | None = Field(default=None, description="Optional summary of the recommendations")
    total_candidates_considered: int = Field(..., description="Number of candidates filtered before ranking")
    fallback_used: bool = Field(default=False, description="Whether fallback ranking was used due to LLM failure")
