import pandas as pd
from src.llm.parser import parse_recommendations

def test_parse_valid_json():
    candidates = pd.DataFrame({
        'restaurant_name': ['A', 'B'],
        'cuisine_list': [['Italian'], ['Chinese']],
        'rating': [4.5, 4.0],
        'estimated_cost': ['₹500', '₹300']
    })
    
    raw_json = '''
    {
        "recommendations": [
            {"rank": 1, "restaurant_name": "A", "explanation": "Good Italian"}
        ],
        "summary": "Enjoy"
    }
    '''
    
    resp = parse_recommendations(raw_json, candidates)
    assert len(resp.recommendations) == 1
    rec = resp.recommendations[0]
    assert rec.restaurant_name == "A"
    assert rec.cuisine == "Italian"
    assert rec.rating == 4.5
    assert rec.estimated_cost == "₹500"
    assert rec.explanation == "Good Italian"
    assert resp.summary == "Enjoy"
    assert resp.fallback_used is False

def test_parse_hallucination():
    candidates = pd.DataFrame({
        'restaurant_name': ['A'],
        'cuisine_list': [['Italian']],
        'rating': [4.5],
        'estimated_cost': ['₹500']
    })
    
    raw_json = '''
    {
        "recommendations": [
            {"rank": 1, "restaurant_name": "Fake", "explanation": "Hallucinated"}
        ]
    }
    '''
    
    resp = parse_recommendations(raw_json, candidates)
    # The hallucinated restaurant should be stripped
    assert len(resp.recommendations) == 0

def test_parse_invalid_json():
    candidates = pd.DataFrame({
        'restaurant_name': ['A']
    })
    resp = parse_recommendations("{bad json}", candidates)
    assert len(resp.recommendations) == 0
    assert resp.fallback_used is True
