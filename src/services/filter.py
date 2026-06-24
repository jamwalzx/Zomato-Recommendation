import pandas as pd
from src.models.preferences import UserPreferences
from src.config import settings

def filter_restaurants(df: pd.DataFrame, prefs: UserPreferences) -> pd.DataFrame:
    """
    Applies deterministic filters (location, rating, cuisine, budget)
    and returns a pre-ranked set of candidates.
    """
    if df.empty:
        return df

    # 1. Location match (case-insensitive substring)
    user_loc = prefs.location.lower().strip()
    if user_loc in ["bangalore", "bengaluru", "any", "all", ""]:
        filtered = df
    else:
        loc_mask = df['location'].str.contains(user_loc, case=False, na=False)
        filtered = df[loc_mask]
        
        # Fallback: if location yields zero results, ignore location filter 
        # so we can still provide recommendations based on cuisine/budget.
        if filtered.empty:
            filtered = df

    # 2. Min rating
    filtered = filtered[filtered['rating'] >= prefs.min_rating]

    if filtered.empty:
        return filtered

    # 3. Cuisine match (case-insensitive substring on any of the restaurant's cuisines)
    user_cuisines = [c.strip().lower() for c in prefs.cuisine.split(',')]
    
    def has_cuisine(cuisines: list[str]) -> bool:
        if not isinstance(cuisines, list) or not cuisines: return False
        for uc in user_cuisines:
            if any(uc in c.lower() for c in cuisines):
                return True
        return False
    
    cuisine_filtered = filtered[filtered['cuisine_list'].apply(has_cuisine)]
    
    # Fallback: if cuisine yields zero results, ignore cuisine filter
    if not cuisine_filtered.empty:
        filtered = cuisine_filtered

    # 4. Budget (numeric cost)
    if 'numeric_cost' in filtered.columns:
        budget_filtered = filtered[filtered['numeric_cost'] <= prefs.budget]
        
        # 5. Expand budget constraint if too few results
        if len(budget_filtered) < settings.top_n:
            # allow a 50% buffer to find more options if exact budget is too tight
            budget_filtered = filtered[filtered['numeric_cost'] <= (prefs.budget * 1.5)]
            
        filtered = budget_filtered
    else:
        # Fallback if numeric_cost is missing for some reason
        pass

    if filtered.empty:
        return filtered

    # 6. Pre-ranking: sort by rating desc, then votes desc
    filtered = filtered.sort_values(by=['rating', 'votes'], ascending=[False, False])
    
    # 7. Cap at MAX_CANDIDATES
    return filtered.head(settings.max_candidates)
