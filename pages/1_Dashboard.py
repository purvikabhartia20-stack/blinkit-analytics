import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import json
import os

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
            margin-bottom: 20px;
        }
        .metric-note { font-size: 12px; color: #94a3b8; margin-top: -10px; margin-bottom: 16px; }
    </style>
    """, unsafe_allow_html=True)


def load_data():
    """
    Load tagged data. Tries live SQLite DB first (local),
    falls back to dashboard_data.json (Streamlit Cloud).
    Returns (df, stats_dict, source_label).
    """
    # ── Live DB ────────────────────────────────────────────────────────────
    if os.path.exists('blinkit_data.db'):
        try:
            conn = sqlite3.connect('blinkit_data.db')
            query = """
                SELECT t.review_id, r.source, t.theme, t.sentiment,
                       t.category_mentioned, t.behavior_signal, t.severity, r.review_text
                FROM tags t
                JOIN reviews r ON t.review_id = r.id
            """
            df = pd.read_sql_query(query, conn)

            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM reviews")
            total = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM reviews WHERE id NOT IN (SELECT review_id FROM tags)")
            untagged = c.fetchone()[0]
            conn.close()

            if not df.empty:
                stats = {"total_reviews": total, "total_tagged": len(df), "total_untagged": untagged}
                return df, stats, "live"
        except Exception:
            pass

    # ── JSON snapshot (cloud) ──────────────────────────────────────────────
    if os.path.exists('dashboard_data.json'):
        try:
            with open('dashboard_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data.get('tags', []))
            stats = data.get('stats', {})
            return df, stats, "snapshot"
        except Exception:
            pass

    return pd.DataFrame(), {}, "none"


def main():
    apply_custom_css()
    st.title("📊 Live Data Dashboard")

    df, stats, source = load_data()

    if source == "snapshot":
        st.info(
            "📦 Showing a pre-built data snapshot (`dashboard_data.json`). "
            "The live database is not available in this environment — "
            "this is normal on Streamlit Cloud."
        )
    elif source == "none":
        st.warning("No data found. Run `python auto_tag.py` locally first.")
        return

    # Clean theme labels
    df['theme'] = df['theme'].str.replace(r'^q\d+_', '', regex=True).str.replace('_', ' ').str.title()

    # ── Metrics ────────────────────────────────────────────────────────────
    st.markdown("### High-Level Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews Tagged", stats.get("total_tagged", len(df)))
    col2.metric("Total Reviews in DB", stats.get("total_reviews", "—"))

    untagged = stats.get("total_untagged", 0)
    col3.metric(
        "Untagged (pending)",
        untagged,
        delta=f"-{untagged}" if untagged > 0 else "✓ All tagged",
        delta_color="inverse"
    )

    if untagged > 0:
        st.markdown(
            f'<p class="metric-note">⚙️ {untagged} reviews still untagged. '
            f'Run <code>python run_full_pipeline.py</code> locally to tag more '
            f'(500/day on free Groq tier).</p>',
            unsafe_allow_html=True
        )

    # ── Theme Distribution ─────────────────────────────────────────────────
    st.markdown("### Theme Distribution")
    relevant_df = df[df['theme'].str.lower() != 'none']
    if not relevant_df.empty:
        theme_counts = relevant_df['theme'].value_counts().reset_index()
        theme_counts.columns = ['Theme', 'Count']
        fig = px.bar(
            theme_counts, x='Theme', y='Count', color='Theme',
            title=f"Themes Identified across {len(df)} tagged reviews",
            color_discrete_sequence=px.colors.sequential.Plasma_r
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0', showlegend=False,
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No theme data yet.")

    # ── Source breakdown ───────────────────────────────────────────────────
    st.markdown("### Reviews by Source")
    source_counts = df['source'].value_counts().reset_index()
    source_counts.columns = ['Source Platform', 'Reviews Tagged']
    fig_src = px.pie(
        source_counts, names='Source Platform', values='Reviews Tagged',
        hole=0.45, color_discrete_sequence=px.colors.sequential.Plasma_r
    )
    fig_src.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0'
    )
    st.plotly_chart(fig_src, use_container_width=True)

    # ── Sentiment + Categories ─────────────────────────────────────────────
    colA, colB = st.columns(2)
    with colA:
        st.markdown("### Sentiment Breakdown")
        sent_counts = df['sentiment'].value_counts().reset_index()
        sent_counts.columns = ['Sentiment', 'Count']
        color_map = {'positive': '#4ade80', 'negative': '#f87171', 'neutral': '#94a3b8'}
        fig2 = px.pie(
            sent_counts, names='Sentiment', values='Count', hole=0.4,
            color='Sentiment', color_discrete_map=color_map
        )
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0')
        st.plotly_chart(fig2, use_container_width=True)

    with colB:
        st.markdown("### Top Categories Mentioned")
        cat_df = df[~df['category_mentioned'].isin(['none-unclear', 'none', ''])]
        if not cat_df.empty:
            cat_counts = cat_df['category_mentioned'].value_counts().reset_index()
            cat_counts.columns = ['Category', 'Count']
            fig3 = px.bar(
                cat_counts, x='Category', y='Count',
                color_discrete_sequence=['#f6d365']
            )
            fig3.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e2e8f0', xaxis_tickangle=-30
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No category data yet.")

    # ── Filterable raw data ────────────────────────────────────────────────
    st.markdown("### Explore Raw Tagged Data")
    f1, f2, f3 = st.columns(3)
    with f1:
        sel_source = st.selectbox("Source", ['All'] + sorted(df['source'].unique().tolist()))
    with f2:
        sel_theme = st.selectbox("Theme", ['All'] + sorted(df['theme'].unique().tolist()))
    with f3:
        sel_sent = st.selectbox("Sentiment", ['All'] + sorted(df['sentiment'].unique().tolist()))

    filtered = df.copy()
    if sel_source != 'All':
        filtered = filtered[filtered['source'] == sel_source]
    if sel_theme != 'All':
        filtered = filtered[filtered['theme'] == sel_theme]
    if sel_sent != 'All':
        filtered = filtered[filtered['sentiment'] == sel_sent]

    st.caption(f"Showing {len(filtered)} of {len(df)} tagged reviews")
    st.dataframe(
        filtered[['review_id', 'source', 'theme', 'sentiment', 'category_mentioned', 'review_text']],
        use_container_width=True,
        hide_index=True
    )


if __name__ == '__main__':
    main()
