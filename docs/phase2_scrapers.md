# Phase 2: Scrapers & Database Population

**Goal:** Pull real reviews from Google Play Store, Apple App Store, and Reddit (using the verified RSS feed approach), clean and deduplicate the data, and store it in SQLite. Real data only — no mock or injected records.

**What I'll see when it's done:**
- The `reviews` table in `blinkit_data.db` populated with real rows.
- An exact count report per source.
- A deduplication report.
- A `docs/reddit_discovery_log.md` documenting exactly which subreddits and search terms were tried via RSS and their real yield.

**Files:**
- `docs/phase2_scrapers.md` (This file)
- `fetch_playstore.py`
- `fetch_appstore.py`
- `fetch_reddit.py`
- `fetch_youtube.py`
- `fetch_consumer_complaints.py`
- `fetch_mouthshut.py`
- `clean.py`
- `run_phase2.py`
- `reddit_discovery_log.md`

**Step-by-step plan:**
5. **Deduplicate**: Deduplicate within each source by hashing `(source + date + text)`.
6. **Store**: Insert all cleaned, deduplicated reviews into the `reviews` table.

**Edge cases:**
- **Network failures / Rate limits**: Each fetcher uses a `requests.Session` with a `urllib3` Retry adapter (3 retries, exponential backoff) or custom retry logic.
- **App Store empty**: Expected behavior per Phase 1. Log and continue.
- **Reddit irrelevant matches**: Basic relevance filter applied during parsing.
- **Emoji-only reviews**: Removed during cleaning.
- **Encoding errors**: Explicit `utf-8` specified on all text operations.
- **Database locked**: Use SQLite timeouts and simple retry loops for inserts.

**Validation checklist:**
- [ ] Exact row counts per source generated.
- [ ] Dedupe count reported.
- [ ] `docs/reddit_discovery_log.md` contains the actual queries and yields.
- [ ] 10-review manual spot-check (real dates/ratings/text) confirmed visually.
- [ ] Deduplication test (deliberate duplicate ignored) passed.
- [ ] Truncation test (oversized string chopped) passed.

**Preconditions:**
- Phase 1 checks passed (Confirmed).

**If something breaks:** 
- If Play Store limits, rely on the exponential backoff.
- If Reddit RSS blocks us again, we will log the zero yield and rely on Play Store data per the brief's allowance for depth over breadth.
