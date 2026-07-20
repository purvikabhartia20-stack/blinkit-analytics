# Phase 5: Interactive Dashboard (Streamlit)

**Goal:** Build a beautiful, responsive, and premium UI to present the Phase 4 insights. Allow users to drill down into specific themes, view quantitative charts, and read the raw supporting quotes.

**What I'll see when it's done:**
- A running `app.py` script.
- A local web interface (default `localhost:8501`).
- A highly aesthetic presentation layer with custom injected CSS for a premium look and feel.

**Files:**
- `docs/phase5_dashboard.md` (This file)
- `app.py`
- `run_dashboard.py` (Helper script if needed, or just standard `streamlit run app.py`)

**Step-by-step plan:**
1. **Initialize Streamlit**: Use a wide layout. Inject custom CSS for a premium dark-mode or glassmorphism aesthetic, adhering strictly to the "Rich Aesthetics" design mandate. This includes modern typography (e.g., Inter), smooth gradients, and subtle hover effects.
2. **Data Loading (with Fallback)**: 
   - Attempt to connect to `blinkit_data.db` and query the `insights` table.
   - If the database is locked or missing, automatically fall back to reading `insights.json`.
3. **Sidebar Navigation**: Allow the user to select one of the 8 research themes.
4. **Main Panel Content**:
   - **Executive Summary**: Render the Groq-generated Markdown prominently.
   - **Quantitative Metrics**: Use Plotly to render beautiful pie charts for Sentiment Distribution and bar charts for Top Categories/Pain Points.
   - **Raw Evidence**: Display a clean, styled table or expanding section showing the actual quotes used to generate the insight.
   - **Zero-Data State**: If a theme has no data (fallback string), display a styled empty-state message rather than broken charts.

**Edge cases Handled:**
- **Database Missing/Locked**: Handled gracefully via the `insights.json` fallback.
- **Port Conflict**: Streamlit handles this natively by incrementing the port.
- **Empty Themes**: Explicitly checking for the "Insufficient data" string and hiding the chart rendering logic to prevent errors.

**Validation checklist:**
- [ ] App launches without errors (`streamlit run app.py`).
- [ ] Custom CSS applies correctly and feels premium.
- [ ] Data loads from SQLite successfully.
- [ ] Plotly charts render interactive data.

**Preconditions:**
- Phase 4 complete (`insights.json` exists and/or DB is populated).
