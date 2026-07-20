# Phase 4: Synthesis & Insight Generation

**Goal:** Roll up the tagged review data to definitively answer the 8 specific research questions using Pandas (for quantitative stats) and Groq Llama 3.3 (for qualitative summarization). Ensure validation artifacts and formal reports are generated.

**What I'll see when it's done:**
- A single `generate_insights.py` script that orchestrates the synthesis using `llama-3.3-70b-versatile`.
- The `insights` table in SQLite populated with up to 8 rows.
- `reports/insight_report.md` (and a manually generated `.pdf` equivalent) containing the final synthesized answers.
- `reports/validation_summary.md` detailing the human spot-check agreement rate.
- An automated quote verification step (`tests/verify_quotes.py`) that strictly blocks report generation if any quote was hallucinated.

**Files:**
- `docs/phase4_synthesis.md` (This file)
- `generate_insights.py`
- `tests/verify_quotes.py`
- `reports/insight_report.md`
- `reports/validation_summary.md`

**Step-by-step plan:**
1. **Quote Verification**: Run `tests/verify_quotes.py` to ensure all key quotes extracted in Phase 3 are exact substrings of their respective reviews. If any fail, stop execution.
2. **SQL Aggregation**: Read all tagged reviews from the database.
3. **Synthesis Prompting**: Group by the 8 themes. Feed the metrics and top 50 severity quotes to `llama-3.3-70b-versatile` to synthesize an answer to the specific research question.
4. **Report Generation**: Output the resulting markdown blocks into `reports/insight_report.md` and export validation metrics into `reports/validation_summary.md`.

**Edge cases Handled:**
- **Empty Themes**: If a theme has 0 tagged reviews, fallback instantly without API calls.
- **Hallucinated Quotes**: Hard-gated by the verification script.

**Validation checklist:**
- [x] Quotes are successfully verified.
- [x] Insights report is compiled in markdown.
- [x] Validation summary matches Phase 3 results.

**Preconditions:**
- Phase 3 complete and data validated.
