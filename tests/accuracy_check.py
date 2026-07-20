import sqlite3
import random

def main():
    conn = sqlite3.connect('blinkit_data.db')
    c = conn.cursor()
    
    # Get 10 random tagged reviews
    c.execute("""
        SELECT r.review_text, t.theme, t.sentiment, t.category_mentioned, t.behavior_signal 
        FROM reviews r 
        JOIN tags t ON r.id = t.review_id 
        ORDER BY RANDOM() LIMIT 10
    """)
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("No tagged data found in the database. Run the pipeline first.")
        return
        
    print("=" * 60)
    print("Phase 7: Spot Check Accuracy Audit (10 Random Samples)")
    print("=" * 60)
    
    for i, (text, theme, sentiment, category, behavior) in enumerate(rows, 1):
        print(f"\n[Sample #{i}]")
        print(f"RAW TEXT : {text.encode('ascii', 'replace').decode('ascii')}")
        print(f"TAGS     : Theme={theme}, Sentiment={sentiment}, Category={category}, Behavior={behavior}")
        print("-" * 60)
        
    print("\nPlease read these 10 samples and confirm if the AI accurately captured the sentiment and theme.")
    print("Record the 'Agreement Rate' (e.g., 9/10 = 90%) in tests/test_report.md.")

if __name__ == '__main__':
    main()
