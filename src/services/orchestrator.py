import logging
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from src.services.filter import filter_restaurants
from src.services.recommender import get_llm_recommendations
from src.data.store import get_restaurants

logger = logging.getLogger(__name__)

def get_recommendations(prefs: UserPreferences) -> RecommendationResponse:
    """
    Orchestrates the entire recommendation pipeline:
    1. Loads dataset
    2. Filters based on preferences
    3. Calls the LLM recommender engine
    """
    logger.info(f"Received request for {prefs.location}, budget: {prefs.budget}, cuisine: {prefs.cuisine}")
    
    # Load processed data
    df = get_restaurants()
    
    if df.empty:
        logger.warning("Dataset is empty or failed to load.")
        return RecommendationResponse(
            recommendations=[],
            summary="Our restaurant database is currently unavailable.",
            total_candidates_considered=0,
            fallback_used=True
        )
        
    # Apply hard filters
    filtered_df = filter_restaurants(df, prefs)
    
    if filtered_df.empty:
        logger.info("No candidates found after filtering.")
        return RecommendationResponse(
            recommendations=[],
            summary="We couldn't find any restaurants matching your exact filters. Try relaxing your budget or minimum rating.",
            total_candidates_considered=0,
            fallback_used=False
        )
        
    # Get LLM recommendations
    return get_llm_recommendations(prefs, filtered_df)
