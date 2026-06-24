# Edge Cases & Corner Scenarios

This document catalogs edge cases, boundary conditions, and corner scenarios for the AI-powered restaurant recommendation system. Use it during implementation, testing, and QA.

**Related docs:** [context.md](./context.md) · [architecture.md](./architecture.md) · [implementation-plan.md](./implementation-plan.md)

---

## Table of Contents

1. [How to Use This Document](#how-to-use-this-document)
2. [Data Ingestion & Preprocessing](#1-data-ingestion--preprocessing)
3. [User Input & Validation](#2-user-input--validation)
4. [Filtering Layer](#3-filtering-layer)
5. [Groq / LLM Integration](#4-groq--llm-integration)
6. [Response Parsing](#5-response-parsing)
7. [Orchestrator & Pipeline](#6-orchestrator--pipeline)
8. [Presentation Layer (UI)](#7-presentation-layer-ui)
9. [Configuration & Environment](#8-configuration--environment)
10. [Security & Abuse](#9-security--abuse)
11. [Performance & Concurrency](#10-performance--concurrency)
12. [Deployment & Infrastructure](#11-deployment--infrastructure)
13. [Cross-Cutting Scenarios](#12-cross-cutting-scenarios)
14. [Edge Case Priority Matrix](#edge-case-priority-matrix)

---

## How to Use This Document

Each edge case includes:

| Column | Description |
|--------|-------------|
| **ID** | Unique reference (e.g., `DATA-01`) |
| **Scenario** | What can go wrong or behave unexpectedly |
| **Expected Behavior** | What the system should do |
| **Handling Strategy** | Implementation guidance |

**Severity legend:**

| Severity | Meaning |
|----------|---------|
| 🔴 Critical | Can break the app, leak data, or produce dangerously wrong output |
| 🟠 High | Major UX failure or incorrect recommendations |
| 🟡 Medium | Degraded experience; fallback should apply |
| 🟢 Low | Minor annoyance; nice to handle |

---

## 1. Data Ingestion & Preprocessing

### External Data Source

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| DATA-01 | 🔴 | Hugging Face dataset unavailable (network down, repo removed) | App fails gracefully with clear error | Retry with exponential backoff (3 attempts); use local Parquet cache if present; block recommendation flow if no cache |
| DATA-02 | 🟠 | Hugging Face download interrupted mid-transfer | Partial/corrupt cache | Validate file integrity after download; delete corrupt cache and retry; do not load incomplete Parquet |
| DATA-03 | 🟠 | Dataset schema changed (column renamed or removed) | Preprocessor fails loudly | Log missing columns at startup; map fields defensively; fail fast with schema mismatch message |
| DATA-04 | 🟡 | Dataset version updated with new rows | Stale cache serves old data | Optional cache TTL or `--refresh-data` flag; document manual refresh |
| DATA-05 | 🟡 | Empty dataset returned (zero rows) | No recommendations possible ever | Detect empty DataFrame after load; show admin/setup error, not user-facing empty search |

### Missing & Invalid Field Values

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| DATA-06 | 🟠 | Restaurant missing `name` or `location` | Row excluded from store | Drop row during preprocessing; log dropped count |
| DATA-07 | 🟡 | Missing `rating` | Row kept or dropped based on policy | Prefer drop if rating required for filtering; or default to `0.0` and exclude from min-rating queries |
| DATA-08 | 🟡 | Missing `cost` / unparseable cost string (e.g., `"-"`, `"N/A"`, `"₹300-₹600"`) | Budget tier unknown | Parse ranges (use midpoint); mark `budget_tier=unknown`; exclude from strict budget filter or treat as all tiers |
| DATA-09 | 🟡 | Missing `cuisine` | Restaurant excluded from cuisine filter | Set cuisine to `["Unknown"]`; may not match user cuisine queries |
| DATA-10 | 🟡 | Missing `votes` | Pre-ranking tie-break unavailable | Default votes to `0`; sort by rating only |
| DATA-11 | 🟢 | Empty string fields (`""`) | Treated as missing | Normalize blanks to `None` before validation |

### Data Type & Format Anomalies

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| DATA-12 | 🟠 | Rating stored as string (`"4.5/5"`, `"NEW"`, `"-"`) | Numeric rating extracted or row dropped | Strip suffixes; handle `"NEW"` as unrated; coerce with `pd.to_numeric(errors="coerce")` |
| DATA-13 | 🟡 | Rating out of range (negative, > 5, > 10 scale) | Clamped or normalized | Detect scale (e.g., /10 → /5); clamp to 0–5 |
| DATA-14 | 🟡 | Cost as range string (`"300, 600"`, `"₹1,000"`) | Single numeric extracted | Strip currency symbols and commas; parse min/max and use midpoint for tier |
| DATA-15 | 🟡 | Cost as non-numeric text (`"Budget Friendly"`) | Tier derived heuristically or unknown | Map known keywords; else `budget_tier=unknown` |
| DATA-16 | 🟡 | Cuisine as multi-value string (`"North Indian, Chinese, Fast Food"`) | Split into list | Split on `,`, `;`, `/`; trim whitespace; dedupe |
| DATA-17 | 🟢 | Cuisine with inconsistent casing (`"italian"`, `"ITALIAN"`) | Normalized for matching | Title-case or lowercase all cuisines at preprocess time |
| DATA-18 | 🟡 | Location with extra whitespace or suffix (`"Bangalore "`, `"Bangalore, Karnataka"`) | Consistent matching | Trim; optionally extract city from compound address |
| DATA-19 | 🟡 | Location aliases (`"Bengaluru"` vs `"Bangalore"`) | Both match same city | Maintain alias map in config |
| DATA-20 | 🟢 | Duplicate restaurants (same name + location) | Single record kept | Deduplicate keeping highest rating or most votes |

### Cache & Storage

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| DATA-21 | 🟠 | Corrupt Parquet cache file | Reload from source | Catch read errors; delete cache; re-download |
| DATA-22 | 🟡 | Cache directory not writable | In-memory-only mode or error | Create `data/processed/` if missing; warn if write fails |
| DATA-23 | 🟡 | Disk full during cache write | Preprocessing completes in memory | Catch `OSError`; log warning; continue without cache |
| DATA-24 | 🟢 | Very large dataset (memory pressure) | App remains responsive | Use chunked processing; consider dtype optimization; load subset for MVP if needed |

---

## 2. User Input & Validation

### Required Fields

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| INPUT-01 | 🟠 | All required fields empty on submit | Validation error; no API call | Block submit in UI; return 400 with field-level errors |
| INPUT-02 | 🟡 | Only some required fields missing | Specific field errors shown | Pydantic validation per field |
| INPUT-03 | 🟡 | Whitespace-only location or cuisine (`"   "`) | Treated as empty | Strip strings before validation; reject if empty after strip |

### Location

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| INPUT-04 | 🟠 | Location not in dataset (e.g., `"Tokyo"`) | Zero results with helpful message | Validate against known cities list; suggest closest matches or popular cities |
| INPUT-05 | 🟡 | Location partial match (`"Ban"` for Bangalore) | Autocomplete or fuzzy match | Dropdown from dataset cities; optional fuzzy search |
| INPUT-06 | 🟡 | Location with special characters (`"Delhi/NCR"`) | Parsed safely | Sanitize input; match alias map |
| INPUT-07 | 🟢 | Mixed case location (`"bangalore"`, `"BANGALORE"`) | Case-insensitive match | Normalize to title case before filter |

### Budget

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| INPUT-08 | 🟠 | Invalid budget value (not low/medium/high) | Validation error | Enum constraint in `UserPreferences` |
| INPUT-09 | 🟡 | Budget omitted but other fields present | Validation error | Required field in model and UI |

### Cuisine

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| INPUT-10 | 🟠 | Cuisine not present in dataset (e.g., `"Ethiopian"`) | Zero results | Show empty state; suggest available cuisines for selected location |
| INPUT-11 | 🟡 | Multi-cuisine input (`"Italian, Chinese"`) | Match restaurants with either cuisine | Split input; OR logic across cuisine tokens |
| INPUT-12 | 🟡 | Cuisine substring match (`"Ind"`) | Unintended broad matches | Prefer exact or prefix match on known cuisine list |
| INPUT-13 | 🟢 | Cuisine with typos (`"Itailan"`) | No or few results | Optional fuzzy match or "did you mean" suggestion |

### Minimum Rating

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| INPUT-14 | 🟠 | Rating below 0 or above 5 | Validation error | Clamp or reject in Pydantic (`ge=0, le=5`) |
| INPUT-15 | 🟡 | Rating exactly 0 | All rated restaurants pass | Allow; document behavior |
| INPUT-16 | 🟡 | Rating exactly 5 | Very few results | Empty state with suggestion to lower threshold |
| INPUT-17 | 🟡 | Float precision edge (`3.999999`) | Treated as ~4.0 | Round to 1 decimal for display; use raw float for filter |
| INPUT-18 | 🟢 | Non-numeric rating from UI (`"abc"`) | Validation error | Numeric input control in Streamlit; server-side validation |

### Additional Preferences (Free Text)

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| INPUT-19 | 🟡 | Empty additional preferences | Normal flow; field ignored | Optional field defaults to `None` |
| INPUT-20 | 🟡 | Very long text (10,000+ chars) | Truncated before prompt | Cap length (e.g., 500 chars); warn user |
| INPUT-21 | 🔴 | Prompt injection attempt (see Security section) | Ignored by LLM; no system override | Sanitize + system prompt guardrails |
| INPUT-22 | 🟢 | Non-English preferences | LLM handles if capable | Pass through; Groq models generally multilingual |
| INPUT-23 | 🟢 | Emoji or unicode in preferences | No crash | UTF-8 safe handling throughout |

---

## 3. Filtering Layer

### Zero & Low Result Scenarios

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| FILTER-01 | 🟠 | Zero restaurants match all filters | Empty response; no Groq call | Return `recommendations=[]` with guidance: lower rating, change cuisine, broaden budget |
| FILTER-02 | 🟡 | Exactly 1 restaurant matches | Single recommendation returned | Groq ranks 1 item; UI shows one card |
| FILTER-03 | 🟡 | Fewer than 5 matches (e.g., 2–3) | Return all available, ranked | Groq ranks available count; don't pad with invented entries |
| FILTER-04 | 🟡 | Many matches (500+) before cap | Top N sent to Groq | Pre-rank by rating/votes; cap at `MAX_CANDIDATES` (20) |
| FILTER-05 | 🟡 | Strict budget yields zero; adjacent tier has results | Relaxed results with notice | Expand to adjacent budget tier; flag `budget_relaxed=True` in response |

### Filter Logic Edge Cases

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| FILTER-06 | 🟡 | Location filter too broad (city name substring in address) | Possible false positives | Prefer city column match over address contains |
| FILTER-07 | 🟡 | Location filter too strict (neighborhood vs city) | Miss valid restaurants | Document match strategy; use contains on city field |
| FILTER-08 | 🟡 | Cuisine partial overlap (`"Cafe"` in `"Cafe, Italian"`) | Match if token present | Tokenize restaurant cuisines; case-insensitive compare |
| FILTER-09 | 🟡 | Restaurant with multiple cuisines; user wants one | Match if any cuisine fits | Intersection logic on cuisine lists |
| FILTER-10 | 🟡 | Rating tie between restaurants | Deterministic order | Secondary sort by votes, then name |
| FILTER-11 | 🟢 | All filtered restaurants have identical rating | Stable sort | Tertiary sort by name ascending |
| FILTER-12 | 🟡 | Budget tier unknown on restaurant | Excluded from strict budget filter | Include only if policy allows unknown tier in relaxed mode |
| FILTER-13 | 🟡 | User min_rating excludes all in location+cuisine | Empty result | Suggest lowering min_rating in message |

### Pre-Ranking & Candidate Selection

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| FILTER-14 | 🟡 | Top-rated candidates all same cuisine | Diversity may be low | Optional diversity boost in pre-rank (future); document as known limitation |
| FILTER-15 | 🟡 | High-rated but low votes (new restaurant) | Still eligible | Include in candidates; LLM may mention "newer spot" |
| FILTER-16 | 🟠 | Pre-rank excludes best LLM match (soft preference) | Acceptable trade-off | Soft prefs handled by Groq within top N; increase N if quality drops |
| FILTER-17 | 🟢 | `MAX_CANDIDATES=0` misconfigured | Error at startup | Validate config > 0 |

---

## 4. Groq / LLM Integration

### Authentication & Configuration

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| GROQ-01 | 🔴 | Missing `GROQ_API_KEY` | Fail fast at startup | Clear error: "Set GROQ_API_KEY in .env" |
| GROQ-02 | 🔴 | Invalid or revoked API key | Groq returns 401 | Catch auth error; show setup message; no silent fallback that hides misconfiguration |
| GROQ-03 | 🟡 | Wrong model name configured | 404 or model error | Validate model at startup smoke test; fallback to `llama-3.1-8b-instant` |
| GROQ-04 | 🟡 | Primary model unavailable | Use fallback model | Try fallback model once; then rule-based fallback |

### Rate Limits & Availability

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| GROQ-05 | 🟠 | Rate limit hit (`429 Too Many Requests`) | Retry or fallback | Exponential backoff (1 retry); then rule-based top 5 |
| GROQ-06 | 🟠 | Groq service outage (5xx) | Fallback recommendations | Rule-based ranking + `fallback_used=True` |
| GROQ-07 | 🟡 | Request timeout (slow response) | Retry once, then fallback | Set timeout (e.g., 30s); log latency |
| GROQ-08 | 🟡 | Concurrent requests exhaust quota | Queued or rejected | Single-user MVP: serialize requests; show "please wait" in UI |
| GROQ-09 | 🟢 | Token limit exceeded (too many candidates in prompt) | Reduce candidates | Cap candidates; truncate prompt; log token estimate |

### Prompt & Model Behavior

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| GROQ-10 | 🔴 | LLM invents restaurant not in candidate list | Hallucination rejected | Parser validates name against candidates; drop invalid entries |
| GROQ-11 | 🟠 | LLM returns fewer than 5 recommendations | Show available count | No padding; return 1–4 if valid |
| GROQ-12 | 🟠 | LLM returns duplicate ranks or duplicate restaurants | Dedupe and re-rank | Parser normalizes ranks; remove duplicates |
| GROQ-13 | 🟡 | LLM returns markdown-wrapped JSON (` ```json ... ``` `) | JSON still parsed | Strip code fences before `json.loads` |
| GROQ-14 | 🟡 | LLM returns prose instead of JSON | Parse fails → retry/fallback | Retry with stricter prompt; then fallback |
| GROQ-15 | 🟡 | LLM returns empty `recommendations` array | Fallback or empty UI | Treat as failure; use rule-based top 5 |
| GROQ-16 | 🟡 | LLM explanation contradicts filters (wrong cuisine cited) | Metadata from data wins | Display cuisine/rating/cost from dataset, not LLM |
| GROQ-17 | 🟡 | LLM ranks clearly worse restaurant #1 | Accept with caveat | MVP accepts LLM ranking; optional re-rank by rating in future |
| GROQ-18 | 🟢 | Summary field missing | Optional field omitted | `summary=None`; UI hides section |
| GROQ-19 | 🟢 | Summary field overly long | Truncated in UI | Cap display length (e.g., 500 chars) |
| GROQ-20 | 🟡 | Temperature too high → inconsistent rankings | Same input, different order | Use `temperature=0.3`; document non-determinism |
| GROQ-21 | 🟡 | Soft preference impossible to satisfy (no "outdoor seating" data) | LLM acknowledges in explanation | Prompt instructs honesty when data lacks attribute |

### Token & Payload Limits

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| GROQ-22 | 🟡 | Candidate list exceeds context window | Truncate candidates | Hard cap at 20; send minimal fields only |
| GROQ-23 | 🟢 | Restaurant name extremely long | Prompt still valid | Truncate name in prompt payload only |
| GROQ-24 | 🟡 | `max_tokens` too low → truncated JSON | Invalid JSON | Set adequate `max_tokens`; retry on parse failure |

---

## 5. Response Parsing

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| PARSE-01 | 🟠 | Invalid JSON syntax | Retry then fallback | `json.loads` in try/except; one repair retry |
| PARSE-02 | 🟠 | Valid JSON but wrong schema (missing `recommendations`) | Fallback | Schema validation; reject and fallback |
| PARSE-03 | 🟡 | Extra unexpected JSON fields | Ignored safely | Pydantic `model_config extra=ignore` |
| PARSE-04 | 🟡 | `rank` missing or non-integer | Auto-assign ranks | Sort by position or assign 1..N |
| PARSE-05 | 🟡 | `restaurant_name` case mismatch (`"truffles"` vs `"Truffles"`) | Fuzzy match to candidate | Case-insensitive lookup in candidate map |
| PARSE-06 | 🟠 | LLM uses index instead of name (`"restaurant_3"`) | Match fails | Prompt explicitly requires exact name; reject unknown |
| PARSE-07 | 🟡 | Explanation field empty | Default template explanation | Fill: "Recommended based on your preferences." |
| PARSE-08 | 🟡 | More than 5 recommendations returned | Truncate to top 5 | Take ranks 1–5 only |
| PARSE-09 | 🟢 | Unicode in explanation | Display correctly | UTF-8 end-to-end |
| PARSE-10 | 🟡 | Candidate merged but restaurant removed from list mid-parse | Skip entry | Lookup error → drop recommendation |

---

## 6. Orchestrator & Pipeline

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| ORCH-01 | 🟠 | Filter succeeds but Groq fails | Fallback recommendations | Top 5 pre-ranked + template explanations + `fallback_used=True` |
| ORCH-02 | 🟡 | Filter returns empty | Skip Groq entirely | Empty response with user guidance |
| ORCH-03 | 🟡 | Partial Groq success (3 valid of 5 parsed) | Return 3 valid | Don't fail entire response for partial parse |
| ORCH-04 | 🟠 | Exception mid-pipeline | User-friendly error | Catch at orchestrator boundary; log stack trace; generic error in UI |
| ORCH-05 | 🟡 | Dataset not loaded at request time | 503 error | Lazy load on startup; health check before serving |
| ORCH-06 | 🟢 | Double submit (user clicks twice) | Idempotent or debounced | Disable button during loading; ignore duplicate in-flight requests |
| ORCH-07 | 🟡 | `total_candidates_considered` mismatch | Accurate count | Set from filter output length before Groq |
| ORCH-08 | 🟢 | Orchestrator called with stale preferences object | Uses submitted snapshot | Pass immutable preference snapshot per request |

---

## 7. Presentation Layer (UI)

### Form & Input UX

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| UI-01 | 🟡 | User submits without selecting location | Inline validation error | Required field markers; disable submit until valid |
| UI-02 | 🟡 | Slider for rating not moved (default 0) | Default value documented | Sensible default (e.g., 3.5); show current value |
| UI-03 | 🟢 | Browser refresh mid-request | Loading state cleared | Streamlit rerun handles; show last result or empty |
| UI-04 | 🟡 | Location dropdown empty (data not loaded) | Setup error shown | Load cities at app init; show spinner then error |

### Results Display

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| UI-05 | 🟠 | Zero results | Actionable empty state | Suggest: lower rating, change cuisine, try adjacent budget |
| UI-06 | 🟡 | Fallback mode active | User informed | Banner: "AI unavailable — showing filter-based picks" |
| UI-07 | 🟡 | Missing optional fields in result (no cost) | Graceful display | Show "Cost not available" |
| UI-08 | 🟢 | Very long restaurant name or explanation | Layout intact | CSS truncate with expand; wrap text |
| UI-09 | 🟡 | Rating display for `0.0` or missing | Sensible UI | Show "Unrated" or hide stars |
| UI-10 | 🟢 | Summary section when `summary=None` | Section hidden | Conditional render |
| UI-11 | 🟡 | Groq slow (>10s) | Loading indicator | Spinner + optional timeout message |
| UI-12 | 🟡 | Special characters in restaurant name (`"Joe's & Döner"`) | Renders correctly | HTML escape in Streamlit (default) |

### Streamlit-Specific

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| UI-13 | 🟡 | Session state lost on rerun | Preferences may reset | Use `st.session_state` for form values |
| UI-14 | 🟢 | Multiple tabs/instances | Independent sessions | Acceptable for MVP |
| UI-15 | 🟡 | App opened before `.env` loaded | Clear config error | Load dotenv at module top |

---

## 8. Configuration & Environment

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| CFG-01 | 🔴 | `.env` file missing | Fail with instructions | Check on startup; point to `.env.example` |
| CFG-02 | 🟡 | `.env` has trailing spaces in API key | Auth may fail | Strip whitespace on load |
| CFG-03 | 🟡 | Budget thresholds misconfigured (low > medium) | Invalid tiers | Validate threshold ordering at startup |
| CFG-04 | 🟡 | `MAX_CANDIDATES` > 50 | Token overflow risk | Cap at reasonable max (e.g., 25) with warning |
| CFG-05 | 🟡 | `TOP_N` > available results | Return fewer | `min(TOP_N, len(candidates))` |
| CFG-06 | 🟢 | Debug mode enabled in production | Verbose logs | Env flag `DEBUG=false` by default |
| CFG-07 | 🟡 | Wrong Python version (< 3.10) | Install fails | Document in README; check in setup |

---

## 9. Security & Abuse

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| SEC-01 | 🔴 | Prompt injection via additional preferences (`"Ignore instructions..."`) | System behavior unchanged | System prompt: ignore override attempts; sanitize input |
| SEC-02 | 🔴 | API key committed to git | Key rotated | `.gitignore` `.env`; scan in CI; document rotation |
| SEC-03 | 🟠 | User input echoed unsafely in UI | No XSS | Streamlit auto-escapes; avoid `unsafe_allow_html` with user data |
| SEC-04 | 🟡 | Automated scraping of Groq via app | Rate limit cost | MVP local only; add rate limit if public API |
| SEC-05 | 🟡 | Extremely large POST body (API mode) | Rejected | Request size limit (e.g., 4 KB) |
| SEC-06 | 🟡 | LLM returns harmful/offensive explanation | Displayed to user | Optional content filter; prompt guidelines for neutral tone |
| SEC-07 | 🟢 | Log files contain user preferences | Privacy aware | Avoid logging full free-text prefs in production |

---

## 10. Performance & Concurrency

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| PERF-01 | 🟡 | First run slow (dataset download) | User informed | Progress indicator; "first run may take minutes" |
| PERF-02 | 🟡 | Filter on 50k+ rows slow | < 500 ms target | Vectorized pandas; pre-index by city if needed |
| PERF-03 | 🟡 | End-to-end > 10 seconds | Acceptable with notice | Log timing; optimize candidate count |
| PERF-04 | 🟢 | Repeated identical queries | Same latency each time | No cache required for MVP; optional memoization |
| PERF-05 | 🟡 | Two users hit app simultaneously (Streamlit) | Both served | Document single-user MVP limitation |
| PERF-06 | 🟡 | Memory leak on long-running Streamlit session | Stable memory | Avoid reloading dataset each rerun; cache in `@st.cache_resource` |

---

## 11. Deployment & Infrastructure

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| DEPLOY-01 | 🟠 | Docker container without network on first run | Cannot download dataset | Pre-bake Parquet in image or mount volume |
| DEPLOY-02 | 🟠 | Secret not injected in cloud deploy | Groq calls fail | Use secrets manager for `GROQ_API_KEY` |
| DEPLOY-03 | 🟡 | Container restart loses in-memory cache | Reload from Parquet volume | Persist `data/processed/` on volume |
| DEPLOY-04 | 🟡 | Clock skew / TLS issues calling Groq | API errors | Standard HTTPS; retry on transient errors |
| DEPLOY-05 | 🟢 | Read-only filesystem | Cache write fails | Fall back to in-memory store |

---

## 12. Cross-Cutting Scenarios

### End-to-End User Journeys

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| E2E-01 | 🟠 | New user, valid prefs, happy path | 5 ranked results with explanations | Primary flow — must always work |
| E2E-02 | 🟠 | Picky user: high rating + narrow cuisine + strict budget | Empty or 1–2 results | Empty state guidance |
| E2E-03 | 🟡 | User relaxes one filter after empty result | More results on retry | "New search" flow; keep form values |
| E2E-04 | 🟡 | Groq down during demo | Fallback results shown | `fallback_used` banner |
| E2E-05 | 🟡 | Dataset city has only one cuisine type | Low diversity | LLM explains best available options |
| E2E-06 | 🟢 | User searches same city twice with different cuisines | Independent results | Stateless per-request pipeline |

### Data + LLM Consistency

| ID | Severity | Scenario | Expected Behavior | Handling Strategy |
|----|----------|----------|-------------------|-------------------|
| CONS-01 | 🟠 | LLM explanation mentions wrong budget tier | User sees correct cost from data | Always display cost/rating from dataset fields |
| CONS-02 | 🟡 | Restaurant closed/permanently shut (stale dataset) | Not known to system | Document dataset staleness in UI footer |
| CONS-03 | 🟡 | Rating in dataset outdated | Shown as-is | Display "data as of [cache date]" if available |

### Boundary Values (Quick Reference)

| Input | Boundary | Expected |
|-------|----------|----------|
| `min_rating` | `0.0` | All rated restaurants eligible |
| `min_rating` | `5.0` | Only perfect-rated (likely empty) |
| `budget` | each tier | Filter to matching `budget_tier` |
| Candidates | `0` | No Groq call |
| Candidates | `1` | Single recommendation |
| Candidates | `20+` | Cap at `MAX_CANDIDATES` |
| Groq output | `0` valid parses | Fallback |
| Groq output | `1–5` valid | Return valid subset |

---

## Edge Case Priority Matrix

Use this matrix to prioritize test coverage in Phase 7.

### Must Test Before MVP (P0)

| IDs |
|-----|
| DATA-01, DATA-06, DATA-12, DATA-21 |
| INPUT-01, INPUT-04, INPUT-08, INPUT-14 |
| FILTER-01, FILTER-04, FILTER-05 |
| GROQ-01, GROQ-05, GROQ-10, GROQ-14 |
| PARSE-01, PARSE-02, PARSE-05 |
| ORCH-01, ORCH-02 |
| UI-05, UI-06 |
| SEC-01, SEC-02 |
| E2E-01, E2E-02, E2E-04 |

### Should Test (P1)

| IDs |
|-----|
| DATA-08, DATA-14, DATA-19 |
| INPUT-10, INPUT-11, INPUT-20 |
| FILTER-02, FILTER-03, FILTER-10 |
| GROQ-03, GROQ-07, GROQ-11, GROQ-12, GROQ-13 |
| PARSE-04, PARSE-07, PARSE-08 |
| ORCH-03, ORCH-06 |
| UI-01, UI-07, UI-11 |
| CFG-03, CFG-04 |
| PERF-01, PERF-02 |

### Nice to Have (P2)

All remaining IDs in sections 1–12.

---

## Suggested Test Case Mapping

| Test File | Edge Case IDs |
|-----------|---------------|
| `tests/test_preprocessor.py` | DATA-06 – DATA-20 |
| `tests/test_filter.py` | FILTER-01 – FILTER-13 |
| `tests/test_parser.py` | PARSE-01 – PARSE-10, GROQ-10 – GROQ-13 |
| `tests/test_orchestrator.py` | ORCH-01 – ORCH-05, E2E-01 – E2E-04 |
| `tests/test_preferences.py` | INPUT-01 – INPUT-18 |

---

## Related Documents

- [context.md](./context.md) — Objectives and workflow
- [architecture.md](./architecture.md) — Error handling, fallback, and Groq design
- [implementation-plan.md](./implementation-plan.md) — Phase 7 testing scope and risk register
