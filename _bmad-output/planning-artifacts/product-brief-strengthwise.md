---
title: "Product Brief: StrengthWise"
status: "complete"
created: "2026-04-18"
updated: "2026-04-18T3"
inputs:
  - "_bmad-output/brainstorming/brainstorming-session-2026-04-18-001.md"
  - "_bmad-output/design-thinking-2026-04-18.md"
  - "_bmad-output/planning-artifacts/research/market-strengthwise-ai-coaching-research-2026-04-18.md"
  - "docs/bmad/BMAD_INPUT.md"
---

# Product Brief: StrengthWise

## Executive Summary

Athletes in niche strength sports — grip, armwrestling, strongman — accumulate years of training data across spreadsheets and memory, but have no way to extract insights from it. General AI tools like ChatGPT can answer training questions, but they forget everything between sessions. Sport-specific apps like ArmProgress log workouts, but offer dashboards, not coaching. No tool connects an athlete's personal training history with proven strength science to deliver cited, sport-specific coaching that remembers who you are.

StrengthWise is a cross-domain AI strength coach with persistent memory, built by a strength athlete and ML engineer who trains in these sports and lives the problem daily. It combines a curated general knowledge base (strength training books, periodization science, proven training cycles) with each athlete's personal training history through dual-source RAG. When you ask "why did my grip stall in cycle 8?", StrengthWise doesn't guess — it retrieves your cycle 8 data, finds relevant periodization principles from its knowledge base, and gives you a cited answer that references both. The architecture is cost-conscious by design: structured logging is always free (no LLM involved), and AI coaching fires only when you ask a question. This isn't just a budget constraint — it's a structural advantage. Competitors burn money on always-on AI features; StrengthWise's event-driven model delivers a genuinely free tier indefinitely.

The market timing is right. LLM inference costs have dropped 10-40x in two years, making per-query AI coaching economically viable for a freemium model. Niche strength sports are growing fast through social media, yet zero tools serve the intersection of sport-specific depth, conversational AI coaching, and persistent personal memory. StrengthWise enters an uncontested niche with near-zero customer acquisition cost, community-driven growth, and a data moat that compounds with every logged session.

## The Problem

Niche strength athletes train without systematic, personalized guidance. The knowledge to train smarter exists — scattered across their own spreadsheets, strength training books, and forum posts — but no tool bridges the gap between personal data and general expertise.

**The spreadsheet graveyard.** Athletes accumulate training logs across XLSX files, notes apps, and various trackers. These logs are never revisited for patterns. Data exists; insight doesn't. The question "why did my grip strength stall in cycle 8 but not cycle 5?" requires manual analysis that nobody has time to perform.

**Cross-domain blindness.** A grip athlete whose plateau matches a well-documented pattern in powerlifting periodization will never know it. Training books exist per discipline, but no tool connects principles across sports. Periodization is periodization — the science transfers, but the translation doesn't happen on its own.

**Every session starts from zero.** ChatGPT can answer a training question, but it doesn't know you stalled on deadlifts in March, that your grip fails before your back does, or that you respond better to high-frequency blocks. You'd need to copy 30 sessions of data, find the right book chapter, write a structured prompt, and still get an answer with no memory of last week's conversation. Nobody actually does this.

**No coaching access.** Niche sport athletes rarely have coaches. General coaches don't understand sport-specific demands. A coach who understands grip sport programming and remembers your training history simply doesn't exist at any affordable price point.

## The Solution

StrengthWise is a conversational AI coach that knows your sport and remembers your history.

**Log training in under 30 seconds.** A structured form captures exercise, sets, reps, weight, RPE, and free-text notes. No LLM involved — logging is instant, free, and works post-session with sweaty hands and brain fog.

**Ask anything about your training.** Natural language chat retrieves answers from two sources simultaneously: your personal training history (stored in DynamoDB) and a curated general knowledge base of strength science (embedded in FAISS). Every response cites both — "Powerlifting research suggests X, and your cycle 5 data confirms Y."

**Value from day one — no history required.** Even your first logged session gives the general knowledge RAG something to anchor advice to. After a few weeks of consistent logging, the personal data source becomes genuinely powerful. Future versions will add XLSX import to rescue years of training data from spreadsheet graveyards, but v1 starts clean and builds forward.

