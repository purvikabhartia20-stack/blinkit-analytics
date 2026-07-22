# Blinkit Category-Discovery Engine — Master README

> **For the AI assistant reading this:** This is the complete project brief — everything is in this one file. Read it fully before doing anything.
>
> This file contains a detailed **Phase Plan** (Section 9). Read it carefully — **it is context, not the final phase documents.** The actual protocol for how we build is in Section 10, and it does not change: you do not create any phase-specific files or write any code until I type the exact phrase **"Implement Phase N."**
>
> If, while reading this or while working, you notice something important that isn't addressed here — a better library, a smarter data source, a gap in the plan — **say so and propose it, but do not implement it until I confirm.** I would rather hear "I think X would work better, here's why" than have you silently pick your own approach.

---

## 1. What we are building, in plain language

I am a Product Manager on the Growth team at Blinkit (a 10-minute grocery/quick-commerce delivery app in India). Blinkit's own strategic goal — the thing I've been asked to move — is stated exactly like this:

> **"Increase the percentage of Monthly Active Customers who purchase products from at least one new category every month."**

Right now, most users buy from the same 2–3 categories on repeat (groceries, snacks) and never try the others Blinkit actually sells (pharmacy, electronics, beauty, pet supplies, baby care, and more). I need to figure out **why** — and the first step, before I design any fix, is to read what real users are actually saying about this, at a scale no human can read manually.

So I'm building a small web app on my own laptop that does five things:

