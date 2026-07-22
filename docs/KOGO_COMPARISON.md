# Comparison: Coded Pipeline vs. Original No-Code KOGO Agent

## Scope note

The original brief for this project was "AI-Driven Analysis of B2C Customer Calls" — sentiment, intent, and escalation classification. The closest available real KOGO artifact for direct comparison is a related but distinct tool: a **call QA / agent-performance scoring agent**, which evaluates how well the *agent* conducted a call (26 metrics such as greeting completeness, persuasion score, SOP compliance) rather than classifying the *customer's* sentiment/intent. The specific subject differs, but both are "audio call → AI analysis → structured score" systems built for the same general business context (Arinox/Blackberrys customer service), making the architectural and engineering comparison below fair and directly relevant, even though the exact output categories aren't 1:1.

## Side-by-side comparison

| Aspect | No-code KOGO agent | This coded pipeline |
|---|---|---|
| **Transcription** | Delegated to a platform-provided speech-to-text tool inside the no-code agent; not directly configurable, not benchmarked against alternatives. | Deliberately evaluated two options (`faster-whisper` vs. Deepgram) on real audio, documented the failure of the free option, and switched only with direct evidence. |
| **Core analysis method** | One large prompt asking an LLM to return all 26 scores in a single JSON response — "prompt the LLM and trust the output," with no independent verification of any individual score. | Purpose-built classification/zero-shot models for each task (sentiment, intent), each producing a real calibrated confidence score, explicitly checked against a threshold before being trusted. |
| **Handling uncertainty** | None. Every score is accepted as-is once it's within its allowed numeric range (a sanity clamp, not a confidence check). | Explicit `"uncertain"` state built into the data model itself — low-confidence predictions are never silently presented as fact. |
| **Failure handling** | If the LLM call fails, silently substitutes generic "moderate" default scores and only marks this with a label change (`"Auto-Scored (FALLBACK)"`) buried in an agent-name field — the dashboard could easily display fabricated-looking "average" performance for a call that was never actually assessed. | Explicit `"no_speech_detected"` status for unanalyzable calls, and a `try`/`except` per call in the batch runner so one failure doesn't corrupt or halt the rest — failures are visible, not disguised as mediocre-but-real results. |
| **Explainability** | Output is just numeric scores — no reasoning or evidence attached to any individual number. | Every escalation score is accompanied by a plain-language `reasons` list tracing exactly which signals (keywords, sentiment, trend) contributed and why. |
| **Cost model** | Every single call requires a hosted LLM API call by design — no free-tier or local option exists in the architecture. | Sentiment and intent run on free local models by default; the one paid dependency (transcription) was adopted deliberately and only after proving the free option's real-world failure. |
| **Validation approach** | No visible mechanism for testing output against known-correct labels within the agent itself. | Built a ground-truth validation script (`validate.py`) against real manually-labeled calls, found and fixed a real bug (ambiguous "escalate" keyword) using that evidence, and documented what still doesn't work. |
| **Engineering process visibility** | Configured through a no-code interface — no commit history, no visible iteration/debugging trail, no way to show *how* the system was built or what tradeoffs were made. | Full Git history: every design decision, bug found, and fix applied is a traceable commit with a message explaining why — directly presentable as evidence of the engineering process, not just the end result. |
| **Customization** | Bound to whatever the no-code platform's chat-agent primitives support; scoring criteria are defined once in a prompt, not independently testable or tunable per metric. | Every threshold, weight, and category is an explicit, independently adjustable constant in code (`CONFIDENCE_THRESHOLD`, `STRONG_KEYWORD_WEIGHT`, `CANDIDATE_INTENTS`, etc.), each one demonstrably revised in response to real evidence during this project. |

## What this comparison demonstrates

The most defensible conclusion isn't "the coded version is smarter" — the underlying LLMs/models in both systems are comparable in raw capability. The real difference is **engineering discipline around trusting AI output**: the no-code agent's architecture has no mechanism to distinguish a confident, correct answer from a low-confidence guess or an outright failure — it always presents *something* as if it were a real result. This project's core contribution was building exactly that missing layer: confidence thresholds, explicit uncertainty states, explainable scoring, and evidence-based validation — the difference between an AI wrapper and an AI *system*.

## Honest limitations of this comparison

- Only the QA-scoring agent's backend logic was available for direct inspection, not the original sentiment/intent/escalation agent this project was directly modeled on — some comparison points are inferred from the closest available real system, not a perfect apples-to-apples match.
- No output-level comparison (e.g., running the same call through both systems side-by-side) was performed — this is a comparison of *architecture and process*, not of raw output accuracy between the two systems.
