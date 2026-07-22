import sqlite3
import pandas as pd
import json
import os
import yaml
import time
import re
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv


def load_config() -> dict:
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)


def get_insight_models(config: dict) -> list[str]:
    """Build insight model chain: primary + fallbacks from config."""
    groq_cfg = config.get('groq', {})
    primary = groq_cfg.get('insights_model', 'llama-3.3-70b-versatile')
    fallbacks = groq_cfg.get('insights_fallback_models', [
        'openai/gpt-oss-20b',
        'llama-3.1-8b-instant',
    ])
    seen = set()
    chain = []
    for m in [primary] + fallbacks:
        if m not in seen:
            seen.add(m)
            chain.append(m)
    return chain

RESEARCH_QUESTIONS = {
    "q1_repeat_buying": "Why do users repeatedly buy from the same categories?",
    "q2_exploration_barriers": "What prevents users from exploring new categories?",
    "q3_discovery": "How do users discover products today?",
    "q4_habits": "What role do habits play in shopping behavior?",
    "q5_info_needed": "What information do users need before trying a new category?",
    "q6_frustrations": "What frustrations emerge repeatedly?",
    "q7_segments": "Which user segments are more likely to experiment?",
    "q8_unmet_needs": "What unmet needs emerge consistently across discussions?"
}

def setup_client():
    # Try Streamlit secrets first (cloud deployment), then fall back to .env (local)
    try:
        import streamlit as st
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        api_key = None
    if not api_key:
        load_dotenv()
        api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in Streamlit secrets or .env")
    return Groq(api_key=api_key)

def _parse_wait_seconds(error_message: str) -> int:
    """Extract the suggested wait time from a Groq rate-limit error message."""
    minutes = re.search(r'(\d+)m', error_message)
    seconds = re.search(r'(\d+(?:\.\d+))s', error_message)
    wait = 0
    if minutes:
        wait += int(minutes.group(1)) * 60
    if seconds:
        wait += int(float(seconds.group(1)))
    return wait if wait > 0 else 60


def call_groq_with_fallback(client, prompt, model_chain: list[str], max_tokens=800):
    """Try each model in model_chain in order, falling back on rate limits."""
    for model in model_chain:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content, model
        except Exception as e:
            err_str = str(e)
            if '429' in err_str or 'rate_limit' in err_str.lower():
                wait = _parse_wait_seconds(err_str)
                print(f"  Rate limit on {model}. Trying next model in chain...")
                continue  # try next model
            else:
                raise  # unexpected — re-raise
    raise RuntimeError("All Groq models are currently rate-limited for insight synthesis.")


def generate_insights():
    print("Starting Phase 4: Insight Generation")
    config = load_config()
    db_path = config.get('database', {}).get('db_path', 'blinkit_data.db')
    model_chain = get_insight_models(config)
    print(f"Insight model chain: {' -> '.join(model_chain)}")
    conn = sqlite3.connect(db_path)
    
    query = """
        SELECT r.source, r.date, r.review_text, t.theme, t.sentiment, t.category_mentioned, 
               t.behavior_signal, t.pain_point, t.unmet_need, t.trust_barrier_mentioned, 
               t.severity, t.key_quote
        FROM tags t
        JOIN reviews r ON t.review_id = r.id
    """
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No tagged data found. Run Phase 3 first.")
        conn.close()
        return

    client = setup_client()
    insights_list = []
    
    cursor = conn.cursor()
    cursor.execute("DELETE FROM insights")
    
    # Ensure reports dir exists
    os.makedirs('reports', exist_ok=True)
    report_lines = ["# Blinkit Category Exploration - Insights Report\n"]
    
    for theme, question in RESEARCH_QUESTIONS.items():
        print(f"Synthesizing theme: {theme}...")
        theme_df = df[df['theme'] == theme]
        
        report_lines.append(f"## Question: {question}\n")
        
        if theme_df.empty:
            summary = "*Insufficient data for this theme in the current sample.*"
            backing_data = {"count": 0}
            print(f"  - No data for {theme}. Skipping API call.")
        else:
            count = len(theme_df)
            sentiment_dist = theme_df['sentiment'].value_counts().to_dict()
            top_categories = theme_df['category_mentioned'].value_counts().head(3).to_dict()
            top_pain_points = theme_df[theme_df['pain_point'] != '']['pain_point'].value_counts().head(3).to_dict()
            
            high_sev = theme_df[theme_df['severity'] == 'high']
            others = theme_df[theme_df['severity'] != 'high']
            sampled_df = pd.concat([high_sev, others]).head(50)
            quotes = sampled_df['key_quote'].dropna().tolist()
            
            backing_data = {
                "count": count,
                "sentiment_distribution": sentiment_dist,
                "top_categories": top_categories,
                "top_pain_points": top_pain_points
            }
            
            prompt = f"""
You are an expert consumer behavior analyst.
Research Question: {question}

Here is the aggregated data for this theme from Blinkit user reviews:
- Total Mentions: {count}
- Sentiment Distribution: {sentiment_dist}
- Top Categories Discussed: {top_categories}
- Top Pain Points: {top_pain_points}

Key Quotes from Users:
{chr(10).join(f"- \\\"{q}\\\"" for q in quotes if q)}

Based ONLY on this data, write a concise, executive-level summary answering the research question. 
Use Markdown formatting. Use bullet points for key takeaways. Do not hallucinate external facts.
"""
            try:
                # Use model fallback chain for resilience against rate limits
                summary, used_model = call_groq_with_fallback(client, prompt, model_chain, max_tokens=800)
                print(f"  - Successfully generated insight for {theme} (model: {used_model})")
            except Exception as e:
                print(f"  - API Error for {theme}: {e}")
                summary = f"*Error generating insight: {e}*"
            
            time.sleep(3)  # Respect RPM limits between synthesis calls
            
        cursor.execute("""
            INSERT INTO insights (theme, summary_markdown, backing_data_json)
            VALUES (?, ?, ?)
        """, (theme, summary, json.dumps(backing_data)))
        
        report_lines.append(f"{summary}\n\n---\n")
        
        insights_list.append({
            "theme": theme,
            "question": question,
            "summary_markdown": summary,
            "backing_data": backing_data
        })
        
    conn.commit()
    
    # Validation Summary extraction
    cursor.execute("SELECT spot_check_date, sample_size, agreement_rate FROM validation_log ORDER BY id DESC LIMIT 1")
    val = cursor.fetchone()
    conn.close()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"insight_report_{timestamp}.md"
    
    with open('reports/insight_report.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        
    with open(f'reports/{report_filename}', 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        
    with open('reports/validation_summary.md', 'w', encoding='utf-8') as f:
        f.write("# Validation Summary\n\n")
        f.write("This document fulfills Requirement #12, detailing the validation of the AI tagging accuracy.\n\n")
        if val:
            f.write(f"- **Last Spot Check Date**: {val[0]}\n")
            f.write(f"- **Sample Size Checked**: {val[1]}\n")
            f.write(f"- **Human-AI Agreement Rate**: {val[2]}%\n")
        else:
            f.write("*No validation runs have been executed yet.*")
    
    with open('insights.json', 'w', encoding='utf-8') as f:
        json.dump(insights_list, f, indent=2)
        
    print(f"Phase 4 Complete! Generated reports in /reports and saved to insights.json")

if __name__ == '__main__':
    generate_insights()