**Analyze any program.** Paste a training program and get it evaluated against general strength principles and your personal response patterns. "This program emphasizes volume, but your data shows you respond better to intensity-focused blocks."

## What Makes This Different

No existing tool combines all three of these capabilities:

**1. Niche sport depth.** StrengthWise understands grip sport implements (grippers, hub lifts, pinch blocks), armwrestling movements (pronation, supination, side pressure), and niche strength programming — not just bodybuilding and generic fitness. Athletes in these sports reject tools that don't speak their language.

**2. Dual-source RAG with citations.** Every AI response draws from both personal training data and general strength science, citing both sources. Personal citations reference specific session dates and metrics; knowledge citations reference the source text and principle. This isn't "try progressive overload" — it's "your volume in cycle 8 was 30% below Prilepin's chart for your intensity range, and your successful cycle 5 used 20% more volume at the same intensity." No existing tool — and no human coach — spans grip, armwrestling, strongman, and powerlifting in a single cited response. This is a category-defining capability.

**3. Persistent memory that compounds.** Every logged session makes the system smarter about you. After three months, StrengthWise knows things about your training patterns that no single ChatGPT conversation could access. This creates both user value and switching costs.

Competitors cover at most two of these three axes. JuggernautAI has AI + sport depth but only for powerlifting ($35/month, no cross-domain). ArmProgress has sport depth for armwrestling but no conversational AI coaching. SensAI has LLM coaching + memory but no niche sport knowledge. Pelaris has advanced LLM architecture but targets multi-sport generalists.

## Who This Serves

**Primary: The Dedicated Niche Athlete.** Age 22-40, trains 3-5x/week in grip sport, armwrestling, or powerlifting. Has 2+ years of training experience and accumulated data in spreadsheets. Trains without systematic periodization. Cannot access or afford sport-specific coaching. Discovers tools through Reddit, Discord, and GripBoard — not the app store. Won't pay for generic fitness apps but will pay for something that genuinely understands their sport.

**Secondary: The Crossover Strength Enthusiast.** Trains multiple strength modalities (e.g., powerlifting + grip, strongman + armwrestling). Actively seeks knowledge transfer between disciplines. The cross-domain RAG capability is most valuable to this user — bridging principles they couldn't connect on their own.

**Market size:** The serviceable addressable market is 500K-2M dedicated niche strength athletes globally (OpenPowerlifting tracks ~980K competitive powerlifters alone; armwrestling market valued at $150M in 2025). The serviceable obtainable market — English-speaking, digitally active, tool-seeking athletes — is 50K-200K. Year 1 target: 500+ active users through organic community growth.

## Business Model

**Freemium with metered AI coaching.**

