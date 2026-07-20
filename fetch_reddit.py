import requests
from bs4 import BeautifulSoup
import time
import os

def fetch_reddit_reviews():
    print("Fetching Reddit discussions via XML RSS...")
    subs = ['india', 'bangalore', 'mumbai', 'delhi']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    formatted = []
    discovery_log = []
    
    discovery_log.append("# Reddit Discovery Log\n")
    discovery_log.append("| Subreddit | Query | Status | Yield |")
    discovery_log.append("|---|---|---|---|")
    
    for sub in subs:
        url = f'https://www.reddit.com/r/{sub}/search.rss?q=blinkit&restrict_sr=on&sort=new'
        
        try:
            r = requests.get(url, headers=headers, timeout=10)
            status = r.status_code
            yield_count = 0
            
            if status == 200:
                soup = BeautifulSoup(r.content, 'xml')
                entries = soup.find_all('entry')
                
                for entry in entries:
                    title = entry.title.text if entry.title else ''
                    content = entry.content.text if entry.content else ''
                    post_id = entry.id.text if entry.id else ''
                    date = entry.updated.text if entry.updated else ''
                    
                    full_text = f"{title}\n{content}".strip()
                    
                    # Basic relevance filter: must mention blinkit
                    if 'blinkit' in full_text.lower():
                        formatted.append({
                            'source': 'reddit',
                            'source_id': post_id,
                            'date': date,
                            'rating': None, # No rating on Reddit
                            'review_text': full_text,
                            'username': 'anonymized',
                            'country_code': 'IN'
                        })
                        yield_count += 1
                        
            discovery_log.append(f"| r/{sub} | search.rss?q=blinkit | {status} | {yield_count} |")
            print(f"r/{sub} yielded {yield_count} posts.")
            
        except Exception as e:
             discovery_log.append(f"| r/{sub} | search.rss?q=blinkit | Error: {e} | 0 |")
             print(f"Error fetching Reddit r/{sub}: {e}")
             
        time.sleep(2) # Be nice to Reddit's RSS rate limits
        
    # Write discovery log
    os.makedirs('docs', exist_ok=True)
    with open('docs/reddit_discovery_log.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(discovery_log))
        
    print(f"Completed Reddit fetch: {len(formatted)} total posts.")
    return formatted
