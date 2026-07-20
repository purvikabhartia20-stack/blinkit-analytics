# Phase 3: Tagger: Category-Exploration Taxonomy

**Goal:** Design a Groq Llama 3.3 tagging schema specific to category-exploration behavior, and tag every cleaned review with structured, validated output. This is the core intellectual work of the whole project — the schema determines whether the eventual insights are actually useful.

**What I'll see when it's done:** Every review has a linked tag record; example outputs shown for sanity-check before the full run; documented schema definition; and a calculated spot-check agreement rate.

**Files:**
- `docs/phase3_tagger.md` (This file)
- `prompts/tagging_prompt.md` (the system instruction given to Groq Llama 3.3)
- `auto_tag.py` (the execution script using Pydantic)
- `tests/test_validation.py` (script to measure human vs AI agreement rate)

**Proposed schema fields (Finalized):**
- `theme` (string): Which of the 8 questions this relates to. One of: `q1_repeat_buying`, `q2_exploration_barriers`, `q3_discovery`, `q4_habits`, `q5_info_needed`, `q6_frustrations`, `q7_segments`, `q8_unmet_needs`, or `none`.
- `sentiment` (string): positive, negative, or neutral.
- `category_mentioned` (string): grocery, pharmacy, electronics, beauty, pet, baby, other, or none-unclear.
- `behavior_signal` (string): repeat-only, attempted-new-category, abandoned-attempt, or unclear.
- `pain_point` (string): Short text.
- `unmet_need` (string): Short text.
- `trust_barrier_mentioned` (boolean): true/false.
- `trust_barrier_text` (string): Short text.
- `severity` (string): low, medium, high.
- `key_quote` (string): verbatim substring, verified later.

**Step-by-step plan:**
1. **Schema Lockdown**: Defined strictly in `auto_tag.py` via Pydantic `ReviewTag`.
2. **API Connection**: Use `llama-3.3-70b-versatile` with a strict `response_schema` parameter.
3. **Batch Execution**: Read from `reviews` table, process individually but sleep between calls (`time.sleep(12)`) to respect the 5 RPM Free Tier quota limit.
4. **Resilience**: Commit to SQLite after every review to ensure partial progress is always saved if quota is hit.
5. **Validation**: Run `tests/test_validation.py` to compare a small human-annotated sample with the Groq Llama 3.3 output, calculating a formal "agreement rate" for the report.

**Edge cases Handled:**
- **Quota Limits**: Built-in 12s sleep respects the strict 5 RPM free tier limit.
- **Malformed JSON**: Prevented natively by using Groq's structured output API.
- **Hinglish**: `tagging_prompt.md` specifically instructs the model to handle "sabzi", "dawai", etc.

**Validation checklist:**
- [x] Pydantic schema strictly maps to the 8 research questions.
- [ ] Automated agreement rate calculated via script.

**Preconditions:**
- Phase 2 complete (Database has clean reviews).
