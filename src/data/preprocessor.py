import pandas as pd
import numpy as np

def clean_rate(rate_str) -> float:
    """Convert rating string like '4.1/5' to float 4.1."""
    if pd.isna(rate_str):
        return np.nan
    rate_str = str(rate_str).strip()
    if rate_str in ('NEW', '-'):
        return np.nan
    if '/' in rate_str:
        rate_str = rate_str.split('/')[0].strip()
    try:
        return float(rate_str)
    except ValueError:
        return np.nan

def clean_cost(cost_str) -> float:
    """Convert cost string like '1,200' to float 1200.0."""
    if pd.isna(cost_str):
        return np.nan
    cost_str = str(cost_str).replace(',', '').strip()
    try:
        return float(cost_str)
    except ValueError:
        return np.nan

def get_budget_tier(cost: float) -> str:
    """Map numeric cost to a budget tier."""
    if pd.isna(cost):
        return "medium"  # Default fallback
    if cost <= 500:
        return "low"
    elif cost <= 1500:
        return "medium"
    else:
        return "high"

def parse_cuisines(cuisine_str) -> list[str]:
    """Parse comma-separated cuisines into a list of strings."""
    if pd.isna(cuisine_str):
        return []
    return [c.strip() for c in str(cuisine_str).split(',') if c.strip()]

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize the raw Zomato dataset."""
    # Map to internal field names
    df = df.rename(columns={
        'name': 'restaurant_name',
        'rate': 'rating',
        'cuisines': 'cuisine',
        'approx_cost(for two people)': 'estimated_cost_raw'
    })
    
    # 1. Handle missing data (Drop rows missing critical fields)
    df = df.dropna(subset=['restaurant_name', 'location'])
    
    # 2. Normalize location
    df['location'] = df['location'].str.strip().str.title()
    
    # 3. Clean rating
    df['rating'] = df['rating'].apply(clean_rate)
    # Drop rows without a valid rating
    df = df.dropna(subset=['rating'])
    
    # 4. Parse cuisine lists
    df['cuisine_list'] = df['cuisine'].apply(parse_cuisines)
    
    # 5. Derive numeric cost and budget_tier
    df['numeric_cost'] = df['estimated_cost_raw'].apply(clean_cost)
    df['budget_tier'] = df['numeric_cost'].apply(get_budget_tier)
    
    # Create display string for estimated cost
    def format_cost(val):
        if pd.isna(val) or str(val).lower() == 'nan':
            return "Unknown"
        return f"₹{str(val).replace('.0', '')} for two"
    
    df['estimated_cost'] = df['numeric_cost'].apply(format_cost)
    
    # 6. Deduplicate records by restaurant_name and location
    df = df.drop_duplicates(subset=['restaurant_name', 'location'], keep='first')
    
    # Filter final columns
    columns_to_keep = [
        'restaurant_name', 'location', 'cuisine', 'cuisine_list', 'rating',
        'estimated_cost', 'budget_tier', 'votes', 'address', 'numeric_cost'
    ]
    
    # Ensure all selected columns exist before filtering (some might be missing if schema differed)
    columns_present = [c for c in columns_to_keep if c in df.columns]
    
    return df[columns_present].copy()
