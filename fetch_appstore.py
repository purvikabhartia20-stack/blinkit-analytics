import requests
import time

# Blinkit App Store ID for India: 960335206
BLINKIT_APP_ID = "960335206"

def fetch_appstore_reviews(max_pages=10):
    """
    Fetches App Store reviews using the public iTunes RSS endpoint.
    Each page returns up to 50 reviews; we paginate up to max_pages.
    """
    print("Fetching App Store reviews via iTunes RSS (paginated)...")
    formatted = []

    for page in range(1, max_pages + 1):
        url = (
            f"https://itunes.apple.com/in/rss/customerreviews/"
            f"page={page}/id={BLINKIT_APP_ID}/sortby=mostrecent/json"
        )
        try:
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                print(f"  App Store page {page}: HTTP {r.status_code}. Stopping pagination.")
                break

            data = r.json()
            entries = data.get('feed', {}).get('entry', [])

            if not isinstance(entries, list):
                entries = [entries] if entries else []

            # First entry on page 1 is app metadata, not a review
            if page == 1 and entries and 'im:rating' not in entries[0]:
                entries = entries[1:]

            if not entries:
                print(f"  App Store page {page}: No more entries. Stopping.")
                break

            for entry in entries:
                review_id = entry.get('id', {}).get('label')
                rating = entry.get('im:rating', {}).get('label')
                title = entry.get('title', {}).get('label', '')
                content = entry.get('content', {}).get('label', '')
                date = entry.get('updated', {}).get('label')
                full_text = f"{title}\n{content}".strip()

                if full_text:
                    formatted.append({
                        'source': 'app_store',
                        'source_id': review_id,
                        'date': date,
                        'rating': int(rating) if rating and str(rating).isdigit() else None,
                        'review_text': full_text,
                        'username': 'anonymized',
                        'country_code': 'IN'
                    })

            print(f"  App Store page {page}: +{len(entries)} reviews (total so far: {len(formatted)})")
            time.sleep(0.5)  # polite pause

        except Exception as e:
            print(f"  App Store page {page} error: {e}")
            break

    print(f"Completed App Store fetch: {len(formatted)} reviews.")
    return formatted


if __name__ == "__main__":
    reviews = fetch_appstore_reviews()
    for r in reviews[:3]:
        print(r)
