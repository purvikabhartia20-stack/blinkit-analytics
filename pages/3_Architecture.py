import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0f111a; color: #e2e8f0; }
        .glass-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .flow-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 40px 0;
            font-family: 'Inter', sans-serif;
        }
        .flow-step {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            padding: 15px 25px;
            width: 80%;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            position: relative;
        }
        .flow-step h4 {
            color: #f6d365;
            margin-top: 0;
            margin-bottom: 5px;
        }
        .flow-arrow {
            color: #94a3b8;
            font-size: 24px;
            margin: 10px 0;
        }
        .flow-row {
            display: flex;
            justify-content: center;
            gap: 20px;
            width: 80%;
        }
        .flow-box {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            padding: 15px;
            flex: 1;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    apply_custom_css()
    st.title("🏗️ Architecture & Pipeline")
    st.markdown("Below is the complete end-to-end data pipeline powering this dashboard.")
    
    # HTML/CSS Flowchart
    st.markdown("""<div class="flow-container">
<div class="flow-row">
<div class="flow-box"><b>🍏 Apple App Store</b><br><small>Reviews</small></div>
<div class="flow-box"><b>🤖 Google Play Store</b><br><small>Reviews</small></div>
<div class="flow-box"><b>🌐 Reddit API</b><br><small>Discussions</small></div>
<div class="flow-box"><b>▶️ YouTube API</b><br><small>Comments</small></div>
<div class="flow-box"><b>🗣️ MouthShut</b><br><small>Web Scraping</small></div>
<div class="flow-box"><b>⚖️ Consumer Complaints</b><br><small>Web Scraping</small></div>
</div>
<div class="flow-arrow">⬇</div>
<div class="flow-step">
<h4>Phase 1: Environment & Verification</h4>
<small>Validate connections, APIs, and ensure the SQLite database schema is perfectly initialized.</small>
</div>
<div class="flow-arrow">⬇</div>
<div class="flow-step">
<h4>Phase 2: Ingestion & Storage</h4>
<small>Data scraped, deduplicated, and stored securely in local <b>SQLite Database</b> (blinkit_data.db)</small>
</div>
<div class="flow-arrow">⬇</div>
<div class="flow-step">
<h4>Phase 3: AI Tagging (Groq API)</h4>
<small>Each review sent to <b>Llama 3.1 8B Instant</b> (primary) with automatic fallback to Llama 3.3 70B.<br>Evaluated against 8 Research Questions. Enforced output via JSON schema.</small>
</div>
<div class="flow-arrow">⬇</div>
<div class="flow-step">
<h4>Phase 4: Synthesis & Insights</h4>
<small>Tagged subsets pushed to <b>Llama 3.3 70B Versatile</b> (with 8B fallback) to generate Executive Summaries.<br>Historical reports saved natively to markdown files.</small>
</div>
<div class="flow-arrow">⬇</div>
<div class="flow-step">
<h4>Phase 5: Backend Orchestration</h4>
<small>Execute end-to-end runs handling errors, fallbacks, and rate limit backoffs gracefully.</small>
</div>
<div class="flow-arrow">⬇</div>
<div class="flow-step" style="border-color: #4ade80;">
<h4 style="color: #4ade80;">Phase 6: Live Dashboard</h4>
<small><b>Streamlit UI</b> visually renders live SQLite tables and markdown files.<br>Generates on-the-fly PDF exports using pure-Python fpdf2.</small>
</div>
<div class="flow-arrow">⬇</div>
<div class="flow-step">
<h4>Phase 7: Testing & Accuracy</h4>
<small>Human spot-checking AI tags to validate accuracy. Logs written to validation_summary.md</small>
</div>
<div class="flow-arrow">⬇</div>
<div class="flow-step">
<h4>Phase 8: Deploy & Polish</h4>
<small>Final presentation formatting, packaging the open-source repo, and preparing deliverables.</small>
</div>
</div>""", unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Tagging Schema")
    st.code("""
    class ReviewTag(BaseModel):
        theme: str (q1-q8, or none)
        sentiment: str
        category_mentioned: str
        behavior_signal: str
        pain_point: str
        unmet_need: str
        trust_barrier_mentioned: bool
        severity: str
    """)
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == '__main__':
    main()
