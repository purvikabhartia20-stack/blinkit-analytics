import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0f111a; color: #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

def main():
    apply_custom_css()
    st.title("💬 Q&A Chat")
    st.markdown("Ask follow-up questions directly of the dataset.")
    
    st.info("Q&A module will be wired to Groq Llama 3.3 for data-backed chat functionality in Phase 6 completion.")
    
    query = st.chat_input("Ask a question (e.g. 'What are the main trust barriers for pharmacy?')")
    if query:
        with st.chat_message("user"):
            st.write(query)
        with st.chat_message("assistant"):
            st.write("This feature is currently under construction. It will process your query against the SQLite database.")

if __name__ == '__main__':
    main()
