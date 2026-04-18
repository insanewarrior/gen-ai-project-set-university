# Design Thinking Session: StrengthWise

**Date:** 2026-04-18
**Facilitator:** Mr.A
**Design Challenge:** StrengthWise — Cross-Domain Strength Coach with Memory

---

## Design Challenge

StrengthWise — a conversational AI coach for niche strength athletes that combines general training knowledge with personal training history to extract insights, detect patterns, and bridge knowledge across strength disciplines — all on a zero-cost AWS architecture built in 7 days.

## Challenge Statement

Strength athletes in niche sports (grip, armwrestling) accumulate training data across spreadsheets and memory but have no systematic way to extract insights, detect patterns, or apply proven principles from adjacent strength disciplines to their own training. They need a tool that *remembers* their history and *connects the dots* across domains — not just another logging app or generic chatbot. The challenge is to design a user experience that makes structured logging frictionless, cross-domain insight retrieval natural, and the entire system viable at zero ongoing cost.

---

## EMPATHIZE: Understanding Users

### User Insights

- **The spreadsheet graveyard:** 13 training cycles logged in XLSX files that are never revisited for patterns. Data exists but insight doesn't.
- **Cross-domain blindness:** Grip athletes don't know that their plateau matches a well-documented pattern in powerlifting periodization. The knowledge exists in books — it's just siloed by sport.
- **The "what should I do today" moment:** Athletes open their phone before a session and either follow a rigid plan that ignores how they feel, or wing it. Neither is optimal.
- **Coach accessibility:** Niche sport athletes rarely have coaches. General coaches don't understand sport-specific demands. Knowledge transfer happens through forums, YouTube, and trial-and-error.
- **Logging friction kills consistency:** If logging takes more than 60 seconds post-session, it doesn't happen. Complex apps get abandoned for simple notes or nothing.

### Key Observations

1. **Insight extraction > data collection.** The real value isn't in recording sets/reps — it's in answering "why did my grip strength stall in cycle 8 but not cycle 5?"
2. **Cross-domain transfer is the moat.** No existing tool connects principles from powerlifting periodization to grip sport programming.
3. **Memory creates trust.** A coach that remembers your history feels like a real coach. A chatbot that asks you to re-explain your background every time feels like a stranger.
4. **Athletes think in narratives, not numbers.** "I felt weak today" is as important as "I lifted 80kg." The system must handle both.
5. **Zero-cost matters for adoption.** Niche sport athletes won't pay $20/month for yet another app. Free tier = real users.

### Empathy Map Summary

| Quadrant | Content |
|----------|---------|
| **Says** | "I don't train systematically" / "I forget what worked" / "I don't know if my program is good" |
| **Thinks** | "There must be a better way" / "Coaches are expensive or don't understand my sport" / "Am I overtraining or undertraining?" |
| **Does** | Logs sporadically in spreadsheets / Follows programs from forums / Switches programs too often / Ignores signs of overtraining |
| **Feels** | Frustrated by stalled progress / Overwhelmed by conflicting advice / Motivated but directionless / Lonely in niche sport training |

---

## DEFINE: Frame the Problem

### Point of View Statement

**A niche strength athlete** needs **a way to extract actionable insights from their accumulated training history and connect them with proven principles from adjacent strength disciplines** because **the knowledge to train smarter already exists — scattered across their own spreadsheets and strength training literature — but no tool bridges the gap between personal data and general expertise.**

### How Might We Questions

1. **HMW** make training logging so fast it becomes invisible (< 30 seconds)?
2. **HMW** surface patterns from a user's training history without them having to ask the right question?
3. **HMW** translate periodization principles from powerlifting/weightlifting into grip sport and armwrestling contexts?
4. **HMW** build coaching trust through memory — so the system feels like a coach who's been with you for years?
5. **HMW** deliver real value at zero marginal cost per user?
6. **HMW** handle the messy human input ("felt weak today", "tweaked my elbow") alongside structured data?
7. **HMW** make cross-domain recommendations feel credible rather than generic?

### Key Insights

- **Insight 1:** The split architecture (structured logging = no LLM, queries = LLM) is itself a UX insight — logging must be frictionless and free, while insight extraction justifies the LLM cost.
- **Insight 2:** The 13 XLSX training cycles represent a *cold start advantage* — most AI coaches start with zero data, but StrengthWise can demonstrate value from day one with historical import.
- **Insight 3:** Cross-domain credibility requires citation. "Powerlifting research shows X, and your data shows Y" is 10x more convincing than "try this."

---

## IDEATE: Generate Solutions

### Selected Methods

