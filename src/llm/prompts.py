import json
import pandas as pd
from src.models.preferences import UserPreferences

SYSTEM_PROMPT = """You are an expert restaurant recommendation assistant. 
Given a user's preferences and a specific list of candidate restaurants, your task is to rank the top 5 best matches from the list and provide a short, personalized explanation for each.

CRITICAL CONSTRAINTS:
1. ONLY recommend restaurants from the provided candidate list. DO NOT hallucinate or invent restaurants.
2. Output MUST be valid JSON matching the exact schema requested.
3. Incorporate the user's "additional_preferences" in your ranking and explanations if provided.
4. Do NOT include fields like ratings, cuisines, or costs in your JSON output. You are ONLY generating the rank, name, and explanation. The system will merge the rest.

EXPECTED JSON SCHEMA:
{
  "recommendations": [
    {
      "rank": 1,
      "restaurant_name": "Exact Name from Candidates",
      "explanation": "Why this matches their preferences..."
    }
  ],
  "summary": "A brief 1-2 sentence overview of the top picks."
}
"""

def build_candidate_json(df: pd.DataFrame) -> str:
    """Serializes the candidate dataframe into a compact JSON string for the LLM."""
    if df.empty:
        return "[]"
    
    # Keep only essential columns to save tokens
    essential_cols = ['restaurant_name', 'cuisine', 'rating', 'estimated_cost', 'location']
    candidates = df[essential_cols].to_dict(orient='records')
    return json.dumps(candidates, indent=2)

def build_user_prompt(prefs: UserPreferences, df_candidates: pd.DataFrame) -> str:
    """Builds the prompt string injecting user preferences and candidates."""
    candidates_json = build_candidate_json(df_candidates)
    
    prompt = f"""USER PREFERENCES:
- Location: {prefs.location}
- Cuisine: {prefs.cuisine}
- Budget Tier: {prefs.budget}
- Minimum Rating: {prefs.min_rating}
- Additional Preferences: {prefs.additional_preferences or 'None'}

CANDIDATE RESTAURANTS (Rank up to 5 from this list):
{candidates_json}
"""
    return prompt
