# Project Context: AI-Driven B2C Customer Call Analysis (Final Year Project)

## Who I am
- Final-year Mechatronics Engineering student, Manipal Institute of Technology.
- Currently an AI Solutions Intern at Arinox AI (Addison Technologies), building enterprise AI agents on their no-code KOGO platform for clients (Sun Mobility, Ministry of Finance, Blackberrys).
- **No prior coding experience.** I've built agents through prompt engineering / no-code config, not by writing software. This project is my first real coding project.
- I need to be taught from scratch, step by step, and I need to actually understand what's happening (not just have code generated for me), because I have to defend this project in a viva/final presentation.

## The project
At Arinox, I built (via KOGO, no-code) an agent for a client called **"AI-Driven Analysis of B2C Customer Calls"**. It analyzed customer service call transcripts for insights.

For my final year project, I want to **rebuild the same concept from scratch with real code**, to prove I can do actual technical/software engineering work, not just configure a no-code platform. This will be presented as my Mechatronics final year project.

## Key constraints and decisions already made
- **No hardware available** — this is a pure software project (no robotics/physical component).
- **LiveKit is NOT required.** We initially considered building this as a LiveKit real-time voice agent, but decided against it — it added unnecessary real-time/async complexity (would have required simulating live calls by publishing recorded audio into a fake "room") that isn't essential to the actual goal. We are now doing a straightforward **batch pipeline** instead.
- **Input:** pre-recorded call audio files (not live calls, not a telephony integration).
- **Output required from the analysis:**
  - Sentiment (per call, ideally as a trend/trajectory through the call, not just one score)
  - Intent classification
  - Complaint / escalation flagging
- **Cost preference:** strong preference for free/zero-cost tools where possible (open-source or free-tier APIs).

## Recommended tech stack
- **Transcription:** Whisper — either OpenAI's API, or `faster-whisper` (local, free, runs fine on a laptop) if we want zero API cost.
- **Analysis:** LLM API calls (OpenAI, Anthropic, or an open-source model) for sentiment/intent/escalation classification. Should NOT just be "prompt the LLM and trust the output" — needs some custom scoring/aggregation logic on top (e.g., rolling sentiment trend across a call, confidence thresholds for escalation flags) to show real engineering, not just an API wrapper.
- **Storage:** JSON or SQLite, one structured record per call.
- **Dashboard:** Streamlit — for showing aggregate trends across all processed calls (complaint rate over time, intent distribution, escalation hotlist). This is the demo-facing piece for the viva.
- **Language:** Python throughout.

## Learning + build plan (roughly 4–6 weeks, few hours/day)
Because I have no coding background, teach concepts *as they come up* in the build, not as separate lessons first. Keep explanations grounded in what the code is actually doing in this project.

1. **Phase 0 — Setup (1–2 days):** Python install, VS Code, Git repo (commit history matters — it's evidence of real work for the viva).
2. **Phase 1 — Just enough Python (~1 week):** variables, functions, if/for, dictionaries/JSON, reading/writing files, installing packages with pip. Practice on toy versions of the actual project (e.g. a script that reads a transcript and counts words) rather than generic tutorials.
3. **Phase 2 — Transcription pipeline (3–5 days):** script that takes an audio file and produces a transcript using Whisper.
4. **Phase 3 — Analysis logic (1–1.5 weeks):** sentiment/intent/escalation classification functions, plus the custom aggregation/scoring logic on top. This is the core "I designed this" part of the project — spend real time here.
5. **Phase 4 — Storage + batch runner (3–5 days):** process a folder of call recordings end-to-end, save structured results.
6. **Phase 5 — Dashboard (3–5 days):** Streamlit app to visualize results across all processed calls.
7. **Phase 6 — Testing + report (~1 week):** validate against known example calls with expected labels, write up architecture, compare against the original no-code KOGO version's outputs, prepare the final report/presentation.

## What "done" looks like
A GitHub repo with: ingestion script, transcription module, analysis module (with my own scoring logic, not just raw LLM output), storage layer, Streamlit dashboard, a handful of test cases, and a README with an architecture diagram — plus a written report comparing this coded version to the original no-code KOGO agent (what changed, why it's more flexible/technical, what I learned).

## How to work with me
- I don't know how to code yet. Explain things simply, one concept at a time, tied to what we're building right now.
- Write/run code directly rather than just describing it — I need to see it work.
- Check in on whether I understand a piece before moving to the next one; I need to be able to explain this project myself in a viva.
