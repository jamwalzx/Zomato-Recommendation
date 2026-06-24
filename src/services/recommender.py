import pandas as pd
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResponse, Recommendation
from src.llm.client import GroqClient
from src.llm.prompts import SYSTEM_PROMPT, build_user_prompt
from src.llm.parser import parse_recommendations
import logging

logger = logging.getLogger(__name__)

def generate_fallback_recommendations(candidates_df: pd.DataFrame) -> RecommendationResponse:
    """Provides rule-based ranking if the LLM fails."""
    top_candidates = candidates_df.head(5)
    
    recs = []
    for idx, row in enumerate(top_candidates.itertuples(), 1):
        cuisine_list = getattr(row, "cuisine_list", [])
        cuisine_str = ", ".join(cuisine_list) if isinstance(cuisine_list, list) else str(getattr(row, "cuisine", ""))
        
        recs.append(Recommendation(
            rank=idx,
            restaurant_name=row.restaurant_name,
            cuisine=cuisine_str,
            rating=float(row.rating),
            estimated_cost=str(getattr(row, "estimated_cost", "N/A")),
            explanation=f"Top rated choice in {row.location} matching your filters."
        ))
        
    return RecommendationResponse(
        recommendations=recs,
        summary="We are experiencing high traffic. Here are our top deterministic picks based on your filters.",
        total_candidates_considered=len(candidates_df),
        fallback_used=True
    )

def get_llm_recommendations(
    prefs: UserPreferences, 
    candidates_df: pd.DataFrame,
    client: GroqClient | None = None
) -> RecommendationResponse:
    """Wires together prompts, LLM client, and parser."""
    if candidates_df.empty:
        return RecommendationResponse(
            recommendations=[],
            summary="No matching restaurants found for your criteria.",
            total_candidates_considered=0,
            fallback_used=False
        )
        
    client = client or GroqClient()
    user_prompt = build_user_prompt(prefs, candidates_df)
    
    try:
        raw_json = client.generate_recommendations(SYSTEM_PROMPT, user_prompt)
        response = parse_recommendations(raw_json, candidates_df)
        
        # If parser stripped out everything due to hallucinations, mark fallback
        if not response.recommendations:
            logger.warning("All LLM recommendations were invalid. Falling back.")
            raise ValueError("Invalid LLM outputs")
            
        return response
    except Exception as e:
        logger.error(f"Recommender failed: {str(e)}")
        # Fallback to top 5 candidates
        return generate_fallback_recommendations(candidates_df)
