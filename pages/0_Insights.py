import streamlit as st
import sqlite3
import json
import os
import glob
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.pdf_gen import generate_pdf_from_md

RESEARCH_QUESTIONS = {
    "q1_repeat_buying":        "Why do users repeatedly buy from the same categories?",
    "q2_exploration_barriers": "What prevents users from exploring new categories?",
    "q3_discovery":            "How do users discover products today?",
    "q4_habits":               "What role do habits play in shopping behavior?",
    "q5_info_needed":          "What information do users need before trying a new category?",
    "q6_frustrations":         "What frustrations emerge repeatedly?",
    "q7_segments":             "Which user segments are more likely to experiment?",
    "q8_unmet_needs":          "What unmet needs emerge consistently across discussions?",
}

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
        .source-badge {
            background: rgba(246, 211, 101, 0.15);
            border: 1px solid rgba(246, 211, 101, 0.4);
            color: #f6d365;
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 99px;
            margin-left: 8px;
            vertical-align: middle;
        }
    </style>
    """, unsafe_allow_html=True)


def load_insights_from_db():
    """Load from SQLite if DB exists and has data."""
    if not os.path.exists('blinkit_data.db'):
        return None
    try:
        conn = sqlite3.connect('blinkit_data.db')
        c = conn.cursor()
        c.execute("SELECT theme, summary_markdown FROM insights ORDER BY theme")
        rows = c.fetchall()
        conn.close()
        return rows if rows else None
    except Exception:
        return None


def load_insights_from_json():
    """Fall back to pre-built insights.json (works on Streamlit Cloud)."""
    json_path = 'insights.json'
    if not os.path.exists(json_path):
        return None
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [(item['theme'], item['summary_markdown']) for item in data]
    except Exception:
        return None


def main():
    apply_custom_css()

    st.sidebar.image(
        "https://upload.wikimedia.org/wikipedia/commons/2/25/Blinkit_logo.png",
        width=150
    )
    st.sidebar.title("Category Exploration")
    st.sidebar.markdown("Navigate using the menu above.")

    st.title("⚡ Insights Report")
    st.markdown(
        "AI-synthesised executive summaries answering 8 research questions "
        "about Blinkit user behaviour, drawn from 830+ tagged reviews."
    )

    # ── Data source selection ──────────────────────────────────────────────
    historical_reports = sorted(glob.glob('reports/insight_report_*.md'), reverse=True)
    report_options = ['Latest Insights'] + historical_reports

    colA, colB = st.columns([3, 1])
    with colA:
        selected_report = st.selectbox("Select Report Version:", report_options)

    report_markdown = ""
    display_rows = []
    data_source_label = ""

    if selected_report == 'Latest Insights':
        # Try live DB first, fall back to insights.json (Streamlit Cloud)
        rows = load_insights_from_db()
        if rows:
            data_source_label = "live database"
        else:
            rows = load_insights_from_json()
            data_source_label = "pre-built snapshot (insights.json)"
            if rows:
                st.info(
                    "📦 Showing insights from the pre-built snapshot "
                    "(`insights.json`). The live database is not available "
                    "in this environment — this is normal on Streamlit Cloud."
                )

        if not rows:
            st.info(
                "No insights found. Run `python generate_insights.py` locally "
                "to generate them, then redeploy."
            )
            return

        for theme, summary in rows:
            question = RESEARCH_QUESTIONS.get(theme, "")
            clean_theme = theme.replace('_', ' ').title()
            display_label = f"{clean_theme}" + (f" — _{question}_" if question else "")
            report_markdown += f"#### {clean_theme}\n\n{summary}\n\n---\n"
            display_rows.append((display_label, summary))

    else:
        # Historical markdown report
        try:
            with open(selected_report, 'r', encoding='utf-8') as f:
                report_markdown = f.read()
            parts = report_markdown.split('---')
            for part in parts:
                if part.strip():
                    display_rows.append(("Historical Entry", part.strip()))
        except Exception as e:
            st.error(f"Could not open report: {e}")
            return

    # ── PDF download ────────────────────────────────────────────────────────
    with colB:
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            pdf_bytes = generate_pdf_from_md(report_markdown)
            st.download_button(
                label="📥 Download PDF",
                data=pdf_bytes,
                file_name="Blinkit_Insights_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.caption(f"PDF unavailable: {e}")

    # ── Render cards ────────────────────────────────────────────────────────
    for title, content in display_rows:
        if title != "Historical Entry":
            st.markdown(f"#### {title}")

        if (content.startswith("*Error generating insight:")
                or "rate_limit_exceeded" in content
                or "Rate limit" in content):
            st.warning(
                "⚠️ This insight hit an API rate limit when it was generated. "
                "Re-run `python generate_insights.py` to refresh it."
            )
        elif content.strip() == "*Insufficient data for this theme in the current sample.*":
            st.info(
                "📊 Not enough tagged reviews for this theme yet. "
                "Run `python auto_tag.py` to tag more reviews."
            )
        else:
            st.markdown(
                f'<div class="glass-card">{content}</div>',
                unsafe_allow_html=True
            )


if __name__ == '__main__':
    main()