| Method | Why |
|--------|-----|
| **SCAMPER Design** | Apply design lenses to existing training tools to find innovation gaps |
| **Crazy 8s (conceptual)** | Force 8 distinct UX approaches for the core interaction |
| **Analogous Inspiration** | Borrow from domains outside fitness tech |

### Generated Ideas

**Core Interaction Models:**
1. Chat-first: everything through conversation (like talking to a coach)
2. Form-first: structured logging with chat for queries only
3. Dashboard-first: visual analytics with chat overlay
4. Voice-first: log training by voice during/after session
5. **Hybrid: structured form for logging, natural language for everything else**
6. Photo-first: snap whiteboard/notebook, OCR extracts data
7. Template-first: pre-built session templates you just fill numbers into
8. Passive-first: import from existing tools (Google Sheets, Strong app)

**Insight Delivery:**
9. On-demand only: user asks, system answers
10. **Proactive nudges: system detects patterns and surfaces them**
11. Weekly digest: automated summary email/message
12. Comparison view: "your cycle 8 vs cycle 5" side-by-side
13. Coach notes: system adds observations to each logged session

**Cross-Domain Features:**
14. "Did you know?" cards linking user patterns to general knowledge
15. **Program analysis: paste any program, get it evaluated against principles + your history**
16. Sport translator: "this powerlifting concept means X for your grip training"
17. Book club: curated knowledge base with personalized excerpts
18. Principle library: browse training principles, see how they apply to your data

**Trust & Memory:**
19. Athlete profile that evolves: system maintains running understanding of you
20. **Training timeline: visual history with annotated milestones and insights**
21. "Remember when..." references in coaching responses
22. Progress narrative: system tells the story of your training journey
23. Assumption tracker: system states what it believes about you, you correct it

**Import & Migration:**
24. **XLSX/CSV bulk import with intelligent parsing**
25. Manual history entry wizard
26. Progressive import: add historical context as conversations happen

**Cost & Architecture:**
27. Tiered responses: quick pattern match (free) vs deep analysis (LLM)
28. **Cached common questions: pre-compute frequent insight patterns**
29. Batch analysis: nightly cron processes new data
30. Community knowledge: anonymized aggregate patterns (future)

### Top Concepts

**Concept A: "The Hybrid Coach" (Selected for MVP)**
- Structured form for session logging (fast, free, no LLM)
- Natural language chat for questions and insight retrieval (LLM, on-demand)
- Dual-source RAG: personal training history + general strength knowledge base
- Cross-domain citations in every response
- XLSX bulk import for cold-start advantage

**Concept B: "The Pattern Detective" (v2 candidate)**
- Same logging approach as Concept A
- Adds proactive pattern detection (when enough data accumulates)
- Weekly insight summaries surfaced automatically
- "Your data suggests..." notifications
- Higher LLM cost but higher engagement

**Concept C: "The Program Analyst" (Merged into A)**
- Paste or describe any training program
- System evaluates it against: (1) general principles, (2) your personal history
- "This program emphasizes X, but your data shows you respond better to Y"
- Lower daily engagement but high-value interactions

**Selected for MVP: Concept A with elements of C** — The Hybrid Coach with program analysis capability.

---

## PROTOTYPE: Make Ideas Tangible

### Prototype Approach

Build a **low-fidelity clickable prototype** covering the 4 core user flows:
1. **Log a session** — structured form, < 30 seconds
2. **Ask a question** — natural language chat with cited response
3. **Import history** — XLSX upload with preview/confirmation
4. **Analyze a program** — paste a program, get evaluation

The prototype should be testable by a single user (you) within 1 day, with hardcoded/mocked responses that represent what the real system would produce.

### Prototype Description

**Screen 1 — Home/Dashboard:**
- Quick-log button (prominent, one-tap access)
- Recent sessions list (last 5)
- Chat input for questions
- "Import Training Data" entry point

**Screen 2 — Session Logging Form:**
- Date (auto-filled: today)
- Sport/discipline selector (grip, armwrestling, running, general strength)
- Exercise list (add rows: exercise name, sets, reps, weight, RPE)
- Free-text notes field ("felt weak", "elbow pain", "new PR")
- Save button -> confirmation -> back to home

**Screen 3 — Chat/Query Interface:**
- Conversational UI (message bubbles)
- System responses include: answer + source citations (which book/principle + which training sessions)
- Suggested follow-up questions
- Cross-domain callouts visually distinct ("From powerlifting research: ...")

**Screen 4 — Program Analysis:**
- Text input area: paste or describe a program
- Analysis output: principle-by-principle evaluation
- Personal overlay: "Based on your 13 cycles, you respond well to X but not Y"

### Key Features to Test

