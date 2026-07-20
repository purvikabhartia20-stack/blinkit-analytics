import os
import sys
import time
from run_phase2 import main as run_phase2_main
from auto_tag import main as auto_tag_main
from generate_insights import main as generate_insights_main

LOCK_FILE = ".pipeline_lock"

def check_lock():
    if os.path.exists(LOCK_FILE):
        print("Pipeline is already running! (Lock file found: .pipeline_lock)")
        print("If you are sure it is not running, manually delete the lock file and try again.")
        sys.exit(1)

def set_lock():
    with open(LOCK_FILE, 'w') as f:
        f.write(str(time.time()))

def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

def main():
    print("=" * 50)
    print("🚀 Starting End-to-End Insights Pipeline (Phase 5)")
    print("=" * 50)
    
    check_lock()
    set_lock()
    
    try:
        print("\n--- [1/3] Phase 2: Ingestion & Storage ---")
        run_phase2_main()
        
        print("\n--- [2/3] Phase 3: AI Tagging ---")
        auto_tag_main()
        
        print("\n--- [3/3] Phase 4: Synthesis & Insights ---")
        generate_insights_main()
        
        print("\n✅ Pipeline completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed due to an error: {e}")
        print("The lock file will be released safely so you can resume later.")
        
    finally:
        release_lock()
        print("=" * 50)

if __name__ == '__main__':
    main()
