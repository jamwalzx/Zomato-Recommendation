import pandas as pd
from src.models.preferences import UserPreferences
from src.services.filter import filter_restaurants
from src.config import settings

def test_filter_location():
    df = pd.DataFrame({
        'restaurant_name': ['A', 'B'],
        'location': ['Bangalore South', 'North Bangalore'],
        'rating': [4.5, 4.5],
        'cuisine_list': [['Italian'], ['Italian']],
        'budget_tier': ['medium', 'medium'],
        'votes': [100, 100]
    })
    prefs = UserPreferences(location='south', budget='medium', cuisine='Italian', min_rating=4.0)
    res = filter_restaurants(df, prefs)
    assert len(res) == 1
    assert res.iloc[0]['restaurant_name'] == 'A'

def test_filter_min_rating():
    df = pd.DataFrame({
        'restaurant_name': ['A', 'B'],
        'location': ['City', 'City'],
        'rating': [3.5, 4.8],
        'cuisine_list': [['Chinese'], ['Chinese']],
        'budget_tier': ['low', 'low'],
        'votes': [100, 100]
    })
    prefs = UserPreferences(location='City', budget='low', cuisine='Chinese', min_rating=4.0)
    res = filter_restaurants(df, prefs)
    assert len(res) == 1
    assert res.iloc[0]['restaurant_name'] == 'B'

def test_filter_cuisine():
    df = pd.DataFrame({
        'restaurant_name': ['A', 'B'],
        'location': ['City', 'City'],
        'rating': [4.5, 4.5],
        'cuisine_list': [['Indian', 'Chinese'], ['Italian']],
        'budget_tier': ['low', 'low'],
        'votes': [100, 100]
    })
    prefs = UserPreferences(location='City', budget='low', cuisine='chinese', min_rating=4.0)
    res = filter_restaurants(df, prefs)
    assert len(res) == 1
    assert res.iloc[0]['restaurant_name'] == 'A'

def test_filter_budget_expansion():
    df = pd.DataFrame({
        'restaurant_name': ['A', 'B', 'C'],
        'location': ['City', 'City', 'City'],
        'rating': [4.5, 4.5, 4.5],
        'cuisine_list': [['Cafe'], ['Cafe'], ['Cafe']],
        'budget_tier': ['high', 'medium', 'low'], 
        'votes': [100, 100, 100]
    })
    # Want high, but only 1 candidate in high. top_n is 5, so it should expand to adjacent (medium)
    prefs = UserPreferences(location='City', budget='high', cuisine='Cafe', min_rating=4.0)
    res = filter_restaurants(df, prefs)
    assert len(res) == 2
    assert set(res['restaurant_name']) == {'A', 'B'}

def test_pre_ranking_and_cap():
    data = []
    for i in range(25):
        data.append({
            'restaurant_name': f'R{i}',
            'location': 'City',
            'rating': 4.0 + (i % 10) * 0.1, # 4.0 to 4.9
            'cuisine_list': ['Cafe'],
            'budget_tier': 'medium',
            'votes': i * 10
        })
    df = pd.DataFrame(data)
    prefs = UserPreferences(location='City', budget='medium', cuisine='Cafe', min_rating=4.0)
    res = filter_restaurants(df, prefs)
    
    # Cap at MAX_CANDIDATES
    assert len(res) == settings.max_candidates
    
    # Top ranked should be highest rating
    assert res.iloc[0]['rating'] >= res.iloc[1]['rating']

def test_empty_results():
    df = pd.DataFrame({
        'restaurant_name': ['A'],
        'location': ['City'],
        'rating': [4.5],
        'cuisine_list': [['Cafe']],
        'budget_tier': ['medium'],
        'votes': [100]
    })
    # Impossible filters
    prefs = UserPreferences(location='Nowhere', budget='high', cuisine='Mexican', min_rating=5.0)
    res = filter_restaurants(df, prefs)
    assert res.empty
