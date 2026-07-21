# Project Log — Phase-by-Phase Notes

Working notes for report writing. Covers what was built, what broke, why decisions were made, and what's still unresolved, phase by phase. Written as things happened, not cleaned up in hindsight — the issues and dead ends are intentionally kept in, since they're real engineering evidence.

---

## Phase 0 — Setup

**What was done:**
- Verified Python, Git, VS Code already installed.
- `git init` in the project folder, `.gitignore` created (initially covering `venv/`, `__pycache__/`, `.env`).
- Set local Git identity (`user.name`/`user.email`, scoped to this repo only — not global) using GitHub-noreply-style email for privacy.
- Created a Python virtual environment (`venv/`) so project dependencies stay isolated from system Python.
- Created a GitHub repo and connected it as `origin`, pushed initial commit. Renamed default branch `master` → `main`.

**Issues faced:**
- None major — first commit failed once due to missing Git identity, fixed immediately.

**Gaps / left for later:**
- None — Phase 0 is fully complete.

---

## Phase 1 — Core Python, practiced on toy versions of the real pipeline

**What was done:**
- File I/O: `open()`/`with`, read vs. write vs. binary modes, why `with` guarantees file closure (resource-leak/lock risk otherwise).
- Functions, `return`, parameters — refactored raw script logic into reusable functions.
- Loops (`for`), conditionals (`if`), string methods (`.split()`, `.lower()`, `in`).
- Lists and dictionaries as structured data; nested dictionaries.
- JSON: `json.dump`/`json.load`, and *why* JSON (bridges Python data structures directly to a storage format).
- `os.makedirs(..., exist_ok=True)` and a dedicated `output/` folder for generated results, kept out of Git (regenerable, not source code) — same reasoning applied later to `venv/`.

**Issues faced:**
- `.split()` on raw text does not strip punctuation — noted as a future data-cleaning concern once real sentiment/intent analysis started (Phase 3).
- Transcript-splitting produced a trailing empty string (files ending in a newline) — filtered out, but flagged as a reminder that real-world text data has invisible quirks that must be checked, not assumed.

**Gaps / left for later:**
- None blocking — this was foundational practice, not final pipeline code.

---

## Phase 2 — Transcription pipeline (Whisper)

**What was done:**
- Chose `faster-whisper` (local, free, open-source Whisper model) over OpenAI's paid Whisper API — zero cost, runs fully offline once the model is downloaded once.
- Built `transcribe.py`: loads `WhisperModel("base", device="cpu", compute_type="int8")`, transcribes an audio file into timestamped segments, saves as structured JSON (`start`, `end`, `text` per line) — same JSON-per-record pattern as Phase 1.
- Created `requirements.txt` via `pip freeze` so the environment is reproducible without committing `venv/`.

**Issues faced:**
- On real test audio (`sample_call_2.mp3`, `sample_call_3.mp3`), the `"base"` Whisper model produced badly garbled or outright nonsensical transcriptions on accented/code-switched Hindi-English speech.
- Tried the larger `"small"` model as a fix — made things *worse* on one file: it **hallucinated** (produced fluent-looking but meaningless Devanagari text) rather than admitting uncertainty. This is a known Whisper failure mode on unclear/noisy audio, not something model size alone fixes.
- Hit a real Windows-specific bug: printing Hindi (Devanagari) text to the terminal crashed with `UnicodeEncodeError`, because Windows' default terminal encoding (`cp1252`) can't represent it. Root cause was the *terminal*, not the code — JSON files written with explicit `encoding="utf-8"` were unaffected. Fixed by setting `PYTHONIOENCODING=utf-8` when running scripts and being explicit about UTF-8 encoding on all file writes.

**Gaps / left for later:**
- `faster-whisper` was ultimately judged not reliable enough for this project's real Hindi/English audio and was supplemented by Deepgram (see Phase 3) — worth deciding in Phase 4/6 whether `faster-whisper` stays as a fallback option or is dropped entirely from the final pipeline.

---

## Phase 3 — Analysis logic (sentiment, intent, escalation)

This was the core "designed, not just wrapped" part of the project. Broken into sub-sections below since a lot happened.

### 3a. Sentiment analysis

**What was done:**
- Model: `cardiffnlp/twitter-xlm-roberta-base-sentiment-multilingual` (free, local, multilingual — required for Hindi+English audio).
- Built `classify_sentiment()`: wraps raw model output with a **confidence threshold** (`CONFIDENCE_THRESHOLD = 0.6`) — predictions below this are relabeled `"uncertain"` rather than trusted as-is.
- Built trend aggregation (`trend.py`): converts trusted labels to numeric scores (`positive=1`, `neutral=0`, `negative=-1`), explicitly **excludes** `"uncertain"` lines from the numeric average (rather than folding them into neutral, which would silently distort the meaning of "neutral"). Compares first-half vs. second-half averages to output `"improving"`/`"declining"`/`"stable"`.
- Tracks `uncertain_ratio` per call and flags the whole result `overall_confidence: "low"` if more than 50% of lines were too ambiguous to trust.

