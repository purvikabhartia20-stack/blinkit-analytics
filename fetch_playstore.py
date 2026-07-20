import time
from google_play_scraper import reviews, Sort

def fetch_playstore_reviews(target_count=2000):
    print("Fetching Play Store reviews...")
    all_reviews = []
    continuation_token = None
    
    # Simple exponential backoff for pagination
    retries = 3
    delay = 1
    
    while len(all_reviews) < target_count:
        try:
            result, continuation_token = reviews(
                'com.grofers.customerapp',
                lang='en',
                country='in',
                sort=Sort.NEWEST,
                count=199, # Batch size
                continuation_token=continuation_token
            )
            
            if not result:
                break
                
            all_reviews.extend(result)
            print(f"Fetched {len(all_reviews)} Play Store reviews so far...")
            
            if not continuation_token:
                break
                
            # Throttle slightly to avoid rate limits
            time.sleep(0.5)
            # Reset retries on success
            retries = 3
            delay = 1
            
        except Exception as e:
            print(f"Error fetching Play Store reviews: {e}")
            retries -= 1
            if retries <= 0:
                print("Max retries reached for Play Store. Stopping fetch.")
                break
            time.sleep(delay)
            delay *= 2
            
    # Format to uniform schema
    formatted = []
    for r in all_reviews[:target_count]:
        formatted.append({
            'source': 'play_store',
            'source_id': r.get('reviewId'),
            'date': r.get('at').isoformat() if r.get('at') else None,
            'rating': r.get('score'),
            'review_text': r.get('content'),
            'username': 'anonymized',
            'country_code': 'IN'
        })
        
    print(f"Completed Play Store fetch: {len(formatted)} reviews.")
    return formatted
