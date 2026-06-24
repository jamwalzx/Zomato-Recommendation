import os
from pathlib import Path
import pandas as pd
from src.data.loader import load_zomato_dataset
from src.data.preprocessor import preprocess_data

def get_cache_path() -> Path:
    cache_path_str = os.getenv("DATA_CACHE_PATH", "data/processed/restaurants.parquet")
    return Path(cache_path_str)

def get_restaurants(force_refresh: bool = False) -> pd.DataFrame:
    """
    Load restaurants from parquet cache if available,
    otherwise download, preprocess, cache, and return.
    """
    cache_path = get_cache_path()
    
    if not force_refresh and cache_path.exists():
        print(f"Loading data from cache: {cache_path}")
        return pd.read_parquet(cache_path)
    
    print("Cache missing or force refresh requested. Downloading dataset...")
    df_raw = load_zomato_dataset()
    
    print("Preprocessing raw dataset...")
    df_clean = preprocess_data(df_raw)
    
    print(f"Caching preprocessed data to {cache_path}...")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_parquet(cache_path, index=False)
    
    return df_clean
