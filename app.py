import streamlit as st

st.set_page_config(page_title="Blinkit Insights", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

pg1 = st.Page("pages/0_Insights.py", title="Insights Report", icon="⚡", default=True)
pg2 = st.Page("pages/1_Dashboard.py", title="Live Dashboard", icon="📊")
pg3 = st.Page("pages/2_Q_and_A.py", title="Q&A Chat", icon="💬")
pg4 = st.Page("pages/3_Architecture.py", title="Architecture", icon="🏗️")
pg5 = st.Page("pages/4_Upload.py", title="Manual Upload", icon="📤")

pg = st.navigation([pg1, pg2, pg3, pg4, pg5])

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/2/25/Blinkit_logo.png", width=150)
st.sidebar.title("Category Exploration")
st.sidebar.markdown("Navigate using the menu above.")

pg.run()
