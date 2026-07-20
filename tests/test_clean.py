import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from clean import clean_and_dedupe

def test_deduplication():
    raw = [
        {'source': 'play', 'date': '2023-01-01', 'review_text': 'Great app!', 'country_code': 'IN'},
        {'source': 'play', 'date': '2023-01-01', 'review_text': 'Great app!', 'country_code': 'IN'}, # Duplicate
        {'source': 'play', 'date': '2023-01-02', 'review_text': 'Great app!', 'country_code': 'IN'}  # Different date
    ]
    cleaned, dedupe_count, _ = clean_and_dedupe(raw)
    assert len(cleaned) == 2, f"Expected 2, got {len(cleaned)}"
    assert dedupe_count == 1, f"Expected 1 duplicate, got {dedupe_count}"
    print("[PASS] test_deduplication")

def test_truncation():
    long_text = "A" * 5000
    raw = [{'source': 'play', 'date': '2023-01-01', 'review_text': long_text, 'country_code': 'IN'}]
    cleaned, _, _ = clean_and_dedupe(raw, char_limit=4000)
    assert len(cleaned[0]['review_text']) == 4000 + len("... [TRUNCATED]"), "Text not properly truncated"
    assert cleaned[0]['review_text'].endswith("... [TRUNCATED]"), "Truncation suffix missing"
    print("[PASS] test_truncation")

def test_html_stripping():
    raw = [{'source': 'play', 'date': '2023-01-01', 'review_text': '<p>Hello <b>World</b></p>', 'country_code': 'IN'}]
    cleaned, _, _ = clean_and_dedupe(raw)
    assert cleaned[0]['review_text'] == "Hello World", f"HTML not stripped correctly: {cleaned[0]['review_text']}"
    print("[PASS] test_html_stripping")

if __name__ == '__main__':
    test_deduplication()
    test_truncation()
    test_html_stripping()
    print("ALL TESTS PASSED.")
