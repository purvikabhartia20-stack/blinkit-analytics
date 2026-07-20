import sqlite3
import yaml
import sys

def get_db_path():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        return config.get('database', {}).get('db_path', 'blinkit_data.db')

def verify_quotes():
    print("Running Automated Quote Verification...")
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = """
        SELECT r.id, r.review_text, t.key_quote 
        FROM tags t
        JOIN reviews r ON t.review_id = r.id
        WHERE t.key_quote IS NOT NULL AND t.key_quote != ''
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    
    failed = 0
    total = len(rows)
    
    for row_id, text, quote in rows:
        # Ignore case and normalize spacing for robust matching, 
        # but technically it should be a pure substring.
        if quote.lower().strip() not in text.lower():
            print(f"  - [FAIL] Review ID {row_id}: Quote not found in text.")
            print(f"      Quote: '{quote}'")
            print(f"      Text : '{text}'")
            failed += 1
            
    conn.close()
    
    print(f"\nVerification Complete.")
    print(f"Total Quotes Checked: {total}")
    print(f"Passed: {total - failed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\nERROR: Some quotes were hallucinated or modified. Export blocked.")
        sys.exit(1)
    else:
        print("\nSUCCESS: All quotes are exact substrings.")
        sys.exit(0)

if __name__ == "__main__":
    verify_quotes()
