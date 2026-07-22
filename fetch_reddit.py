import requests
from bs4 import BeautifulSoup
import time
import os

# Search both brand names: "blinkit" (current) and "grofers" (legacy name still used in posts)
SEARCH_TERMS = ["blinkit", "grofers"]
SUBREDDITS = [
    'india', 'bangalore', 'mumbai', 'delhi', 'gurgaon', 'noida',
    'pune', 'hyderabad', 'chennai', 'kolkata', 'ahmedabad',
    'chandigarh', 'lucknow', 'jaipur', 'surat', 'indore'
]
# old.reddit.com RSS is more stable and less rate-limited than www.reddit.com
RSS_BASE = "https://old.reddit.com/r/{sub}/search.rss?q={term}&restrict_sr=on&sort=new"
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (compatible; BlinkitResearchBot/1.0; '
        '+https://github.com/purvikabhartia20-stack/blinkit-analytics)'
    )
}
MAX_429_RETRIES = 3
BASE_BACKOFF = 10  # seconds


def _fetch_rss(url: str) -> tuple[int, bytes | None]:
    """Fetch one RSS URL with 429-aware retry. Returns (status_code, content)."""
    backoff = BASE_BACKOFF
    for attempt in range(MAX_429_RETRIES):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 429:
                wait = int(r.headers.get('Retry-After', backoff))
                print(f"    429 on {url}. Retrying in {wait}s (attempt {attempt + 1}/{MAX_429_RETRIES})...")
                time.sleep(wait)
                backoff *= 2
                continue
            return r.status_code, r.content
        except Exception as e:
            print(f"    Network error fetching {url}: {e}")
            time.sleep(5)
    return 429, None  # all retries exhausted


def fetch_reddit_reviews():
    print("Fetching Reddit discussions via old.reddit.com RSS...")
    seen_ids = set()
    formatted = []
    discovery_log = [
        "# Reddit Discovery Log\n",
        "| Subreddit | Query | Status | Yield |",
        "|---|---|---|---|"
    ]

    for sub in SUBREDDITS:
        sub_yield = 0
        for term in SEARCH_TERMS:
            url = RSS_BASE.format(sub=sub, term=term)
            status, content = _fetch_rss(url)

            if status == 200 and content:
                soup = BeautifulSoup(content, 'xml')
                entries = soup.find_all('entry')

                for entry in entries:
                    post_id = entry.id.text if entry.id else ''
                    if post_id in seen_ids:
                        continue  # dedupe across search terms
                    seen_ids.add(post_id)

                    title = entry.title.text if entry.title else ''
                    content_tag = entry.content.text if entry.content else ''
                    date = entry.updated.text if entry.updated else ''
                    full_text = f"{title}\n{content_tag}".strip()

                    # Must mention either brand name to be relevant
                    if 'blinkit' in full_text.lower() or 'grofers' in full_text.lower():
                        formatted.append({
                            'source': 'reddit',
                            'source_id': post_id,
                            'date': date,
                            'rating': None,
                            'review_text': full_text,
                            'username': 'anonymized',
                            'country_code': 'IN'
                        })
                        sub_yield += 1

            discovery_log.append(
                f"| r/{sub} | q={term} | {status} | {sub_yield} |"
            )
            # Be polite: 2s between requests (Reddit's crawl-delay recommendation)
            time.sleep(2)

        print(f"r/{sub}: {sub_yield} relevant posts found.")

    # Write discovery log
    os.makedirs('docs', exist_ok=True)
    with open('docs/reddit_discovery_log.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(discovery_log))

    print(f"Completed Reddit fetch: {len(formatted)} total posts.")
    return formatted


if __name__ == "__main__":
    posts = fetch_reddit_reviews()
    for p in posts[:3]:
        print(p)