1. **Goes out to the internet** and pulls real Blinkit reviews and discussions from public sources (Play Store, App Store, and Reddit at minimum — see Section 5 for exactly what's confirmed vs. what needs live discovery).
2. **Reads every single review** using an AI (Groq/Llama 3.3) and tags each one — what topic it's about, sentiment, what kind of user wrote it, how serious the complaint is, and which *category-behavior* pattern it reflects.
3. **Lets me upload extra reviews** manually as a spreadsheet, for any source that can't be scraped automatically.
4. **Generates a report** that answers specific product questions (Section 3) using real quotes from real users as evidence — never invented or paraphrased-to-sound-like-a-quote.
5. **Shows everything in a dashboard** I can open on my laptop — charts, a refresh button, the report, and a chat box to ask follow-up questions of the data directly.

That's the whole product. The part that deserves the most care is **what the AI is looking for when it reads a review** — the tagging schema needs to be built specifically around category-exploration behavior: why don't people try new categories, what stops them, what would make them trust a new category. This has to reflect the actual behavior under study, not a generic sentiment/topic schema — a schema built for a different kind of product wouldn't capture the right signals here.

---

## 2. Who I am and what I know

- **I am NOT a coder.** I cannot write code, debug code, or read code in detail. I can read plain English explanations of what code does.
- I am a Product Manager. I understand product thinking, user segments, feature prioritization, and I've already done the industry/business-case research for this project separately — you don't need to justify *why* this matters, just build the tool that investigates *how*.
- I will be running an AI coding partner (Antigravity or similar) to write, run, and fix code, and explain in plain English what it did.
- **Explain things like I'm intelligent but technical jargon doesn't help me.** Use analogies. Avoid words like "ORM," "async," "middleware" unless you also define them in brackets the first time.
- If something goes wrong, **explain WHY it went wrong before fixing it.** I'm trying to understand the system, not just get an output.

---

## 3. The questions this project must answer

There are **8 research questions** and **4 separate "show your work" process requirements**. Treat all 12 as individually gradable, not as one blended goal.

**The 8 research questions:**
1. Why do users repeatedly buy from the same categories?
2. What prevents users from exploring new categories?
3. How do users discover products today?
4. What role do habits play in shopping behavior?
5. What information do users need before trying a new category?
6. What frustrations emerge repeatedly?
7. Which user segments are more likely to experiment?
8. What unmet needs emerge consistently across discussions?

**The 4 process-transparency requirements — these are separate from the findings themselves:**
9. Demonstrate **how** the workflow gathers and analyzes data.
10. Demonstrate **how** themes are identified.
11. Demonstrate **how** insights are generated.
12. Demonstrate **how** the quality of those insights was validated.

Item 12 needs a real, named answer to "how do we know the AI's tagging is actually correct" — such as a human spot-check sample with a measured agreement rate, cross-source triangulation, or a confidence/severity score attached to each theme. Propose a specific method; don't leave this implicit.

---

## 4. Hard constraints — these CANNOT be broken

### Money
- **Everything must be free.** Zero dollars spent on anything.
- I have use the free tier Groq API for fast LLM inference.
- I have Antigravity free-tier access.
- **We are staying on free tools only — no paid APIs, and no Claude/Anthropic or OpenAI models inside the pipeline itself,** even though I'm discussing and planning this project with Claude separately. The pipeline's own AI calls stay on free-tier Groq API. Do not suggest switching this unless you flag it as a proposal for me to approve first.

### Tools and AI engines allowed
- **Groq API** (free tier). Use Llama 3.3 70B Versatile for bulk tagging and synthesis — it's extremely fast and supports JSON schema enforcement — the stronger reasoning model is worth reserving for the harder job of generating insights across the whole dataset, where quality matters more than speed.
- **Free Python libraries only**: `google-play-scraper`, `app-store-scraper`, `requests`, `praw` or unauthenticated Reddit JSON endpoints, `streamlit`, `sqlite3` (built-in), `plotly`, `pandas`, `pyyaml`, `beautifulsoup4`, and any other free library if it genuinely helps — propose it, don't just add it silently.

### Tools NOT allowed
- No paid AI APIs (OpenAI, Anthropic, Grok) inside the pipeline.
- No paid scraping services.
- No paid databases or paid hosting.
- No API that costs money to access at any volume we'd realistically need (e.g. paid-tier Twitter/X API, Instagram Graph API beyond free limits).

### Tech stack, and why each piece is chosen
- **Language:** Python 3.11+
- **UI framework:** Streamlit — frontend and backend live in one file, which matters because I need to run and see results myself without deploying separate infrastructure.
- **Database:** SQLite — a single file, no server to set up or maintain, appropriate for a local, single-user tool.
- **Charts:** Plotly — works natively inside Streamlit.
- **AI:** Groq API (Llama 3.3 70B Versatile for tagging and synthesis).
- **Deployment:** Streamlit Community Cloud free tier, or local laptop.

If you think a different choice would genuinely serve this project better — say so, with a reason, and wait for my confirmation before changing anything.

---

## 5. Data sources — confirmed identifiers, and what still needs live discovery

**We need all real reviews. No mock, synthetic, or injected data in anything that produces the final numbers — ever, at any stage that could end up in a report.** More on this in Section 7.

### Source 1: Google Play Store — confirmed
- **Library:** `google-play-scraper` (free, no key needed)
- **Target:** Blinkit app, package name `com.grofers.customerapp` *(verified directly against the live Play Store listing)*
- **Volume:** propose a number based on what's realistically gettable without hitting rate limits — 2,000 most recent as a starting point, adjustable
- **Country:** IN (India) — this is an India-specific product
- **Sort:** Newest first
- **Fields needed:** date, rating (1–5 stars), review text, username (anonymize), country code

### Source 2: Apple App Store — confirmed
- **Library:** `app-store-scraper` (free, no key needed)
- **Target:** Blinkit app, App ID `960335206` *(verified directly against the live App Store listing)*
- **Volume:** propose based on realistic availability — Apple reviews tend to be far sparser than Play Store for Indian apps; don't force a large number if the real volume is thin
- **Country:** IN
- **Fields needed:** date, rating, title, review text, country code

### Source 3: Reddit — method confirmed, scope needs live discovery

Reddit data is gettable via **unauthenticated Reddit JSON search endpoints** (e.g. `reddit.com/search.json?q=...`, no key, no login required), which work by *search query* across any subreddit or across all of Reddit — this fits the free-tools constraint and doesn't depend on a dedicated community existing.

There is no single, dedicated, high-volume Blinkit subreddit the way some other products have an obvious home community. So instead of hard-coding a subreddit list from assumption, do this:
1. Use the search-endpoint method, but query broadly — search `q=blinkit` (and variants: "blinkit delivery," "blinkit app," "blinkit refund," etc.) both across general India-focused subs (r/india, r/bangalore, r/mumbai, r/delhi) **and** unrestricted Reddit-wide search (no subreddit filter) — this captures Blinkit mentions wherever they actually occur, which may be broader and less predictable than one dedicated community would be.
2. Report back real volume and substance before committing to a final source list.
3. It's fine if this ends up being a thinner source than Play Store — **depth on fewer sources is explicitly fine per the brief; source breadth is not the grading criterion.**

### Sources not automatically included — propose, don't assume
YouTube comments, Instagram, and Twitter are not part of the default source list. For a grocery-delivery app, meaningful discussion volume on these platforms is uncertain. **Assess this rather than including it by default:** if you find real, substantive Blinkit discussion on any of these, propose adding it with an estimate of volume and effort; if not, propose leaving it out and explain why. Either answer is fine — just make it a reasoned decision.

---

## 6. Parameters to prevent constant API failures — be explicit, don't leave this implicit

A pipeline that scrapes multiple external sources is inherently fragile — without proactive handling, a single failure partway through a long multi-source pull can waste significant time redoing completed work. Set concrete numeric parameters up front:

- **Rate limiting:** define a max-requests-per-minute ceiling per source, below the platform's documented or observed limit, and throttle to it proactively rather than waiting to get rate-limited first.
- **Retry policy:** every external call retries up to 3 times with exponential backoff (1s → 2s → 4s), and logs clearly on final failure rather than crashing the whole run.
- **Checkpointing / resumability:** the pipeline must save progress incrementally (e.g. after every N records, or after each source completes) so a failure partway through does not require starting over from zero. This matters especially for Reddit (Section 5), where the discovery process may involve more trial-and-error than a known, fixed source list.
- **Quota tracking:** for the Groq API free tier specifically, track calls made against the known 30 Requests Per Minute (RPM) limit and pause/warn before hitting it, rather than failing mid-run with no explanation.
- **Timeout handling:** every network call has an explicit timeout; a hung request should never freeze the whole pipeline silently.
- **Cool-down on repeated failures:** if a single source fails 3 times in a row, stop hammering it, log it clearly, and continue with the other sources rather than blocking the whole run on one bad connection.

Propose the exact numeric values for these (requests/minute, checkpoint frequency, timeout duration) based on what's realistic for the specific libraries in use — I'd rather you set real, tested numbers than have me guess them.

---

## 7. Dashboard resilience — a fallback pattern, kept clearly separate from real data

A live session (testing, or a live demo) could hit an API failure at an inconvenient moment. Rather than the dashboard going blank or crashing, it should be able to fall back to a cached/sample state — but this needs a hard, structural separation from real analysis data, enforced so it can't be violated by accident:

- A clearly-named fallback/cache dataset, stored in an obviously separate table (e.g. `fallback_cache`, never mixed into the same rows as real scraped/tagged data).
- A visible flag or label in the UI whenever fallback data is being shown, so it's never mistaken for real results — including during a live demo, where this matters most.
- An explicit reset step that runs before any pull whose output is meant to produce real, submittable numbers, so fallback-state data can never leak into what actually gets reported.

Propose the specific implementation (table structure, flag mechanism, reset trigger) — the goal is dashboard resilience that never, under any circumstance, contaminates the real findings.

---

## 8. Universal edge cases — bake these into every phase

1. **Network failures** — retry 3× with exponential backoff (see Section 6).
2. **Rate limits** — proactive throttling, not just reactive handling (see Section 6).
3. **Empty results** — if a source returns zero new records, log clearly and continue; never crash.
4. **Encoding issues** — reviews may contain emojis, Hindi/regional-language text mixed with English (Hinglish is common in Indian app reviews), or special characters. UTF-8 everywhere, and don't assume English-only text.
5. **Duplicate reviews** — detect by source + date + text hash, skip.
6. **Long reviews** — truncate to a defined character limit before sending to Groq; state the limit explicitly.
7. **API key missing** — clear plain-English error, not a stack trace.
8. **Database locked** — wrap writes in try/except, retry once.
9. **AI returns invalid JSON** — parse defensively; retry once with a stricter prompt; skip and log after 2 failures, don't silently drop the review without a record.
10. **Slow runs** — live progress bar and step-by-step status so a long run doesn't look frozen.
11. **Reddit search scope isn't pre-fixed** — since Section 5's Reddit *scope* (not method) is determined live rather than hard-coded, the pipeline should handle "this particular query/sub produced very little" gracefully, as a normal outcome to report and move past, not an error state.

---

## 9. The Phase Plan — context for what gets built, phase by phase

**Read this whole section now and add any edge cases or corrections you'd make. This is context, not the final phase documents — see Section 10 for what you actually do with it.**

### Phase 1 — Environment & Connection Verification

**Goal:** Confirm every external connection actually works before any real data collection begins — Groq API, Play Store scraper, App Store scraper, Reddit search endpoint, local database, local dashboard shell.

**What I'll see when it's done:** A verification script that pings all four external connections and prints a clear pass/fail for each; an empty SQLite database file with the full schema already created; `streamlit run app.py` opens a blank dashboard shell without errors.

**Files:** `.env` / `config.yaml`, `init_db.py`, `verify_setup.py`

**Step-by-step plan:**
1. Create the config template with placeholders for the Groq API key.
2. Design and create the database schema: a `reviews` table (raw cleaned text + metadata), a `tags` table (Groq's structured output per review, linked by review ID), an `insights` table (synthesized answers per research question), a `validation_log` table (spot-check results, agreement rates), and a `fallback_cache` table with an explicit `is_fallback` boolean flag — never mixed into the main `reviews`/`tags` tables (see Section 7).
3. Write one test call per source: a trivial Groq prompt, a single Play Store review pull, a single App Store review pull, a single Reddit search query — each wrapped so a failure prints a plain-English cause, not a stack trace.
4. Confirm which Apple App Store storefront to use — **IN specifically**, not US/UK/CZ (some Apple listings redirect across storefronts; confirm the correct one returns India-relevant reviews before relying on it).

**Edge cases:**
- Missing or invalid Groq API key → clear message, not a stack trace.
- Play Store package name typo or app removed/renamed → validate by checking the returned app title matches "Blinkit" before proceeding.
- App Store ID resolves to the wrong storefront → explicitly print the returned app name/publisher for manual confirmation.
- **Reddit's JSON endpoints require a descriptive `User-Agent` header** — requests without one get throttled or blocked quickly; easy to miss and looks like a random intermittent failure if not handled from the start.
- SQLite file can't be created due to directory permissions → clear error naming the exact path.
- Local Streamlit port already in use → clear message with the conflicting port number.
- Groq free-tier quota already partially used from earlier testing → check remaining quota before assuming a fresh full allowance.

**Validation checklist:** All four connection checks green in `verify_setup.py`. Database file has all five tables with correct schemas (visually confirmed). Streamlit opens locally with no console errors.

**Preconditions:** Groq API key obtained. Confirmed IN storefront details for both stores.

**If something breaks:** Groq quota error on first test call → confirm RPM limits aren't exceeded. Play Store returns `None` → re-verify package name against the live listing. Reddit returns 429 → add the User-Agent header fix, retry with a short delay.

---

### Phase 2 — Scrapers & Database Population

**Goal:** Pull real reviews from Play Store, App Store, Reddit, and YouTube (search-based scope, per Section 5), clean and deduplicate, store in SQLite. Real data only — no mock/injected records enter this table under any circumstance.

**What I'll see when it's done:** The `reviews` table populated with real rows; exact count report per source; a dedupe report; a `reddit_discovery_log.md` documenting exactly which subreddits/search terms were tried and their real yield.

**Files:** `fetch_playstore.py`, `fetch_appstore.py`, `fetch_reddit.py`, `fetch_youtube.py`, `clean.py`, `reddit_discovery_log.md`

**Step-by-step plan:**
1. Play Store: pull recent reviews (start ~2,000, adjustable), IN storefront, newest-first.
2. App Store: pull whatever volume is genuinely available for IN — **do not force a target number.**
3. Reddit: run the search-endpoint queries from Section 5, log every query/sub combination and its actual yield in `reddit_discovery_log.md` — this log doubles as direct evidence for the brief's "demonstrate how the workflow gathers data" requirement.
3b. YouTube: Pull comments from top videos matching Blinkit ads/reviews using YouTube Data API v3.
4. Clean: strip HTML, normalize whitespace, preserve Hindi/Hinglish/regional-script text as-is — **do not auto-translate**, since translation risks distorting meaning and the LLM can handle multilingual input directly in Phase 3.
5. Deduplicate within each source by a hash of (source + date + text). No cross-source dedup — a Play Store review and a Reddit post are different artifacts even if from the same user.
6. Truncate reviews over a defined character limit (propose 4,000, confirm before implementing).

**Edge cases:**
- Play Store rate limit after sustained pulling → apply Section 6's backoff parameters.
- App Store yields very few IN reviews → expected, not a failure, report honestly.
- Reddit search returns irrelevant matches (e.g., usernames containing "blinkit," unrelated spam) → basic relevance filter requiring a delivery/order/app-related keyword alongside "blinkit."
- Emoji-only or empty-text reviews → exclude from volume counts.
- Network interruption mid-pull → resume from last checkpoint (fully wired in Phase 5).
- Devanagari script encoding errors → explicit UTF-8 handling, tested with a real sample.

**Validation checklist:** Exact row counts per source, dedupe count reported, 10-review manual spot-check (real dates/ratings/text) before Phase 3.

**Tests:** Unit test for dedupe (deliberately duplicated pair → exactly one survives). Unit test for truncation (oversized string → truncates at limit).

**Preconditions:** Phase 1 fully verified.

**If something breaks:** Confirm checkpoint resume works without re-pulling completed sources.

---

### Phase 3 — Tagger: Category-Exploration Taxonomy

**Goal:** Design a tagging schema specific to category-exploration behavior, and tag every cleaned review with structured, validated output. This is the core intellectual work of the whole project — the schema determines whether the eventual insights are actually useful.

**What I'll see when it's done:** Every review has a linked tag record; example outputs shown for sanity-check before the full run; documented schema definition.

**Files:** `prompts/tagging_prompt.md` (the single most important artifact in this build), `auto_tag.py`, schema definition file.

**Proposed schema fields** (review and adjust before implementing): `theme` (which of the 8 questions this relates to, can be multiple), `sentiment` (positive/negative/neutral), `category_mentioned` (grocery/pharmacy/electronics/beauty/pet/baby/other/none-unclear), `behavior_signal` (repeat-only/attempted-new-category/abandoned-attempt/unclear), `pain_point` (short text), `unmet_need` (short text), `trust_barrier_mentioned` (boolean + text — directly answers "what information do users need before trying a new category"), `severity` (low/med/high), `key_quote` (verbatim, capped, must be an exact substring — verified in Phase 4).

**Step-by-step plan:**
1. Lock the schema before writing the prompt.
2. Batch reviews (propose 15 at a time, due to Groq schema-enforcement API constraints) using Llama 3.3 70B with a schema-enforcing prompt.
3. Parse defensively; malformed JSON → retry once with a stricter prompt; skip + log after 2 failures.
4. Store in `tags` table, linked by review ID.

**Edge cases:**
- Model declines a flagged review (profanity/anger) → distinct failure mode from malformed JSON, log and skip.
- Schema drift (extra/missing fields) → validate the full schema on every response.
- Partial batch success → retry only the missing ones individually.
- Hinglish/mixed-language review → test explicitly, confirm quality doesn't degrade.
- No clear category mentioned → schema must allow `none/unclear` rather than forcing a guess.
- Quota exhausted mid-run → checkpoint after every batch.

**Validation checklist — this is the direct answer to the brief's "how did you validate insight quality" requirement:**
- Human spot-check: manually review a random sample (propose N=30–50), compare human judgment against the LLM's tag, calculate an agreement rate. **This must be a real, calculated figure — the direct answer to requirement #12.**
- Cross-field sanity check: severity should roughly correlate with sentiment.

**Tests:** Hand-written test reviews with known correct tags, run as an automated test — assert output matches expectations.

**Preconditions:** Phase 2 complete.

**If something breaks:** API downtime mid-run → this is what the fallback/cache pattern (Section 7) exists for.

---

### Phase 4 — Synthesizer: Answering All 12 Requirements

**Goal:** Aggregate tagged data into direct, evidenced answers to the 8 research questions, and explicitly demonstrate the 4 process-transparency requirements.

**What I'll see when it's done:** `insight_report.md`/`.pdf` with one section per question, each with a data-backed claim, real aggregate numbers, and 3+ real verbatim quotes; a separate `validation_summary.md` stating methodology and the actual agreement-rate result.

**Files:** `synthesizer.py`, `reports/insight_report.md`, `reports/validation_summary.md`

**Step-by-step plan:**
1. Roll up tags by theme × segment × sentiment into a crosstab.
2. For each of the 8 questions, generate a synthesized answer using Groq Llama 3.3 70B, fed the crosstab plus top quotes per theme — not raw text of every review.
3. Write `validation_summary.md` explicitly.
4. Export as Markdown and PDF.

**Edge cases:**
- Thin data on a question → report as an honest data gap, not a manufactured confident answer.
- Synthesizer paraphrases a quote instead of transcribing exactly → **must be caught programmatically** (see Tests).
- PDF export breaks on emoji/Devanagari → test specifically.

**Validation checklist:** Every quote confirmed as an exact substring of a real review. Each of the 8 questions has a non-empty evidenced answer, or an explicit "insufficient data" note.

**Tests:** Automated quote-verification script (exact substring match) — a hard gate before PDF export, not a manual spot-check.

**Preconditions:** Phase 3 complete with calculated agreement rate.

**If something breaks:** Any quote fails verification → block PDF export until fixed. Hard stop.

---

### Phase 5 — Backend Orchestration

**Goal:** A single `pipeline.py` running Phases 2–4 end to end, with Section 6's resilience parameters actually implemented as real values.

**What I'll see when it's done:** `python pipeline.py` executes scrape → clean → tag → synthesize with a visible progress log; safely re-runnable, pulling only new reviews.

**Files:** `pipeline.py`, checkpoint/lock state file

**Step-by-step plan:** Wire the phases together; implement concrete numeric values for requests/minute, checkpoint frequency, quota tracking, timeout, and the 3-strikes cooldown rule.

**Edge cases:**
- Pipeline interrupted (sleep/network drop) → resumes from last checkpoint, no duplicate work.
- Concurrent runs → lock file prevents corruption.
- Daily quota exhausted mid-run → pauses cleanly, resumable next day.

**Validation checklist:** Deliberately interrupt mid-run, restart, confirm correct resume with no duplicated/lost data.

**Tests:** The interrupt-and-resume test above is required and must pass — it is the test for this phase.

**Preconditions:** Phases 2–4 individually verified.

**If something breaks:** Corrupted lock file → documented manual recovery (delete lock, verify DB state, resume).

---

### Phase 6 — Streamlit Frontend

**Goal:** A working dashboard — status, insights, Q&A chat, raw data browse — with the fallback-data flag (Section 7) visibly implemented.

**What I'll see when it's done:** `streamlit run app.py` opens a working dashboard; refresh works; fallback/cached data is always visibly flagged when shown.

**Files:** `app.py`, `ui/` components

**Step-by-step plan:** Build the tab structure, wire each to the real database, implement the fallback-flag UI explicitly.

**Edge cases:**
- Dashboard opened before any pipeline run → clear empty-state messaging.
- Out-of-scope Q&A question → the model says it doesn't know rather than fabricating a plausible answer — **test explicitly.**
- Large volume slows chart rendering → paginate/sample.

**Validation checklist:** Every chart/number has an adjacent plain-English interpretation. Deliberately disable the Groq API key to confirm the fallback flag actually fires.

**Tests:** The deliberate API-key-disable test is required.

**Preconditions:** Phase 5 has completed at least one full real run.

---

### Phase 7 — End-to-End Testing & Accuracy Check

**Goal:** A fresh, systematic pass through every validation checklist item from Phases 1–6, plus finalizing the formal accuracy numbers.

**What I'll see when it's done:** A test report showing pass/fail on every edge case and validation item, and the final locked agreement-rate figure.

**Files:** Expansion of `tests/`, `test_report.md`

**Step-by-step plan:** Systematically re-run every Phase 1–6 validation item, document results, finalize the spot-check sample if not already locked.

**Edge cases:** This phase exists to surface remaining edge cases — anything found is a real bug to fix.

**Validation checklist:** Every Phase 1–6 item passes, or has a documented, explicitly accepted reason why not.

**Tests:** This phase's output *is* the test suite — automated where feasible, documented manual steps otherwise.

**Preconditions:** Phases 1–6 complete.

---

### Phase 8 — Deploy, Polish & Deliverables

**Goal:** A live public URL, the exported PDF report, and 1-slider content ready for the final deck.

**What I'll see when it's done:** A public URL that works cold (fresh session, not logged in on the dev machine); `insight_report.pdf` ready to link as a deliverable; a one-slide "how this works" summary ready to paste into the deck.

**Files:** Deployment config, final README polish

**Step-by-step plan:** Deploy to Streamlit Community Cloud free tier; test the public URL in a fresh/incognito session; confirm no secrets or API keys are exposed anywhere in the public repo, including git history.

**Edge cases:**
- API key accidentally present in git history even if removed from current files → check history explicitly, not just current state, before making the repo public.
- Streamlit Community Cloud's resource limits differ from local → confirm the deployed app serves the already-collected/tagged database rather than attempting a live full re-scrape on every visitor, which would likely exceed free-tier limits or take too long.
- Deployed app crashes on cold start due to an environment variable only ever set locally → explicit deployment checklist for every required env var.

**Validation checklist:** Fresh incognito-browser test of the live public URL. Secret-scan of the repository before making it public.

**Tests:** The cold-start test of the deployed (not local) app is the required test for this phase.

**Preconditions:** Phase 7 complete with everything passing.

---

## 10. The phase document protocol — this is how we actually work, no exceptions

Section 9 above is **context, not the deliverable.** Here is the real protocol:

1. Right now: read this entire file. Review Section 9 critically — add any edge cases you know that we don't (failure modes specific to `google-play-scraper`, `app-store-scraper`, Reddit's current JSON endpoint behavior, or the Groq API), and flag anything you'd structure differently. Share this as a review. **Do not create any files. Do not write any code.**
2. When I type **"Implement Phase N"** — that exact phrase, and only then — you create a **new, separate file**, `docs/phaseN_<name>.md`, containing that phase's finalized, implementation-ready architecture (same structure as Section 9's entries: Goal, What I'll see, Files, Step-by-step, Edge cases, Validation checklist, Preconditions, If something breaks) — built from the corresponding part of Section 9, expanded and finalized, not copied verbatim.
3. You implement that phase's actual code.
4. You **stop**, report what was built and how I can verify it, and wait.
5. You do **not** begin Phase N+1 — not even to "get a head start" — until I explicitly say so. Every phase is a separate, gated step.

This applies to every one of the 8 phases, without exception.

---

## 11. Success criteria for the whole project

I'll consider this done when all of these are true:

- I can run `streamlit run app.py` locally and the app opens in my browser.
- The dashboard shows charts with real data from real reviews — never mock/injected data in anything user-facing.
- The refresh button works and only pulls new reviews on subsequent runs.
- I can upload a manual CSV for any source that can't be auto-scraped, and it appears correctly in the database.
- The insights view gives a clear, evidenced answer to each of the 8 research questions (Section 3), each with real user quotes as support.
- The 4 process-transparency requirements (Section 3, items 9–12) are each demonstrable, including a named, working insight validation methodology.
- The Q&A feature lets me ask free-form questions and get answers sourced from the actual data.
- I can export the insight report as PDF.
- A README in the project root explains setup and run instructions.
- Each phase document (created per Section 10) accurately describes what was actually built in that phase.

---

## 12. One more thing — tell me if something's missing

If, at any point, you think this brief is missing something that matters for a strong outcome — a better technique, a data source I haven't considered, a validation method that would be more convincing, anything — **raise it explicitly and explain why**, but do not build it into the project until I've confirmed I want it included.

---

## 13. Tone and explanation style for me

- Plain English, like explaining to a smart PM friend over coffee.
- Define technical terms in brackets the first time: "We'll use SQLite (a small database that lives in one file, no server needed)."
- Describe what changed in human terms: "Created the scraper file. It pulls Play Store reviews for Blinkit. Tested it — it works."
- Don't dump code at me unless I ask. Summarize what it does.
- On errors: (1) what happened, (2) why, (3) what you're doing about it.

---

## 14. Your first action right now

After reading this entire file, do exactly this and nothing more:

1. Confirm you've read it: reply "I've read the README."
2. Confirm you understand the fallback-resilience pattern in Section 7.
3. Share your review of Section 9 (edge cases to add, anything you'd restructure) as an overview.

Do not create the `docs/` folder yet. Do not create any phase-specific files. Do not write any code. Wait for me to type **"Implement Phase 1"** — that phrase, specifically, is what starts Phase 1, and nothing before it does.
