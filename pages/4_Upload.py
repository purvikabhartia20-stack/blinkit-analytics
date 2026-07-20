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
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    apply_custom_css()
    st.title("📤 Manual Data Upload")
    st.markdown("Upload a CSV of additional reviews for sources that cannot be automatically scraped.")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        st.success("File uploaded successfully! Parsing logic will be added in Phase 6.")
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == '__main__':
    main()
