import sqlite3
import os
import yaml
from groq import Groq
from pydantic import BaseModel, Field
import json
import time
import re


def load_config() -> dict:
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)


def get_db_path(config: dict) -> str:
    return config.get('database', {}).get('db_path', 'blinkit_data.db')


def get_tagging_models(config: dict) -> list[str]:
    """Build the full fallback chain: primary model + fallbacks from config."""
    groq_cfg = config.get('groq', {})
    primary = groq_cfg.get('tagging_model', 'llama-3.1-8b-instant')
    fallbacks = groq_cfg.get('tagging_fallback_models', [
        'llama3-8b-8192',
        'openai/gpt-oss-20b',
        'llama-3.3-70b-versatile',
    ])
    # Dedupe while preserving order
    seen = set()
    chain = []
    for m in [primary] + fallbacks:
        if m not in seen:
            seen.add(m)
            chain.append(m)
    return chain


class ReviewTag(BaseModel):
    review_id: int
    theme: str = Field(description=(
        "One of: q1_repeat_buying, q2_exploration_barriers, q3_discovery, "
        "q4_habits, q5_info_needed, q6_frustrations, q7_segments, q8_unmet_needs, none"
    ))
    sentiment: str = Field(description="positive, negative, or neutral")
    category_mentioned: str = Field(description=(
        "grocery, pharmacy, electronics, beauty, pet, baby, snacks, "
        "apparel, other, or none-unclear"
    ))
    behavior_signal: str = Field(description=(
        "repeat-only, attempted-new-category, abandoned-attempt, or unclear"
    ))
    pain_point: str = Field(description="Short summary of frustration, or empty string")
    unmet_need: str = Field(description="What they wish existed, or empty string")
    trust_barrier_mentioned: bool = Field(description="True if they lack trust for a category")
    trust_barrier_text: str = Field(description="Reason for lack of trust, or empty string")
    severity: str = Field(description="low, medium, or high")
    key_quote: str = Field(description="Direct quote justifying tags")


def setup_client() -> Groq:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env")
    return Groq(api_key=api_key)


def load_prompt() -> str:
    with open('prompts/tagging_prompt.md', 'r', encoding='utf-8') as f:
        return f.read()


def _parse_wait_seconds(error_message: str) -> int:
    """Extract the suggested wait time from a Groq rate-limit error (e.g. 'try again in 17m16.8s')."""
    minutes = re.search(r'(\d+)m', error_message)
    seconds = re.search(r'(\d+(?:\.\d+))s', error_message)
    wait = 0
    if minutes:
        wait += int(minutes.group(1)) * 60
    if seconds:
        wait += int(float(seconds.group(1)))
    return wait if wait > 0 else 60  # safe default


def tag_single_review(client, review_id, review_text, system_prompt, model_chain: list[str]) -> dict | None:
    """
    Tag one review with automatic model fallback and rate-limit handling.
    Returns a tag_data dict on success, None on permanent failure.
    """
    model_index = 0
    network_retries = 5
    current_prompt = system_prompt
    json_retry = 0

    while model_index < len(model_chain):
        model = model_chain[model_index]
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": current_prompt + "\nIMPORTANT: You must return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": f"Review ID: {review_id}\nReview Text: {review_text}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=512  # compact output conserves daily token budget
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
                        "No markdown fences, no preamble, no trailing text."
                    )
                    continue
                else:
                    print(f"  JSON parse failed 3x for review {review_id} on {model}. Trying next model.")
                    model_index += 1
                    json_retry = 0
                    current_prompt = system_prompt
                    continue

        except Exception as e:
            err_str = str(e)
            err_lower = err_str.lower()

            if '429' in err_str or 'rate_limit' in err_lower or 'quota' in err_lower or 'tpd' in err_lower:
                wait = _parse_wait_seconds(err_str)
                model_index += 1
                json_retry = 0
                if model_index >= len(model_chain):
                    # All models exhausted — sleep the actual suggested wait, then restart chain
                    print(
                        f"  All models rate-limited for review {review_id}. "
                        f"Sleeping {wait}s then retrying from top of chain..."
                    )
                    time.sleep(wait)
                    model_index = 0
                else:
                    print(
                        f"  Rate limit on {model} (review {review_id}). "
                        f"Switching to {model_chain[model_index]}..."
                    )

            elif any(k in err_lower for k in ['11001', 'getaddrinfo', 'timeout', 'connection', 'socket']):
                if network_retries <= 0:
                    print(f"  Max network retries reached for review {review_id}. Skipping.")
                    return None
                print(f"  Network error for review {review_id}. Retrying ({network_retries} left)...")
                time.sleep(5)
                network_retries -= 1

            else:
                print(f"  Unexpected error for review {review_id} on {model}: {e}")
                model_index += 1
                if model_index >= len(model_chain):
                    return None

    print(f"  Permanently failed to tag review {review_id}.")
    return None


def batch_tag_reviews(limit: int | None = None):
    config = load_config()
    db_path = get_db_path(config)
    model_chain = get_tagging_models(config)

    # Read run limit and delay from config (overridable via CLI limit arg)
    groq_cfg = config.get('groq', {})
    config_limit = groq_cfg.get('tagging_limit_per_run', 500)
    delay = float(groq_cfg.get('tagging_delay_seconds', 2.1))
    effective_limit = limit if limit is not None else config_limit

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
        SELECT id, review_text
        FROM reviews
        WHERE id NOT IN (SELECT review_id FROM tags)
        ORDER BY id
        LIMIT ?
    """
    cursor.execute(query, (effective_limit,))
    untagged = cursor.fetchall()

    if not untagged:
        print("No untagged reviews found.")
        conn.close()
        return

    print(f"Found {len(untagged)} untagged reviews to process this run (limit={effective_limit}).")
    print(f"Model chain: {' -> '.join(model_chain)}")
    print(f"Inter-call delay: {delay}s\n")

    client = setup_client()
    system_prompt = load_prompt()

    successful = 0
    failed = 0
    batch_size = 10
    total_batches = (len(untagged) - 1) // batch_size + 1

    for i in range(0, len(untagged), batch_size):
        batch = untagged[i:i + batch_size]
        batch_num = i // batch_size + 1
        print(f"Batch {batch_num}/{total_batches} — reviews {i+1}–{min(i+batch_size, len(untagged))}")

        for review_id, review_text in batch:
            tag_data = tag_single_review(client, review_id, review_text, system_prompt, model_chain)

            if tag_data is None:
                failed += 1
            else:
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
                successful += 1

            # Inter-call delay: prevents RPM exhaustion (30 RPM = 1 call/2s minimum)
            time.sleep(delay)

        # Commit after every batch — progress is saved even if run is interrupted
        conn.commit()
        print(f"  Saved. Running totals: {successful} tagged, {failed} failed.\n")

    conn.close()

    # Check how many remain untagged
    conn2 = sqlite3.connect(db_path)
    c2 = conn2.cursor()
    c2.execute("SELECT COUNT(*) FROM reviews WHERE id NOT IN (SELECT review_id FROM tags)")
    remaining = c2.fetchone()[0]
    conn2.close()

    print(f"Run complete. Tagged: {successful}, Failed: {failed}")
    if remaining > 0:
        print(f"{remaining} reviews still untagged. Re-run 'python auto_tag.py' to continue.")
    else:
        print("All reviews are now tagged.")


if __name__ == '__main__':
    batch_tag_reviews()
