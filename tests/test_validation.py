import sqlite3
import yaml

def get_db_path():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        return config.get('database', {}).get('db_path', 'blinkit_data.db')

def calculate_agreement_rate():
    print("Running Human-AI Spot Check Validation...")
    
    # Mock ground-truth for exactly 5 reviews to demonstrate the requirement #12 process.
    # In a real environment, a PM would manually label these 5 reviews and paste them here.
    human_ground_truth = {
        # review_id: expected_theme
        1: "q4_habits",
        2: "none",
        3: "q6_frustrations",
        4: "q2_exploration_barriers",
        5: "q8_unmet_needs"
    }
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    matches = 0
    total_checked = 0
    
    print("\n--- Spot Check Results ---")
    for review_id, expected_theme in human_ground_truth.items():
        cursor.execute("SELECT theme FROM tags WHERE review_id = ?", (review_id,))
        result = cursor.fetchone()
        
        if result:
            ai_theme = result[0]
            total_checked += 1
            if ai_theme == expected_theme:
                matches += 1
                status = "MATCH"
            else:
                status = f"MISMATCH (AI: {ai_theme}, Human: {expected_theme})"
            
            print(f"Review {review_id}: {status}")
    
    if total_checked == 0:
        print("\nNo tags found in the database yet to validate. Please run Phase 3 tagging first.")
        conn.close()
        return
        
    agreement_rate = (matches / total_checked) * 100
    
    print(f"\nTotal Sample Size: {total_checked}")
    print(f"Agreement Rate: {agreement_rate}%")
    
    # Log to validation_log table per README specs
    from datetime import datetime
    cursor.execute("""
        INSERT INTO validation_log (spot_check_date, sample_size, agreement_rate, notes)
        VALUES (?, ?, ?, ?)
    """, (datetime.now().isoformat(), total_checked, agreement_rate, "Mock human spot check run."))
    
    conn.commit()
    conn.close()
    
    print("\nValidation logged to database.")

if __name__ == "__main__":
    calculate_agreement_rate()
