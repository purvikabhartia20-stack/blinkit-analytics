import os
import sys
import json
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from auto_tag import ReviewTag

def test_pydantic_schema():
    # Simulate a valid JSON response from Groq
    mock_json = """
    {
        "review_id": 1,
        "theme": "speed_expectation",
        "sentiment": "negative",
        "category_mentioned": "grocery",
        "behavior_signal": "repeat-only",
        "pain_point": "Late delivery",
        "unmet_need": "",
        "trust_barrier_mentioned": false,
        "trust_barrier_text": "",
        "severity": "medium",
        "key_quote": "took 30 mins instead of 10"
    }
    """
    
    # Parse and validate with Pydantic
    data = json.loads(mock_json)
    tag = ReviewTag(**data)
    
    assert tag.theme == "speed_expectation"
    assert tag.trust_barrier_mentioned is False
    assert tag.severity == "medium"
    
    print("[PASS] test_pydantic_schema: Schema successfully parsed and validated.")

if __name__ == '__main__':
    test_pydantic_schema()
