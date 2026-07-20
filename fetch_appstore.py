import requests

def fetch_appstore_reviews():
    print("Fetching App Store reviews via RSS...")
    # Using the RSS endpoint verified in Phase 1
    url = 'https://itunes.apple.com/in/rss/customerreviews/id=960335206/sortBy=mostRecent/json'
    
    formatted = []
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            entries = data.get('feed', {}).get('entry', [])
            
            if not isinstance(entries, list):
                entries = [entries] if entries else []
                
            for entry in entries:
                review_id = entry.get('id', {}).get('label')
                author = 'anonymized'
                rating = entry.get('im:rating', {}).get('label')
                title = entry.get('title', {}).get('label', '')
                content = entry.get('content', {}).get('label', '')
                date = entry.get('updated', {}).get('label')
                
                full_text = f"{title}\n{content}".strip()
                
                formatted.append({
                    'source': 'app_store',
                    'source_id': review_id,
                    'date': date,
                    'rating': int(rating) if rating and rating.isdigit() else None,
                    'review_text': full_text,
                    'username': author,
                    'country_code': 'IN'
                })
    except Exception as e:
        print(f"App Store fetch error (handled gracefully): {e}")
        
    print(f"Completed App Store fetch: {len(formatted)} reviews.")
    return formatted
