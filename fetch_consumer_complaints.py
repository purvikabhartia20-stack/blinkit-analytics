import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_cc_reviews():
    print("Fetching from ConsumerComplaints.in...")
    url = "https://www.consumercomplaints.in/grofers-b108535"
    # Spoof real browser headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    reviews = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"  - Failed to fetch ConsumerComplaints. Status: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        complaints = soup.find_all('td', class_='complaint')
        
        for comp in complaints:
            try:
                title_tag = comp.find('a', class_='complaint-title')
                if not title_tag:
                    continue
                title = title_tag.text.strip()
                link = title_tag['href']
                date_str = datetime.now().isoformat()
                
                reviews.append({
                    'source': 'consumercomplaints',
                    'source_id': link,
                    'date': date_str,
                    'rating': None,
                    'review_text': title,
                    'username': 'anonymous',
                    'country_code': 'IN'
                })
            except Exception as e:
                print(f"  - Error parsing complaint: {e}")
                
        print(f"  - Finished fetching ConsumerComplaints. Found {len(reviews)} complaints.")
        return reviews
        
    except Exception as e:
        print(f"  - ConsumerComplaints scrape failed: {e}")
        return []

if __name__ == "__main__":
    fetch_cc_reviews()
