"""
fix_insights.py — Sync the insights table from SQLite → insights.json.

This replaces the old approach that wrote fake placeholder data.
The Insights page reads from SQLite (live), but insights.json is used
by external tooling and historical reports. This keeps them in sync.

Usage: python fix_insights.py
"""
import sqlite3
import json
import yaml

RESEARCH_QUESTIONS = {
    "q1_repeat_buying": "Why do users repeatedly buy from the same categories?",
    "q2_exploration_barriers": "What prevents users from exploring new categories?",
    "q3_discovery": "How do users discover products today?",
    "q4_habits": "What role do habits play in shopping behavior?",
    "q5_info_needed": "What information do users need before trying a new category?",
    "q6_frustrations": "What frustrations emerge repeatedly?",
    "q7_segments": "Which user segments are more likely to experiment?",
    "q8_unmet_needs": "What unmet needs emerge consistently across discussions?",
}


def get_db_path() -> str:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config.get('database', {}).get('db_path', 'blinkit_data.db')


def sync_insights_json():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT theme, summary_markdown, backing_data_json FROM insights")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No insights in database. Run generate_insights.py first.")
        return

    insights_list = []
    for theme, summary, backing_json in rows:
        try:
            backing = json.loads(backing_json) if backing_json else {}
        except json.JSONDecodeError:
            backing = {}

        insights_list.append({
            "theme": theme,
            "question": RESEARCH_QUESTIONS.get(theme, ""),
            "summary_markdown": summary,
            "backing_data": backing,
        })

    with open('insights.json', 'w', encoding='utf-8') as f:
        json.dump(insights_list, f, indent=2, ensure_ascii=False)

    print(f"Synced {len(insights_list)} insights from DB → insights.json")


if __name__ == '__main__':
    sync_insights_json()
