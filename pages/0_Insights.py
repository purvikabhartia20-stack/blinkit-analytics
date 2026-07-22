import streamlit as st
import sqlite3
import json
import os
import glob
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.pdf_gen import generate_pdf_from_md

def apply_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #0f111a;
            color: #e2e8f0;
        }
        h1 {
            background: linear-gradient(90deg, #f6d365 0%, #fda085 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            letter-spacing: -1px;
            margin-bottom: 0.5rem;
        }
        .glass-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .fallback-flag {
            background: rgba(234, 179, 8, 0.2);
            border-left: 4px solid #eab308;
            color: #fde047;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    apply_custom_css()
    
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/2/25/Blinkit_logo.png", width=150)
    st.sidebar.title("Category Exploration")
    st.sidebar.markdown("Navigate using the menu above.")
    
    st.title("⚡ Insights Report")
    
    # Check if we are using fallback data
    is_fallback = False
    if os.path.exists('blinkit_data.db'):
        conn = sqlite3.connect('blinkit_data.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='fallback_cache'")
        if c.fetchone()[0] > 0:
            c.execute("SELECT COUNT(*) FROM fallback_cache WHERE is_fallback=1")
            fallback_count = c.fetchone()[0]
            if fallback_count > 0:
                is_fallback = True
        conn.close()
        
    if is_fallback:
        st.markdown('<div class="fallback-flag">⚠️ FALLBACK DATA ACTIVE. These insights are generated from a cached sample, not live scraped data.</div>', unsafe_allow_html=True)
    
    # Get available reports
    historical_reports = sorted(glob.glob('reports/insight_report_*.md'), reverse=True)
    report_options = ['Live Database (Latest)'] + historical_reports
    
    colA, colB = st.columns([3, 1])
    with colA:
        selected_report = st.selectbox("Select Report Version:", report_options)
        
    report_markdown = ""
    display_rows = []
    
    if selected_report == 'Live Database (Latest)':
        conn = sqlite3.connect('blinkit_data.db')
        c = conn.cursor()
        c.execute("SELECT theme, summary_markdown FROM insights")
        rows = c.fetchall()
        conn.close()
        
        if not rows:
            st.info("The Synthesizer (Phase 4) has not been run yet on the final data. \\n\\n**Please navigate to the Dashboard (Page 1) to view the live, real-time tags and charts!**")
            return
            
        for theme, summary in rows:
            clean_theme = theme.replace('_', ' ').title()
            report_markdown += f"#### {clean_theme}\\n\\n{summary}\\n\\n---\\n"
            display_rows.append((clean_theme, summary))
    else:
        with open(selected_report, 'r', encoding='utf-8') as f:
            report_markdown = f.read()
        
        # Simple splitting for historical markdown to mimic cards
        parts = report_markdown.split('---')
        for part in parts:
            if part.strip():
                display_rows.append(("Historical Entry", part.strip()))
                
    with colB:
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_bytes = generate_pdf_from_md(report_markdown)
        st.download_button(
            label="📥 Download PDF", 
            data=pdf_bytes, 
            file_name="Blinkit_Insights_Report.pdf", 
            mime="application/pdf",
            use_container_width=True
        )

    for title, content in display_rows:
        if title != "Historical Entry":
            st.markdown(f"#### {title}")
        
        # Detect and style error/insufficient-data states
        if content.startswith("*Error generating insight:") or "rate_limit_exceeded" in content or "Rate limit" in content:
            st.warning(
                "⚠️ This insight could not be generated due to API rate limits. "
                "Re-run **Phase 4** after the rate limit resets (usually within 24 hours). "
                "The system will automatically try smaller, faster models first."
            )
        elif content.strip() == "*Insufficient data for this theme in the current sample.*":
            st.info("📊 Not enough tagged reviews for this theme yet. Run Phase 3 (tagging) to add more data.")
        else:
            st.markdown(f'<div class="glass-card">{content}</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
