import json
import logging
import pandas as pd
from src.models.recommendation import Recommendation, RecommendationResponse

logger = logging.getLogger(__name__)

def parse_recommendations(
    raw_json: str, 
    candidates_df: pd.DataFrame
) -> RecommendationResponse:
    """
    Parses LLM JSON, guards against hallucinations by validating names against
    the candidates DataFrame, and enriches recommendations with metadata.
    """
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON: {e}")
        return RecommendationResponse(
            recommendations=[],
            summary=None,
            total_candidates_considered=len(candidates_df),
            fallback_used=True
        )

    recommendations_data = data.get("recommendations", [])
    summary = data.get("summary")
    
    parsed_recommendations = []
    
    # Create lookup dict for enrichment and hallucination check
    candidate_lookup = candidates_df.set_index('restaurant_name').to_dict('index')
    
    for item in recommendations_data:
        name = item.get("restaurant_name")
        if not name or name not in candidate_lookup:
            logger.warning(f"Hallucination or missing name detected: {name}. Skipping.")
            continue
            
        candidate_info = candidate_lookup[name]
        
        # We need cuisine, rating, estimated_cost as strings
        cuisine_list = candidate_info.get("cuisine_list", [])
        cuisine_str = ", ".join(cuisine_list) if isinstance(cuisine_list, list) else str(candidate_info.get("cuisine", ""))
        
        try:
            rec = Recommendation(
                rank=item.get("rank", len(parsed_recommendations) + 1),
                restaurant_name=name,
                cuisine=cuisine_str,
                rating=float(candidate_info.get("rating", 0.0)),
                estimated_cost=str(candidate_info.get("estimated_cost", "N/A")),
                explanation=item.get("explanation", "Recommended based on your preferences.")
            )
            parsed_recommendations.append(rec)
        except Exception as e:
            logger.warning(f"Failed to build recommendation for {name}: {e}")
            
    # Sort by rank
    parsed_recommendations.sort(key=lambda x: x.rank)
    
    return RecommendationResponse(
        recommendations=parsed_recommendations,
        summary=summary,
        total_candidates_considered=len(candidates_df),
        fallback_used=False
    )
