import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_mouthshut_reviews():
    print("Fetching from MouthShut...")
    url = "https://www.mouthshut.com/product-reviews/Grofers-com-reviews-925746736"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    reviews = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"  - Failed to fetch MouthShut. Status: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        html_reviews = soup.find_all('div', class_='review-article')
        
        for rev in html_reviews:
            try:
                title_tag = rev.find('a', class_='review-title')
                content_tag = rev.find('div', class_='more reviewdata')
                
                if not title_tag:
                    continue
                
                title = title_tag.text.strip()
                content = content_tag.text.strip() if content_tag else ""
                full_text = f"{title}\n{content}"
                
                date_str = datetime.now().isoformat()
                
                reviews.append({
                    'source': 'mouthshut',
                    'source_id': None,
                    'date': date_str,
                    'rating': None,
                    'review_text': full_text,
                    'username': 'anonymous',
                    'country_code': 'IN'
                })
            except Exception as e:
                print(f"  - Error parsing MouthShut review: {e}")
                
        print(f"  - Finished fetching MouthShut. Found {len(reviews)} reviews.")
        return reviews
        
    except Exception as e:
        print(f"  - MouthShut scrape failed: {e}")
        return []

if __name__ == "__main__":
    fetch_mouthshut_reviews()
