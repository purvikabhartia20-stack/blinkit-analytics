import os
import time
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

def fetch_youtube_comments(target_count=2000, search_query="Blinkit review"):
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key or api_key == "your_youtube_api_key_here":
        print("YouTube API Key is missing. Skipping YouTube fetch.")
        return []
        
    youtube = build('youtube', 'v3', developerKey=api_key)
    all_comments = []
    
    try:
        # Search for Blinkit related videos
        print(f"Searching YouTube for: '{search_query}'")
        search_response = youtube.search().list(
            q=search_query,
            part='id,snippet',
            maxResults=10,
            type='video'
        ).execute()
        
        video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
        print(f"Found {len(video_ids)} videos. Fetching comments...")
        
        for video_id in video_ids:
            if len(all_comments) >= target_count:
                break
                
            next_page_token = None
            
            while len(all_comments) < target_count:
                try:
                    kwargs = {
                        'videoId': video_id,
                        'part': 'snippet',
                        'maxResults': 100,
                        'textFormat': 'plainText'
                    }
                    if next_page_token:
                        kwargs['pageToken'] = next_page_token
                        
                    response = youtube.commentThreads().list(**kwargs).execute()
                    
                    for item in response.get('items', []):
                        comment = item['snippet']['topLevelComment']['snippet']
                        all_comments.append({
                            'source': 'youtube',
                            'source_id': item['id'],
                            'date': comment.get('publishedAt'),
                            'rating': None, # YouTube doesn't have comment ratings
                            'review_text': comment.get('textDisplay'),
                            'username': 'anonymized',
                            'country_code': 'IN'
                        })
                        
                    next_page_token = response.get('nextPageToken')
                    if not next_page_token:
                        break
                        
                    time.sleep(0.5) # Throttle to avoid rate limit
                    
                except HttpError as e:
                    # Video might have comments disabled
                    print(f"Skipping video {video_id}: Comments disabled or API error.")
                    break
                    
    except HttpError as e:
        print(f"YouTube API Error: {e}")
        
    print(f"Completed YouTube fetch: {len(all_comments)} comments.")
    return all_comments[:target_count]

if __name__ == '__main__':
    comments = fetch_youtube_comments(target_count=50)
    for c in comments[:2]:
        print(c)
