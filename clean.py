import hashlib
import re
from bs4 import BeautifulSoup
import emoji

def clean_and_dedupe(raw_reviews, char_limit=4000):
    cleaned = []
    seen_hashes = set()
    dedupe_count = 0
    emoji_only_count = 0
    
    for r in raw_reviews:
        text = r.get('review_text', '')
        if not text:
            continue
            
        # Strip HTML using BeautifulSoup safely
        if bool(BeautifulSoup(text, "html.parser").find()):
            text = BeautifulSoup(text, "html.parser").get_text(separator=" ")
            
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Check if empty or emoji-only
        text_no_emoji = emoji.replace_emoji(text, replace='').strip()
        if not text_no_emoji:
            emoji_only_count += 1
            continue
            
        # Truncate to character limit
        if len(text) > char_limit:
            text = text[:char_limit] + "... [TRUNCATED]"
            
        r['review_text'] = text
        
        # Hash for deduplication
        source_id = r.get('source_id')
        if source_id:
            hash_input = f"{r['source']}_{source_id}".encode('utf-8')
        else:
            hash_input = f"{r['source']}_{text}".encode('utf-8')
        
        record_hash = hashlib.md5(hash_input).hexdigest()
        
        if record_hash in seen_hashes:
            dedupe_count += 1
            continue
            
        seen_hashes.add(record_hash)
        r['hash'] = record_hash
        cleaned.append(r)
        
    return cleaned, dedupe_count, emoji_only_count
