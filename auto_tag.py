import sqlite3
import os
import yaml
from groq import Groq
from pydantic import BaseModel, Field
import json
import time
import re

# Model fallback chain — ordered from most token-efficient to most capable.
# llama-3.1-8b-instant has a much higher free-tier TPD than the 70B model.
TAGGING_MODELS = [
    "llama-3.1-8b-instant",   # Primary: high TPD, fast
    "llama3-8b-8192",          # Fallback 1
    "llama-3.3-70b-versatile", # Fallback 2: most capable but lowest TPD
]

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

def _parse_wait_seconds(error_message: str) -> int:
    """Extract the wait time from a Groq rate-limit error message (e.g. 'try again in 17m16.8s')."""
    minutes = re.search(r'(\d+)m', error_message)
    seconds = re.search(r'(\d+(?:\.\d+))s', error_message)
    wait = 0
    if minutes:
        wait += int(minutes.group(1)) * 60
    if seconds:
        wait += int(float(seconds.group(1)))
    return wait if wait > 0 else 60  # default 60s if not parseable


def tag_single_review(client, review_id, review_text, system_prompt):
    """
    Tag one review with automatic model fallback and rate-limit handling.
    Returns tag_data dict on success, None on permanent failure.
    """
    model_index = 0
    network_retries = 5
    current_prompt = system_prompt
    json_retry = 0

    while model_index < len(TAGGING_MODELS):
        model = TAGGING_MODELS[model_index]
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": current_prompt + "\nIMPORTANT: You must return valid JSON."},
                    {"role": "user", "content": f"Review ID: {review_id}\nReview Text: {review_text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=512  # Keep output small to preserve daily token budget
            )

            raw = response.choices[0].message.content
            try:
                tag_data = json.loads(raw)
                return tag_data
            except json.JSONDecodeError:
                json_retry += 1
                if json_retry <= 2:
                    current_prompt = system_prompt + (
                        "\n\nCRITICAL: Return ONLY valid JSON matching the schema. "
                        "No markdown, no preamble, no extra text."
                    )
                    continue
                else:
                    print(f"  JSON parse failed 3× for review {review_id} on {model}. Trying next model.")
                    model_index += 1
                    json_retry = 0
                    current_prompt = system_prompt
                    continue

        except Exception as e:
            err_str = str(e)
            err_lower = err_str.lower()

            if '429' in err_str or 'rate_limit' in err_lower or 'quota' in err_lower or 'tpd' in err_lower:
                wait = _parse_wait_seconds(err_str)
                print(f"  Rate limit on {model} (review {review_id}). Trying next model in fallback chain...")
                # Don't sleep — just advance to next model which has fresh quota
                model_index += 1
                json_retry = 0
                if model_index >= len(TAGGING_MODELS):
                    # All models exhausted — wait for the shortest limit to reset
                    print(f"  All models rate-limited. Sleeping {wait}s before retrying from top of chain...")
                    time.sleep(wait)
                    model_index = 0  # retry from primary model

            elif any(k in err_lower for k in ['11001', 'getaddrinfo', 'timeout', 'connection', 'socket']):
                if network_retries <= 0:
                    print(f"  Max network retries for review {review_id}. Skipping.")
                    return None
                print(f"  Network error for review {review_id}. Retrying ({network_retries} left)...")
                time.sleep(5)
                network_retries -= 1

            else:
                print(f"  Unexpected error for review {review_id} on {model}: {e}")
                model_index += 1  # try next model
                if model_index >= len(TAGGING_MODELS):
                    return None

    print(f"  Permanently failed to tag review {review_id} after exhausting all models.")
    return None


def batch_tag_reviews(batch_size=10, limit=None):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get untagged reviews
    query = """
        SELECT id, review_text 
        FROM reviews 
        WHERE id NOT IN (SELECT review_id FROM tags)
        ORDER BY id
    """
    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query)
    untagged = cursor.fetchall()

    if not untagged:
        print("No untagged reviews found.")
        conn.close()
        return

    print(f"Found {len(untagged)} untagged reviews. Tagging in batches of {batch_size}...")
    print(f"Model fallback chain: {' -> '.join(TAGGING_MODELS)}")

    client = setup_client()
    system_prompt = load_prompt()

    successful_tags = 0
    failed_tags = 0
    total_batches = (len(untagged) - 1) // batch_size + 1

    for i in range(0, len(untagged), batch_size):
        batch = untagged[i:i + batch_size]
        batch_num = i // batch_size + 1
        print(f"\nBatch {batch_num}/{total_batches} — reviews {i+1} to {min(i+batch_size, len(untagged))}")

        for review_id, review_text in batch:
            tag_data = tag_single_review(client, review_id, review_text, system_prompt)

            if tag_data is None:
                failed_tags += 1
                continue

            cursor.execute("""
                INSERT INTO tags (
                    review_id, theme, sentiment, category_mentioned, behavior_signal,
                    pain_point, unmet_need, trust_barrier_mentioned, trust_barrier_text,
                    severity, key_quote
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                review_id,
                tag_data.get('theme', 'none'),
                tag_data.get('sentiment', 'neutral'),
                tag_data.get('category_mentioned', 'none-unclear'),
                tag_data.get('behavior_signal', 'unclear'),
                tag_data.get('pain_point', ''),
                tag_data.get('unmet_need', ''),
                bool(tag_data.get('trust_barrier_mentioned', False)),
                tag_data.get('trust_barrier_text', ''),
                tag_data.get('severity', 'low'),
                tag_data.get('key_quote', '')
            ))
            successful_tags += 1

        # Commit after every batch so progress is saved even if interrupted
        conn.commit()
        print(f"  Batch saved. Total: {successful_tags} tagged, {failed_tags} failed.")

    conn.close()
    print(f"\nTagging complete. Success: {successful_tags}, Failed: {failed_tags}")


if __name__ == '__main__':
    batch_tag_reviews(limit=None)