**Issues faced:**
- On the initial tiny/garbled test transcript, 60% of lines were `"uncertain"` — a stress test that validated the threshold logic was actually doing something, not just decoration.
- `sum(scores) / len(scores)` on an empty list (all lines uncertain) would crash with `ZeroDivisionError` — guarded against explicitly in `compute_average()`.

**Gaps / left for later:**
- `CONFIDENCE_THRESHOLD = 0.6` and the "improving/declining" difference threshold (`0.2`) are both judgment calls, not empirically tuned — flagged for validation against more real calls in Phase 6.

### 3b. Transcription source: Whisper → Deepgram

**What was done:**
- Given Whisper's real accuracy problems (see Phase 2), switched to **Deepgram's API** (`nova-2` model, `utterances=true` for timestamped segments) for at least the problematic real-audio test cases. User supplied their own Deepgram API key (free-tier usage).
- API key stored only in `.env` (never hardcoded, never committed — `.env` was gitignored from Phase 0).
- Deepgram's output on the same audio was dramatically more coherent than Whisper's — a real, evidence-based justification for the switch (documented via direct side-by-side transcripts, not just described).

**Issues faced / tradeoffs:**
- Unlike `faster-whisper` (fully local, no key, no per-use cost), Deepgram is a hosted paid service requiring an API key, internet access, and (beyond free tier) ongoing cost. This tradeoff — accuracy vs. cost/dependency — is worth stating explicitly in the report.

**Gaps / left for later:**
- No formal decision yet on whether the final Phase 4 batch pipeline uses Deepgram exclusively, `faster-whisper` exclusively, or picks per-call/falls back — needs to be decided before Phase 4.

### 3c. Privacy: redaction