| Feature | Assumption to Validate |
|---------|----------------------|
| Structured form logging | Users will log consistently if it takes < 30 seconds |
| Dual-source RAG responses | Citations from both personal data and general knowledge feel credible |
| Cross-domain recommendations | Athletes trust advice bridged from adjacent sports |
| XLSX import | Historical data can be parsed meaningfully from real spreadsheets |
| Free-text notes | Unstructured input adds real value to later queries |
| Program analysis | "Evaluate my program" is a compelling entry point |

---

## TEST: Validate with Users

### Testing Plan

**Participants:**
1. **Mr.A (you)** — primary user, dogfooding from day 1
2. **2-3 training partners** from grip sport / armwrestling community
3. **1-2 general strength athletes** (test cross-domain value proposition)
4. **1 coach** if accessible (test whether insights match coaching intuition)

**Test Tasks:**
1. Log today's training session using the form — measure time, note friction
2. Ask 3 questions about training history — evaluate response quality and citation credibility
3. Import an XLSX training cycle — note confusion points
4. Paste a training program and ask for analysis — is the output useful?
5. Ask a cross-domain question — does the answer feel credible?

**Capture Method:**
- Think-aloud protocol during tasks
- Post-task rating: usefulness (1-5), trust (1-5), would-use-again (yes/no)
- Note every point of confusion, hesitation, or surprise

### User Feedback

*(To be collected during and after MVP build)*

| Task | Expected Friction Points |
|------|------------------------|
| Session logging | Too many fields? Wrong exercise categories? RPE confusing for beginners? |
| Question asking | Users don't know what to ask? Responses too generic? Citations feel fake? |
| XLSX import | Column mapping fails? Data looks wrong after import? Trust issues? |
| Program analysis | Output too academic? Not actionable enough? Missing user context? |
| Cross-domain | Recommendations feel like a stretch? Not enough domain-specific language? |

### Key Learnings

*(To be filled post-testing)*

| Hypothesis | Status |
|-----------|--------|
| Logging in < 30s drives consistency | To validate |
| Dual-source citations build trust | To validate |
| Cross-domain transfer feels credible | To validate |
| XLSX import provides meaningful cold start | To validate |
| Free-text notes improve query quality | To validate |
| Program analysis is a compelling use case | To validate |

---

## Next Steps

### Refinements Needed

1. **Logging form UX** — test and iterate on field count, defaults, and sport-specific customization. Must survive the "sweaty hands, post-session brain fog" test.
2. **RAG response quality** — tune chunk size, retrieval count, and prompt template to balance citation density vs. readability.
3. **Cross-domain framing** — develop a consistent voice for bridging recommendations ("Powerlifting research suggests... Your data shows... Consider...")
4. **Import pipeline** — handle the messiness of real XLSX files (inconsistent column names, missing data, mixed formats).
5. **Mobile responsiveness** — if athletes log on phones (likely), the form must work on small screens.

### Action Items

| Priority | Action | Phase |
|----------|--------|-------|
| P0 | Define the structured logging schema (exercises, sets, reps, weight, RPE, notes, sport) | Build Day 1 |
| P0 | Build XLSX import parser for the 13 training cycles | Build Day 1 |
| P0 | Curate and chunk the general knowledge corpus (strength training books) | Build Day 1-2 |
| P0 | Implement dual-source FAISS index (personal + general) | Build Day 2 |
| P0 | Build the logging form UI | Build Day 2-3 |
| P0 | Build the chat/query interface with RAG pipeline | Build Day 3-4 |
| P1 | Build program analysis feature | Build Day 4-5 |
| P1 | Implement cross-domain citation formatting | Build Day 4-5 |
| P1 | End-to-end testing with real data | Build Day 5-6 |
| P1 | Deploy to AWS (Lambda + DynamoDB + S3/FAISS) | Build Day 6 |
| P2 | User testing with 2-3 training partners | Build Day 6-7 |
| P2 | Iterate based on feedback | Build Day 7 |
| **Fallback** | If behind by Day 3: drop program analysis, ship general RAG + logging + bare frontend | Day 3 decision |

### Success Metrics

| Metric | Target | How to Measure |
|--------|--------|---------------|
| Session logging time | < 30 seconds | Stopwatch during testing |
| Query response relevance | 4+/5 user rating | Post-query rating |
| Cross-domain citation credibility | 3.5+/5 user rating | Post-query rating |
| XLSX import accuracy | > 90% fields correctly parsed | Manual spot-check |
| AWS steady-state cost | $0/month | AWS billing dashboard |
| Demo day cost | < $1 | AWS billing dashboard |
| MVP completion | Core flows working | Day 6 checkpoint |
| User retention (self) | Daily logging for 2+ weeks post-build | Self-tracking |

---

_Generated using BMAD Creative Intelligence Suite - Design Thinking Workflow_
