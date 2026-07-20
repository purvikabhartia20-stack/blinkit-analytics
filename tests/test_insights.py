import os
import sqlite3
import json

def test_insights_generation():
    if not os.path.exists('insights.json'):
        print("[FAIL] insights.json does not exist")
        return
        
    with open('insights.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if len(data) != 8:
        print(f"[FAIL] Expected 8 themes in JSON, got {len(data)}")
        return
        
    print("[PASS] insights.json generated with 8 themes")
    
    conn = sqlite3.connect('blinkit_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM insights")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count != 8:
        print(f"[FAIL] Expected 8 rows in insights table, got {count}")
        return
        
    print("[PASS] insights table populated correctly")
    print("ALL TESTS PASSED.")

if __name__ == '__main__':
    test_insights_generation()
