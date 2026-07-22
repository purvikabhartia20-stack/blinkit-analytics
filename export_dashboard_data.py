"""
export_dashboard_data.py — Export tagged data snapshot for cloud deployment.
Run this locally after tagging, then commit dashboard_data.json to the repo.
Streamlit Cloud reads this file since it has no live SQLite DB.
"""
import sqlite3
import json
import yaml


def get_db_path():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config.get('database', {}).get('db_path', 'blinkit_data.db')


def export():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Tagged reviews with source info
    c.execute("""
        SELECT t.review_id, r.source, t.theme, t.sentiment,
               t.category_mentioned, t.behavior_signal, t.severity, r.review_text
        FROM tags t
        JOIN reviews r ON t.review_id = r.id
    """)
    cols = ['review_id', 'source', 'theme', 'sentiment',
            'category_mentioned', 'behavior_signal', 'severity', 'review_text']
    rows = [dict(zip(cols, row)) for row in c.fetchall()]

    # Summary stats
    c.execute("SELECT COUNT(*) FROM reviews")
    total_reviews = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tags")
    total_tagged = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM reviews WHERE id NOT IN (SELECT review_id FROM tags)")
    total_untagged = c.fetchone()[0]

    conn.close()

    data = {
        "stats": {
            "total_reviews": total_reviews,
            "total_tagged": total_tagged,
            "total_untagged": total_untagged,
        },
        "tags": rows
    }

    with open('dashboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(rows)} tagged rows → dashboard_data.json")
    print(f"Stats: {total_tagged}/{total_reviews} tagged, {total_untagged} pending")


if __name__ == '__main__':
    export()
