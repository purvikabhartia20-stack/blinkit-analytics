import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

BASE_URL = "https://www.consumercomplaints.in/grofers-b108535"
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.consumercomplaints.in/',
}


def fetch_cc_reviews(max_pages=5):
    """
    Fetch Blinkit/Grofers complaints from ConsumerComplaints.in.
    Falls back gracefully if the site blocks scraping.
    """
    print("Fetching from ConsumerComplaints.in...")
    reviews = []

    for page in range(1, max_pages + 1):
        url = BASE_URL if page == 1 else f"{BASE_URL}?page={page}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)

            if response.status_code in (403, 429):
                print(f"  ConsumerComplaints page {page}: blocked (HTTP {response.status_code}). Stopping.")
                break
            if response.status_code != 200:
                print(f"  ConsumerComplaints page {page}: HTTP {response.status_code}. Stopping.")
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try multiple known selectors
            complaint_blocks = (
                soup.find_all('td', class_='complaint') or
                soup.find_all('div', class_='complaint') or
                soup.find_all('div', class_='complaint-item') or
                soup.find_all('li', class_='complaint')
            )

            if not complaint_blocks:
                # Fallback: find any links that look like complaint titles
                links = soup.find_all('a', href=lambda h: h and '/complaints/' in h)
                if links:
                    for link in links:
                        title = link.get_text(strip=True)
                        if title and len(title) > 15:
                            reviews.append({
                                'source': 'consumercomplaints',
                                'source_id': link.get('href'),
                                'date': datetime.now().isoformat(),
                                'rating': None,
                                'review_text': title,
                                'username': 'anonymous',
                                'country_code': 'IN'
                            })
                    print(f"  ConsumerComplaints page {page}: +{len(links)} via fallback link selector.")
                else:
                    print(f"  ConsumerComplaints page {page}: No complaints found (layout may have changed).")
                    break
            else:
                page_count = 0
                for comp in complaint_blocks:
                    try:
                        title_tag = (
                            comp.find('a', class_='complaint-title') or
                            comp.find('a') or
                            comp.find('strong')
                        )
                        if not title_tag:
                            continue
                        title = title_tag.get_text(strip=True)
                        link = title_tag.get('href', '')

                        if title:
                            reviews.append({
                                'source': 'consumercomplaints',
                                'source_id': link,
                                'date': datetime.now().isoformat(),
                                'rating': None,
                                'review_text': title,
                                'username': 'anonymous',
                                'country_code': 'IN'
                            })
                            page_count += 1
                    except Exception as e:
                        print(f"  Error parsing complaint block: {e}")

                print(f"  ConsumerComplaints page {page}: +{page_count} (total: {len(reviews)})")

            time.sleep(1.5)

        except Exception as e:
            print(f"  ConsumerComplaints page {page} failed: {e}")
            break

    print(f"Completed ConsumerComplaints fetch: {len(reviews)} complaints.")
    return reviews


if __name__ == "__main__":
    fetch_cc_reviews()
