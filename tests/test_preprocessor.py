import pandas as pd
import numpy as np
from src.data.preprocessor import clean_rate, clean_cost, get_budget_tier, parse_cuisines, preprocess_data

def test_clean_rate():
    assert clean_rate("4.1/5") == 4.1
    assert clean_rate(" 4.2 /5 ") == 4.2
    assert np.isnan(clean_rate("NEW"))
    assert np.isnan(clean_rate("-"))
    assert np.isnan(clean_rate(np.nan))

def test_clean_cost():
    assert clean_cost("800") == 800.0
    assert clean_cost("1,200") == 1200.0
    assert clean_cost(" 1,500 ") == 1500.0
    assert np.isnan(clean_cost(np.nan))

def test_get_budget_tier():
    assert get_budget_tier(400) == "low"
    assert get_budget_tier(500) == "low"
    assert get_budget_tier(800) == "medium"
    assert get_budget_tier(1500) == "medium"
    assert get_budget_tier(2000) == "high"
    assert get_budget_tier(np.nan) == "medium"

def test_parse_cuisines():
    assert parse_cuisines("North Indian, Chinese") == ["North Indian", "Chinese"]
    assert parse_cuisines("Cafe , Bakery ") == ["Cafe", "Bakery"]
    assert parse_cuisines(np.nan) == []

def test_preprocess_data():
    df_raw = pd.DataFrame({
        'name': ['Jalsa', 'Missing Loc', None, 'Dup', 'Dup', 'Bad Rate'],
        'location': [' banashankari ', None, 'BTM', 'Koramangala', 'Koramangala', 'Indiranagar'],
        'rate': ['4.1/5', '3.0/5', '4.0/5', '3.5/5', '3.5/5', 'NEW'],
        'cuisines': ['North Indian, Chinese', 'Cafe', 'South Indian', 'Italian', 'Italian', 'Continental'],
        'approx_cost(for two people)': ['800', '400', '200', '1,600', '1,600', '1,000'],
        'votes': [775, 10, 20, 100, 100, 5],
        'address': ['942, 21st Main...', '...', '...', '...', '...', '...']
    })
    
    df_clean = preprocess_data(df_raw)
    
    # Missing loc or name should be dropped. 
    # 'Bad Rate' is dropped due to 'NEW' rating.
    # Duplicates should be reduced to 1.
    # Expected rows: Jalsa, Dup
    assert len(df_clean) == 2
    
    # Verify Location normalization
    assert df_clean.iloc[0]['location'] == 'Banashankari'
    
    # Verify Budget tier
    assert df_clean.iloc[0]['budget_tier'] == 'medium'
    assert df_clean.iloc[1]['budget_tier'] == 'high'
    
    # Verify Rating float
    assert df_clean.iloc[0]['rating'] == 4.1
    
    # Verify Cuisine List
    assert df_clean.iloc[0]['cuisine_list'] == ["North Indian", "Chinese"]