**What was done:**
- Real audio/transcripts contained genuine sensitive data (client company name, a customer's name). Rather than blanket-excluding all transcripts from Git, built a **redaction pipeline** (`redact.py`) so transcripts could still be used/shared with identifying info removed.
- Two-layer approach: (1) NER model (`dslim/bert-base-NER`, free/local) auto-detects entity types like organizations; (2) a hardcoded keyword list as a safety net for known terms, since NER alone proved unreliable.
- Per explicit direction, only **organization/company** mentions are redacted — personal names are left as-is (judged not reliably/consistently identifiable enough by the NER model to bother, and lower privacy risk in this context than the company name).
- Raw audio files and raw (non-redacted) transcripts remain excluded from Git entirely (`*.mp3`, `*.wav`, `*.m4a`, `output/` all gitignored) — redaction only affects what *could* be shared, it doesn't change what's committed by default.

**Issues faced:**
- The NER model **missed one instance of the company name entirely** (false negative) and **misclassified another instance** as a person instead of an organization, in testing on the exact same transcript. This directly motivated adding the keyword-list safety net.
- Key design realization: for redaction specifically, a **false negative (missing something) is worse than a false positive (over-redacting)** — the opposite priority from the sentiment/intent confidence thresholds, where low-confidence guesses are *distrusted*. Worth explicitly contrasting in the report as two different applications of the same underlying "don't blindly trust model output" principle.

**Gaps / left for later:**
- Redaction has only been tested on one real call transcript — needs broader testing across more calls before being trusted as reliable (Phase 6).
- Keyword safety net is currently hardcoded (`"blackberry"`, `"blackberrys"`) — not a general solution for unknown future company/client names without manual updates.

### 3d. Intent classification

**What was done:**
- Method: zero-shot classification (`MoritzLaurer/mDeBERTa-v3-base-mnli-xnli`, free/local, multilingual) — lets custom candidate labels be defined without training a dedicated model.
- Initial candidate list (`order status`, `complaint`, `refund request`, etc.) was a **guess**, not grounded in real data — confidence scores were consistently too low to trust (0.26–0.38 on real calls).
- Diagnosed *why*: (1) more candidate categories = harder task than 3-class sentiment (lower random-guess baseline), (2) transcript quality itself limits classification, (3) classifying isolated single-line fragments (rather than the whole call) is a poor fit for a call-level property like intent — fixed by classifying the joined full transcript instead of per-line.
- **Grounded the category list in real data**: extracted only aggregate category names/counts (zero personal data) from two internal Excel exports — an outbound call log (~6,500 rows) and a customer support ticket system (~2,655 rows). Found the real data reflects apparel-retail-specific categories (Order Shipping, Defect, Return/Refund, Alteration, Exchange, etc.) and outbound sales/retention-style calls, not just inbound complaints. Rebuilt the candidate list accordingly. Documented in `docs/intent_taxonomy_reference.md` (aggregate-only, safe to share).
- Both source Excel files were **deleted** after extraction per privacy requirements — the raw data contained real customer names, phone numbers, emails.
- Applied the same confidence-threshold pattern as sentiment (`INTENT_CONFIDENCE_THRESHOLD = 0.4`, deliberately lower than sentiment's 0.6 to reflect intent's harder, more-categories task).

**Issues faced:**
- Even after grounding categories in real data, confidence on a real test call (`sample_call_3`) only rose modestly (0.28 → 0.34 → 0.36 across iterations) — still below threshold, correctly flagged `"uncertain"`.
- Root cause identified: that particular call is a genuine **blend** of intents (retention call + product inquiry + return-policy explanation) that doesn't cleanly match any single category — and the category list has no plain "general product inquiry" (non-defect) option, a real gap.

**Gaps / left for later:**
- Category list still needs a "general product inquiry" (or similar) category to close the gap found above.
- Only validated on one real call in depth — needs broader testing in Phase 6 to see if 0.4 threshold and the 8 categories generalize.

### 3e. Escalation flagging

**What was done:**
- Combined signals into one explainable weighted score (`escalate.py`): keyword matches (reusing Phase 1's exact technique) + overall negative sentiment (below -0.3) + declining trend + high ratio of negative-vs-trusted lines (>30%).
- Each triggered factor adds weighted points **and** a human-readable reason string appended to a `reasons` list — the score is never an opaque number, it's traceable back to specific evidence. Final score bucketed into `Low`/`Medium`/`High`.
- Tested on `sample_call_3`: correctly scored `0`/`"Low"` with an empty reasons list, matching the call's genuinely positive resolution ("Thank you so much").

**Issues faced:**
- None yet — this is the least-tested piece so far (only one real call run through it end-to-end).

**Gaps / left for later:**
- Weights (`40`/`30`/`20`/`10`) and thresholds (`-0.3`, `30%`) are initial judgment calls, entirely untested against a range of real escalated vs. non-escalated calls — this is probably the single most important thing to validate in Phase 6, since a wrong threshold here has the most real-world consequence (missing a genuine escalation, or crying wolf on a fine call).

### 3f. Local model vs. paid LLM comparison (sentiment)

**What was done:**
- Built `compare_sentiment.py` to test whether a general-purpose LLM (via API) would out-perform the purpose-built local sentiment model, using OpenAI (`gpt-4o-mini`) and Gemini (`gemini-2.0-flash`) with API keys supplied by the user.
- Design note: LLMs don't natively output a calibrated confidence score the way a classification model does — had to explicitly prompt for self-reported confidence as JSON, and parse it. Flagged as a materially weaker signal than the local model's real softmax-based confidence.
- Wrapped both API calls in `try`/`except` so failures don't crash the whole comparison run.

**Issues faced:**
- **Both APIs failed on every single test line** with quota/billing errors: OpenAI returned `insufficient_quota` (429), Gemini returned `RESOURCE_EXHAUSTED` with an explicit `limit: 0` for the free tier. Neither is a code bug — both accounts are not actually funded/enabled for API use, despite having valid keys.
- Decision made: rather than requiring the user to configure billing just for this side comparison, accepted the result as-is.

**Result / conclusion for the report:**
- The local model completed all 8 test lines in **0.03–0.11 seconds each**, with zero setup, zero cost, and zero external dependency.
- Both paid alternatives, despite being "good" models in principle, were **not usable in practice** without additional account configuration — a real, legitimate finding that reinforces (rather than undermines) the decision to build the core pipeline on free local models: they don't have this class of deployment/reliability risk.

**Gaps / left for later:**
- No real head-to-head accuracy comparison was actually obtained — only the local model produced valid results. If billing gets configured later, this comparison could be re-run for a fuller picture, but it is *not* a blocker for the rest of the project.

---

## Open items carried into Phase 4 and beyond

1. Decide `faster-whisper` vs. Deepgram (or both, with fallback logic) for the batch pipeline.
2. Add a "general product inquiry" intent category to close the gap found in real-call testing.
3. All thresholds (`0.6` sentiment, `0.4` intent, escalation weights/thresholds, `0.2` trend difference) are unvalidated judgment calls — Phase 6 testing against known-labeled calls should specifically check whether these need tuning.
4. Redaction has only been validated on one transcript — needs broader testing.
5. Only one real call (`sample_call_3`) has been run through the *entire* pipeline end-to-end (sentiment + intent + escalation together) — Phase 4's batch runner will be the first real multi-call stress test.
