import sqlite3
import os
import yaml
from groq import Groq
from pydantic import BaseModel, Field
import json
import time

class ReviewTag(BaseModel):
    review_id: int
    theme: str = Field(description="One of: q1_repeat_buying, q2_exploration_barriers, q3_discovery, q4_habits, q5_info_needed, q6_frustrations, q7_segments, q8_unmet_needs, none")
    sentiment: str = Field(description="positive, negative, or neutral")
    category_mentioned: str = Field(description="grocery, pharmacy, electronics, beauty, pet, baby, other, or none-unclear")
    behavior_signal: str = Field(description="repeat-only, attempted-new-category, abandoned-attempt, or unclear")
    pain_point: str = Field(description="Short summary of frustration, or empty string")
    unmet_need: str = Field(description="What they wish existed, or empty string")
    trust_barrier_mentioned: bool = Field(description="True if they lack trust for a category")
    trust_barrier_text: str = Field(description="Reason for lack of trust, or empty string")
    severity: str = Field(description="low, medium, or high")
    key_quote: str = Field(description="Direct quote justifying tags")

def get_db_path():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        return config.get('database', {}).get('db_path', 'blinkit_data.db')

def setup_client():
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env")
    return Groq(api_key=api_key)

def load_prompt():
    with open('prompts/tagging_prompt.md', 'r', encoding='utf-8') as f:
        return f.read()

def batch_tag_reviews(batch_size=10, limit=None):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get untagged reviews
    query = """
        SELECT id, review_text 
        FROM reviews 
        WHERE id NOT IN (SELECT review_id FROM tags)
    """
    if limit:
        query += f" LIMIT {limit}"
        
    cursor.execute(query)
    untagged = cursor.fetchall()
    
    if not untagged:
        print("No untagged reviews found.")
        return
        
    print(f"Found {len(untagged)} untagged reviews. Tagging in batches of {batch_size}...")
    
    client = setup_client()
    system_prompt = load_prompt()
    
    successful_tags = 0
    failed_tags = 0
    
    for i in range(0, len(untagged), batch_size):
        batch = untagged[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(untagged)-1)//batch_size + 1}...")
        
        for review_id, review_text in batch:
            retries = 3
            network_retries = 5
            backoff = 13
            success = False
            current_prompt = system_prompt
            
            while (retries > 0 or network_retries > 0) and not success:
                try:
                    response = client.chat.completions.create(
                        model='llama-3.3-70b-versatile',
                        messages=[
                            {"role": "system", "content": current_prompt + "\nIMPORTANT: You must return valid JSON."},
                            {"role": "user", "content": f"Review ID: {review_id}\nReview Text: {review_text}"}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.1
                    )
                    
                    try:
                        tag_data = json.loads(response.choices[0].message.content)
                    except json.JSONDecodeError as json_err:
                        # JSON Parse failure path
                        print(f"JSON Parse failed for review {review_id}: {json_err}. Retrying with stricter prompt...")
                        if retries > 1:
                            retries -= 1
                            current_prompt = system_prompt + "\n\nCRITICAL: You must return ONLY valid, well-formed JSON matching the exact schema provided. Do not include markdown code blocks, preamble, or any extra text."
                            continue
                        else:
                            print(f"Failed to parse JSON after retries for review {review_id}. Skipping.")
                            failed_tags += 1
                            break # Move to next review
                    
                    cursor.execute("""
                        INSERT INTO tags (
                            review_id, theme, sentiment, category_mentioned, behavior_signal,
                            pain_point, unmet_need, trust_barrier_mentioned, trust_barrier_text,
                            severity, key_quote
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        review_id, tag_data.get('theme', 'none'), tag_data.get('sentiment', 'neutral'), 
                        tag_data.get('category_mentioned', 'none-unclear'), tag_data.get('behavior_signal', 'unclear'), 
                        tag_data.get('pain_point', ''), tag_data.get('unmet_need', ''),
                        bool(tag_data.get('trust_barrier_mentioned', False)), tag_data.get('trust_barrier_text', ''),
                        tag_data.get('severity', 'low'), tag_data.get('key_quote', '')
                    ))
                    
                    successful_tags += 1
                    success = True
                    # No aggressive sleep needed for Groq
                    
                except Exception as e:
                    err_str = str(e).lower()
                    if '429' in err_str or 'quota' in err_str or 'exhausted' in err_str:
                        # Rate limit path
                        if retries <= 0:
                            print(f"Max rate limit retries reached for review {review_id}.")
                            failed_tags += 1
                            break
                        print(f"Rate limit hit on review {review_id}. Sleeping for {backoff} seconds...")
                        time.sleep(backoff)
                        backoff *= 2
                        retries -= 1
                    elif '11001' in err_str or 'getaddrinfo' in err_str or 'timeout' in err_str or 'connection' in err_str or 'socket' in err_str:
                        # Network error path
                        if network_retries <= 0:
                            print(f"Max network retries reached for review {review_id}.")
                            failed_tags += 1
                            break
                        print(f"Network error on review {review_id}. Retrying... ({network_retries} left)")
                        time.sleep(5) # Short wait for transient network drop
                        network_retries -= 1
                    else:
                        # Other unexpected errors
                        print(f"Unexpected error tagging review {review_id}: {e}")
                        failed_tags += 1
                        break
                        
        # Commit after every batch
        conn.commit()
        
    conn.close()
    print(f"Tagging complete. Success: {successful_tags}, Failed: {failed_tags}")

if __name__ == '__main__':
    # Limit removed for full Groq run
    batch_tag_reviews(limit=None)
