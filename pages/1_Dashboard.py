import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
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
    </style>
    """, unsafe_allow_html=True)

def load_tags_data():
    if not os.path.exists('blinkit_data.db'):
        return pd.DataFrame()
    conn = sqlite3.connect('blinkit_data.db')
    query = """
        SELECT t.id, t.review_id, r.source, t.theme, t.sentiment, t.category_mentioned, 
               t.behavior_signal, t.severity, r.review_text
        FROM tags t
        JOIN reviews r ON t.review_id = r.id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df['theme'] = df['theme'].str.replace(r'^q\d+_', '', regex=True).str.replace('_', ' ').str.title()
    return df

def main():
    apply_custom_css()
    st.title("📊 Live Data Dashboard")
    
    df = load_tags_data()
    
    if df.empty:
        st.warning("No tagging data found in the database. Run Phase 3 tagging first.")
        return
        
    st.markdown("### High-Level Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Reviews Tagged", len(df))
    
    relevant_df = df[df['theme'] != 'None']
    col2.metric("Relevant Signal (Q1-Q8)", len(relevant_df))
    col3.metric("Noise (None)", len(df[df['theme'] == 'None']))
    
    # Theme Distribution
    st.markdown("### Theme Distribution (Excluding 'none')")
    if not relevant_df.empty:
        theme_counts = relevant_df['theme'].value_counts().reset_index()
        theme_counts.columns = ['Theme', 'Count']
        theme_counts['Theme'] = theme_counts['Theme'].str.replace(r'^q\d+_', '', regex=True).str.replace('_', ' ').str.title()
        fig = px.bar(theme_counts, x='Theme', y='Count', color='Theme', title="Themes Identified")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No relevant themes found yet.")

    colA, colB = st.columns(2)
    with colA:
        st.markdown("### Sentiment Breakdown")
        sent_counts = df['sentiment'].value_counts().reset_index()
        sent_counts.columns = ['Sentiment', 'Count']
        fig2 = px.pie(sent_counts, names='Sentiment', values='Count', hole=0.4,
                      color_discrete_sequence=['#94a3b8', '#f87171', '#4ade80'])
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0')
        st.plotly_chart(fig2, use_container_width=True)
        
    with colB:
        st.markdown("### Top Categories Mentioned")
        cat_counts = df[df['category_mentioned'] != 'none-unclear']['category_mentioned'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Count']
        fig3 = px.bar(cat_counts, x='Category', y='Count', title="Categories Explored", color_discrete_sequence=['#f6d365'])
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0')
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### Raw Tagged Data")
    
    # Filter controls
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        sources = ['All'] + sorted(df['source'].unique().tolist())
        sel_source = st.selectbox("Filter by Source", sources)
    
    with f_col2:
        themes = ['All'] + sorted(df['theme'].unique().tolist())
        sel_theme = st.selectbox("Filter by Theme", themes)
        
    with f_col3:
        sentiments = ['All'] + sorted(df['sentiment'].unique().tolist())
        sel_sentiment = st.selectbox("Filter by Sentiment", sentiments)
        
    # Apply filters
    filtered_df = df.copy()
    if sel_source != 'All':
        filtered_df = filtered_df[filtered_df['source'] == sel_source]
    if sel_theme != 'All':
        filtered_df = filtered_df[filtered_df['theme'] == sel_theme]
    if sel_sentiment != 'All':
        filtered_df = filtered_df[filtered_df['sentiment'] == sel_sentiment]
        
    st.dataframe(filtered_df[['review_id', 'source', 'theme', 'sentiment', 'category_mentioned', 'review_text']])

if __name__ == '__main__':
    main()
