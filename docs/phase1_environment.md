# Phase 1: Environment & Connection Verification

**Goal:** Confirm every external connection actually works before any real data collection begins — Groq Llama 3.3 API, Play Store scraper, App Store scraper, Reddit search endpoint, local database, local dashboard shell.

**What I'll see when it's done:** 
- A verification script (`verify_setup.py`) that pings all four external connections and prints a clear pass/fail for each.
- An empty SQLite database file (`blinkit_data.db`) with the full schema already created.
- `streamlit run app.py` opens a blank dashboard shell without errors.

**Files:**
- `docs/phase1_environment.md` (This file)
- `.env` / `config.yaml`
- `init_db.py`
- `verify_setup.py`
- `app.py`
- `requirements.txt`

**Step-by-step plan:**
1. Create `requirements.txt` listing all necessary free Python libraries.
2. Create the config template (`.env.example` and `config.yaml`) with placeholders for the Groq Llama 3.3 API key and db path.
3. Design and create the database schema in `init_db.py`: a `reviews` table (raw cleaned text + metadata), a `tags` table (Groq's structured output per review, linked by review ID), an `insights` table (synthesized answers per research question), a `validation_log` table (spot-check results, agreement rates), and a `fallback_cache` table with an explicit `is_fallback` boolean flag (never mixed into the main `reviews`/`tags` tables).
4. Write one test call per source in `verify_setup.py`: a trivial Groq Llama 3.3 prompt, a single Play Store review pull, a single App Store review pull, a single Reddit search query (with `User-Agent` header) — each wrapped so a failure prints a plain-English cause, not a stack trace.
5. Provide a basic `app.py` for Streamlit testing.

**Edge cases:**
- **Missing or invalid Groq Llama 3.3 API key:** `verify_setup.py` catches this and provides a clear message, not a stack trace.
- **Groq Llama 3.3 Rate Limits:** Even if quota is available, the free tier has strict RPM limits. A trivial ping might succeed while batch processing later fails.
- **Play Store package name typo or app removed:** Validated by checking the returned result exists.
- **App Store ID resolves to the wrong storefront / scraper fails:** The `app-store-scraper` returned a JSON parse error because Apple blocks/throttles the scraper. Tested Apple's official RSS feed (`https://itunes.apple.com/in/rss/customerreviews/id=960335206/sortBy=mostRecent/json`) which returned 200 OK but 0 reviews for both Blinkit and Swiggy in IN. Handled by treating JSON errors from the scraper as a graceful '0 reviews' state to prevent crashing the pipeline.
- **Reddit's JSON endpoints:** The unauthenticated `search.json` endpoint universally returns a 403 Forbidden due to recent Reddit API changes blocking programmatic non-OAuth access. Replaced with Reddit's RSS feed (`https://www.reddit.com/r/india/search.rss?q=blinkit&restrict_sr=on&sort=new`) parsed as XML, using a standard Chrome User-Agent, which returns 200 OK and successfully bypasses the restriction without requiring developer apps.
- **SQLite file can't be created:** Handled via a local storage write test.
- **Local Streamlit port already in use:** Streamlit handles this gracefully by picking another port, but user should be aware.

**Validation checklist:**
- [x] All external connection checks pass (Green) in `verify_setup.py`.
- [x] Database file has all five tables with correct schemas (visually confirmed or tested via script).
- [x] Streamlit opens locally with no console errors.
- [x] Directory is writable.

**Preconditions:**
- Groq Llama 3.3 API key obtained (User needs to put it in `.env`).
- Confirmed IN storefront details for both stores.

**If something breaks:** 
- Groq Llama 3.3 quota error on first test call → confirm RPM limits aren't exceeded for the trivial ping. 
- Play Store returns `None` → re-verify package name against the live listing. 
- Reddit returns 429 → check the User-Agent header fix.