- **Free tier (always):** Structured training logging, training history dashboard. No LLM cost — sustainable at any user count.
- **Free AI queries:** 3 coaching queries per day (10/day during first week to ensure the "aha moment" isn't throttled during onboarding).
- **Premium (~$7-10/month):** Unlimited AI coaching queries, program analysis, priority response quality. Positioned well below JuggernautAI ($35/month), above commodity trackers ($5/month).

**Cost architecture:** Structured logging costs $0 (Python validation + DynamoDB write). AI queries cost ~$0.01-0.03 each (embed → FAISS search → DynamoDB fetch → one LLM call). LLM inference costs continue to drop ~10x/year, improving unit economics over time.

**Unit economics (12-month projection):**

| Metric | Conservative | Optimistic |
|--------|-------------|-----------|
| Active users | 500 | 1,000 |
| Paid conversion | 5% | 10% |
| Paying subscribers | 25 | 100 |
| Monthly revenue (~$8.50/mo avg) | ~$210 | ~$850 |
| LLM costs (all users, free + paid) | ~$150 | ~$450 |
| AWS infra (DynamoDB, Lambda, S3) | ~$20 | ~$50 |
| **Net monthly** | **~$40** | **~$350** |

Break-even requires ~20 paying subscribers. Conservative scenario is tight but viable; optimistic scenario is comfortably self-sustaining. The 10/day onboarding query limit and 3/day steady-state limit keep free-tier LLM costs bounded.

**Data ownership:** Users own their data. Full export (CSV) and account deletion available at any time. Data encrypted at rest in DynamoDB. No data sharing with third parties.

**Growth model:** Community-driven, zero paid marketing. Primary channels: Reddit (r/GripTraining ~95K, r/armwrestling ~45K, r/powerlifting ~450K), GripBoard forums, Discord servers. One authentic endorsement from a respected community member outperforms any ad campaign. Built by a strength athlete, not a tech company — genuine credibility in tight-knit communities.

## Success Criteria

| Metric | Target | Rationale |
|--------|--------|-----------|
| Personal daily use | Daily logging + weekly queries | Dogfooding validates real utility |
| Infrastructure self-sufficiency | Revenue covers costs within 12 months | Product must sustain itself |
| Active users (12 months) | 500+ | Organic community growth, zero paid marketing |
| Session logging time | < 30 seconds | Friction kills consistency |
| First dual-cited AI response | Within session 1 | The "aha moment" that determines adoption |
| 90-day retention | > 50% (vs 31% industry avg) | Memory-based value should compound retention |
| Freemium-to-paid conversion | 5-10% | Metered paywall with daily free queries |

## Knowledge Base

The general knowledge corpus — StrengthWise's "coaching brain" — is curated from:
- **13 XLSX powerlifting training cycles** (builder's own data) with self-calculated formulas, parsed via openpyxl + one-time LLM into natural language descriptions of training logic, periodization structure, and progression schemes — used as general knowledge corpus content, not as user import
- **3-5 strength training books/PDFs** covering periodization principles, progressive overload models, and sport-specific programming (chunked and embedded)
- Sport-specific exercise databases for grip, armwrestling, and general strength movements

All content is embedded into a FAISS index that works identically on local dev and AWS (file in S3). Corpus quality directly determines response quality — this is the most important pre-build asset.

## Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| **AI gives bad training advice** | High | Every response cites sources so users can verify. Explicit disclaimers: not medical advice. User feedback mechanism to flag bad responses. |
| **Cold start without historical data** | Medium | General knowledge RAG provides value from first session. Personal data compounds over weeks of logging. XLSX import planned for v2 to accelerate cold start. |
| **7-day build scope is aggressive** | High | 3-day fallback explicitly defined. Core architecture (RAG + logging) prioritized over polish. |
| **Copyright risk from embedded books** | Medium | Use freely available training principles and public-domain content where possible. Chunked excerpts for educational use. Replace with original content over time. |
| **Competitor adds persistent memory** | Medium | True moat is community trust + curated niche corpus + accumulated user data, not the architecture alone. Window is narrow — ship fast and build data moat. |
| **Single-developer dependency** | Medium | Open architecture on standard AWS services. No proprietary infrastructure. User data exportable. |

## Scope

**v1 (7-day capstone build):**
- Structured training logging form (sport selector, exercises, sets/reps/weight/RPE, notes)
- Dual-source RAG query engine (personal history + general knowledge)
- Program analysis (paste program, get evaluation)
- Cross-domain cited responses
- AWS deployment: Lambda, DynamoDB, S3/FAISS, API Gateway, Cognito
- Basic frontend: log page, chat page, history page

**Explicitly NOT in v1:**
- Proactive pattern detection / weekly auto-alerts (v2 — needs data accumulation)
- Community or social features (athletes use existing forums)
- Coach-facing tools / B2B multi-athlete management
- Wearable integration
- XLSX bulk import for historical training data (v2 — high value but technically risky for 7-day build)
- Voice or photo-based logging
- Mobile app (web-first, mobile-responsive)

**3-day fallback:** If behind by Day 3, drop program analysis. Ship general RAG + structured logging + bare frontend. Still a working product with the core dual-source architecture.

## Vision

If StrengthWise succeeds, it becomes the default training companion for niche strength athletes worldwide — the coach who knows your sport, remembers your history, and gets smarter every session.

Year 1: A self-sustaining product used daily by hundreds of grip, armwrestling, and powerlifting athletes. Revenue covers infrastructure. Community word-of-mouth drives steady growth.

Year 2: Expansion into adjacent strength sports — strongman, Olympic weightlifting, Highland games. The dual-source RAG architecture is sport-agnostic; only the knowledge corpus needs updating. Deeper cross-domain transfer as the knowledge base grows. Proactive pattern detection surfaces insights athletes didn't think to ask about.

The long game: the most comprehensive training memory system for strength athletes. Every logged session, every query, every insight compounds into a personal training intelligence that no competitor can replicate and no athlete would want to leave behind.
