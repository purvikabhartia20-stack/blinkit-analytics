"""
run_full_pipeline.py — One-command daily pipeline runner.

What it does:
  1. Tags up to 500 reviews (one day's free-tier budget on llama-3.1-8b-instant)
  2. Regenerates all insights from the newly tagged data
  3. Syncs insights DB → insights.json

Run this once per day until all reviews are tagged:
    python run_full_pipeline.py

Check progress in the Live Dashboard (page 1) of the Streamlit app.
"""
import sqlite3
import yaml
import sys


def get_db_path():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config.get('database', {}).get('db_path', 'blinkit_data.db')


def print_status(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM reviews')
    total = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM tags')
    tagged = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM reviews WHERE id NOT IN (SELECT review_id FROM tags)')
    untagged = c.fetchone()[0]
    conn.close()
    pct = (tagged / total * 100) if total else 0
    print(f"\n  Total reviews : {total}")
    print(f"  Tagged        : {tagged} ({pct:.1f}%)")
    print(f"  Untagged      : {untagged}")
    return untagged


def main():
    print("=" * 55)
    print("  Blinkit Insights — Daily Pipeline Runner")
    print("=" * 55)

    db_path = get_db_path()

    print("\n[Before]")
    untagged_before = print_status(db_path)

    if untagged_before == 0:
        print("\n✅ All reviews are already tagged!")
        print("   Regenerating insights from full dataset...\n")
    else:
        print(f"\n--- Step 1/3: Tagging (up to 500 reviews) ---")
        from auto_tag import batch_tag_reviews
        batch_tag_reviews()

    print(f"\n[After tagging]")
    untagged_after = print_status(db_path)

    print(f"\n--- Step 2/3: Regenerating Insights ---")
    from generate_insights import generate_insights
    generate_insights()

    print(f"\n--- Step 3/3: Syncing insights.json ---")
    from fix_insights import sync_insights_json
    sync_insights_json()

    print("\n" + "=" * 55)
    print(f"  Run complete.")
    if untagged_after > 0:
        print(f"  {untagged_after} reviews still untagged.")
        print(f"  Run this script again tomorrow to continue.")
    else:
        print(f"  All reviews tagged — full insights now available!")
    print("=" * 55)


if __name__ == '__main__':
    main()
