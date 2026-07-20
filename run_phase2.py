import sqlite3
import yaml
from fetch_playstore import fetch_playstore_reviews
from fetch_appstore import fetch_appstore_reviews
from fetch_reddit import fetch_reddit_reviews
from fetch_youtube import fetch_youtube_comments
from fetch_consumer_complaints import fetch_cc_reviews
from fetch_mouthshut import fetch_mouthshut_reviews
from clean import clean_and_dedupe

def get_db_path():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        return config.get('database', {}).get('db_path', 'blinkit_data.db')

def store_reviews(reviews):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=10)
    cursor = conn.cursor()
    
    inserted = 0
    for r in reviews:
        try:
            cursor.execute("""
                INSERT INTO reviews (source, source_id, date, rating, review_text, username, country_code, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r['source'], r['source_id'], r['date'], r['rating'], 
                r['review_text'], r['username'], r['country_code'], r['hash']
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            pass # Already exists in DB
            
    conn.commit()
    conn.close()
    return inserted

def main():
    print("Starting Phase 2: Scrapers & Database Population")
    
    playstore_data = fetch_playstore_reviews(target_count=50) # Target lowered for fast test execution, but adjustable
    appstore_data = fetch_appstore_reviews()
    reddit_data = fetch_reddit_reviews()
    youtube_data = fetch_youtube_comments()
    cc_data = fetch_cc_reviews()
    mouthshut_data = fetch_mouthshut_reviews()
    
    all_raw = playstore_data + appstore_data + reddit_data + youtube_data + cc_data + mouthshut_data
    print(f"\nTotal raw pulled: {len(all_raw)}")
    
    cleaned_data, dedupe_count, emoji_only_count = clean_and_dedupe(all_raw)
    
    print(f"\nCleaning Report:")
    print(f"- Cleaned and kept: {len(cleaned_data)}")
    print(f"- Removed as duplicates: {dedupe_count}")
    print(f"- Removed as emoji-only/empty: {emoji_only_count}")
    
    inserted = store_reviews(cleaned_data)
    print(f"\nDatabase Storage:")
    print(f"- Successfully inserted into DB: {inserted}")
    print(f"- Skipped (already in DB): {len(cleaned_data) - inserted}")
    
    print("\nPhase 2 Complete. Review docs/reddit_discovery_log.md for yield details.")

if __name__ == '__main__':
    main()
