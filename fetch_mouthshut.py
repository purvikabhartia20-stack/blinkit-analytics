import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

MOUTHSHUT_URL = "https://www.mouthshut.com/product-reviews/Grofers-com-reviews-925746736"
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}


def fetch_mouthshut_reviews(max_pages=5):
    print("Fetching from MouthShut (Grofers/Blinkit)...")
    reviews = []

    for page in range(1, max_pages + 1):
        url = MOUTHSHUT_URL if page == 1 else f"{MOUTHSHUT_URL}/page-{page}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 403:
                print(f"  MouthShut page {page}: 403 Forbidden (bot protection active). Stopping.")
                break
            if response.status_code != 200:
                print(f"  MouthShut page {page}: HTTP {response.status_code}. Stopping.")
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try multiple known selectors — MouthShut restructures their HTML periodically
            review_blocks = (
                soup.find_all('div', class_='review-article') or
                soup.find_all('div', class_='reviewdata') or
                soup.find_all('div', attrs={'itemprop': 'review'}) or
                soup.find_all('div', class_='review')
            )

            if not review_blocks:
                print(f"  MouthShut page {page}: No review blocks found (site layout may have changed).")
                break

            page_count = 0
            for rev in review_blocks:
                try:
                    # Title
                    title_tag = (
                        rev.find('a', class_='review-title') or
                        rev.find('strong', class_='title') or
                        rev.find('h2') or
                        rev.find('h3')
                    )
                    title = title_tag.get_text(strip=True) if title_tag else ""

                    # Body
                    body_tag = (
                        rev.find('div', class_='more reviewdata') or
                        rev.find('div', class_='reviewdata') or
                        rev.find('p', class_='review-description') or
                        rev.find('p')
                    )
                    body = body_tag.get_text(strip=True) if body_tag else ""

                    full_text = f"{title}\n{body}".strip()
                    if not full_text or full_text == title:
                        full_text = title  # at minimum store title

                    if full_text:
                        reviews.append({
                            'source': 'mouthshut',
                            'source_id': None,
                            'date': datetime.now().isoformat(),
                            'rating': None,
                            'review_text': full_text,
                            'username': 'anonymous',
                            'country_code': 'IN'
                        })
                        page_count += 1
                except Exception as e:
                    print(f"  Error parsing MouthShut review block: {e}")

            print(f"  MouthShut page {page}: +{page_count} reviews (total: {len(reviews)})")
            time.sleep(1)

        except Exception as e:
            print(f"  MouthShut page {page} fetch failed: {e}")
            break

    print(f"Completed MouthShut fetch: {len(reviews)} reviews.")
    return reviews


if __name__ == "__main__":
    fetch_mouthshut_reviews()
