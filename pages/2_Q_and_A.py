import streamlit as st
import json
import os

def apply_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0f111a; color: #e2e8f0; }
        .stChatMessage { background: rgba(30, 41, 59, 0.7) !important; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)


def get_groq_client():
    """Get Groq client — tries Streamlit secrets first, then .env."""
    api_key = None
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        pass
    if not api_key:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    from groq import Groq
    return Groq(api_key=api_key)


def load_context() -> str:
    """Build a compact context string from insights.json for the system prompt."""
    if not os.path.exists('insights.json'):
        return "No insight data available."
    try:
        with open('insights.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        lines = ["You are an expert analyst for Blinkit (quick-commerce app in India)."]
        lines.append("Answer questions based ONLY on the following research insights derived from 830+ user reviews.\n")
        for item in data:
            theme = item.get('theme', '').replace('_', ' ').title()
            question = item.get('question', '')
            summary = item.get('summary_markdown', '')
            if summary and not summary.startswith('*Insufficient') and 'Error' not in summary[:30]:
                lines.append(f"### {theme} — {question}")
                # Truncate long summaries to keep context compact
                lines.append(summary[:800])
                lines.append("")
        lines.append("\nIf a question goes beyond this data, say so clearly. Do not hallucinate.")
        return "\n".join(lines)
    except Exception as e:
        return f"Could not load insight context: {e}"


def main():
    apply_custom_css()
    st.title("💬 Q&A Chat")
    st.markdown(
        "Ask questions about Blinkit user behaviour. "
        "Answers are grounded in the 830+ reviewed dataset."
    )

    client = get_groq_client()
    if client is None:
        st.error("GROQ_API_KEY not found. Add it to `.env` (local) or Streamlit secrets (cloud).")
        return

    context = load_context()

    # Initialise chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render existing messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Suggested questions
    if not st.session_state.messages:
        st.markdown("**Try asking:**")
        suggestions = [
            "What are the main reasons users don't explore new categories?",
            "What trust barriers exist for pharmacy purchases?",
            "What are the top frustrations users mention?",
            "Which user segments are most likely to try new categories?",
            "What unmet needs come up most often?",
        ]
        cols = st.columns(2)
        for i, q in enumerate(suggestions):
            if cols[i % 2].button(q, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                st.rerun()

    # Chat input
    if prompt := st.chat_input("Ask anything about the Blinkit dataset..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": context},
                            *[{"role": m["role"], "content": m["content"]}
                              for m in st.session_state.messages]
                        ],
                        max_tokens=600
                    )
                    answer = response.choices[0].message.content
                except Exception as e:
                    answer = f"Sorry, I couldn't get a response right now: {e}"

            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear chat"):
            st.session_state.messages = []
            st.rerun()


if __name__ == '__main__':
    main()
