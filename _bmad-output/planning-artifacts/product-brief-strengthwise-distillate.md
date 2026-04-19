---
title: "Product Brief Distillate: StrengthWise"
type: llm-distillate
source: "product-brief-strengthwise.md"
created: "2026-04-18"
purpose: "Token-efficient context for downstream PRD creation"
---

# Product Brief Distillate: StrengthWise

## Rejected Ideas (do not re-propose)

- **Sports #1: Training Memory** — conversational query over personal history only. Rejected: too thin without general knowledge source
- **Sports #2: Adaptive Coach** — weekly agent-driven plan adaptation. Rejected: too expensive (LLM on every plan cycle), too complex for 7-day build
- **Sports #3: Niche Sport Knowledge Base** — community-level dataset building. Rejected: requires community contributions, chicken-and-egg problem
- **Sports #5: Training Pattern Detective** — proactive pattern detection as standalone. Rejected: merged into StrengthWise as v2 stretch goal
- **Sports #6: Program Translator** — parse programs, map against principles. Rejected as standalone; program analysis merged into StrengthWise MVP
- **Research #1-3: PhD-focused ideas** (Feasibility Filter, Journal Matcher, Progress Tracker). Rejected: user explicitly excluded research/academic angle
- **Hybrid #1: StrengthWise + Research Paper** — dual-purpose product + paper. Rejected: user explicitly said this is a product, not academic project
- **Wild #1: Coach-as-a-Service API** — B2B angle. Rejected for v1: requires validated individual product first
- **Voice-first logging** — rejected: adds complexity, structured form is faster for strength athletes
- **Photo-first logging** — rejected: OCR from notebooks unreliable, not worth build time
- **Passive-first logging** — rejected: import from other apps (Google Sheets, Strong) adds integration complexity
- **Dashboard-first interaction** — rejected: hybrid model (form for logging, chat for queries) won over pure dashboard
- **XLSX import for v1** — deprioritized to v2: technically risky for 7-day build, messy real-world spreadsheets with inconsistent formats. Athletes start fresh in v1

## Requirements Hints

- **Logging form fields:** date (auto-today), sport/discipline selector (grip, armwrestling, running, general strength), exercise list (exercise name, sets, reps, weight, RPE per row), free-text notes field ("felt weak", "elbow pain", "new PR")
- **Logging time target:** < 30 seconds per session. Must pass "sweaty hands, post-session brain fog" mobile test
- **Free-text notes are first-class data:** "felt weak today" is as important as "80kg x 5" — system must handle both structured and unstructured input in queries
- **Sport-specific exercise recognition is critical:** if a grip athlete types "gripper close" or "hub lift" and the system doesn't recognize it, trust is instantly broken. Exercise database must be pre-populated for grip, armwrestling, and powerlifting
- **Citation format in AI responses:** personal citations reference specific session dates and metrics; knowledge citations reference source text and principle name. Both must appear in every dual-source response
- **Rate limiting:** 3 free AI queries/day steady state, 10/day during first week of onboarding. Premium: unlimited
- **Data export:** CSV export of all training data available to all users (free and paid). Account deletion fully supported
- **Data encryption:** at rest in DynamoDB
- **IaC requirement:** one-command deploy (CDK/Terraform), one-command teardown, zero lingering resources
- **API security:** rate limiting, auth on all endpoints, input validation for prompt injection, per-user usage caps
- **Frontend screens (from design thinking):** (1) Home/Dashboard with quick-log button + recent sessions + chat input, (2) Session Logging Form, (3) Chat/Query Interface with message bubbles + citations + suggested follow-ups, (4) Program Analysis input + evaluation output
- **Cross-domain callouts visually distinct** in chat UI: "From powerlifting research: ..." styled differently from personal data references
- **Suggested follow-up questions** after each AI response to guide users who don't know what to ask
- **No social features, no gamification, no virtual rewards** — serious athletes actively reject these

## Technical Context

- **AWS stack:** Lambda (compute), DynamoDB (user data + training logs), S3 (FAISS index + static frontend), API Gateway (routing + rate limiting), Cognito (auth, 50K MAU free), CloudFront (CDN)
- **Vector store:** FAISS file-based — works identically on local filesystem and in S3. No managed vector DB needed
- **LLM:** Claude API with budget cap. Local dev: same API or Ollama fallback
- **LLM cost per query:** ~$0.01-0.03 (embed → FAISS search → DynamoDB fetch → one LLM call). May require multiple calls for complex queries (re-ranking, citation verification) — budget up to $0.05/query worst case
- **Current LLM pricing:** Claude Haiku at $0.25/$1.25 per 1M tokens, Sonnet at $3/$15. Prompt caching 90% off cached input. Batch processing 50% off
- **Knowledge base ingestion:** 13 XLSX powerlifting cycles parsed via openpyxl + one-time LLM into natural language descriptions. 3-5 strength training books chunked and embedded. All stored as single FAISS index file
- **GenAI patterns used:** RAG (FAISS), LLM as coaching/explanation layer, LLM as one-time data ingestion (XLSX → NL), agent with tool use (DynamoDB + FAISS queries)
- **Frontend:** S3 + CloudFront on AWS, local dev server for development. Web-first, mobile-responsive. No native mobile app in v1
- **Local dev stack:** Python (Flask/FastAPI), DynamoDB Local (Docker), FAISS on disk, same Claude API
- **7-day build plan:** Day 1 IaC+scaffolding, Day 2 knowledge ingestion+FAISS, Day 3 RAG pipeline, Day 4 personal data integration, Day 5 dual-source query, Day 6 frontend, Day 7 demo prep
- **3-day fallback:** Drop program analysis. Ship general RAG + structured logging + bare frontend. Still demonstrates core dual-source architecture

## Detailed User Scenarios

- **Primary persona:** 22-40 year old dedicated niche athlete, trains 3-5x/week in grip/armwrestling/powerlifting, 2+ years experience, logs sporadically in spreadsheets, no systematic periodization, discovers tools through Reddit/Discord/GripBoard
- **"Aha moment" scenario:** User logs 5-10 sessions → asks "why am I stalling on grippers?" → receives response citing their recent volume trend AND a periodization principle from the knowledge base → realizes this is fundamentally different from ChatGPT
- **Cross-domain scenario:** Armwrestler asks about peaking for competition → system retrieves powerlifting peaking protocols from knowledge base + user's recent training intensity data → explains how those principles translate to armwrestling-specific prep
- **Program analysis scenario:** User pastes a training program from a forum → system evaluates it against general principles ("volume is high for your recovery capacity based on RPE trends") AND personal patterns ("you responded better to intensity blocks in your last 3 cycles")
- **Psychographic profile:** values mastery over quick results, skeptical of generic advice, respects domain expertise, high conscientiousness, training is central identity, low tolerance for admin overhead
- **Adoption behavior:** tries free → validates sport understanding in first 2-3 sessions → assesses insight quality → commits or abandons permanently within 7-14 days. Generic responses = permanent loss

## Competitive Intelligence

- **JuggernautAI:** $34.99/month, powerlifting only, hundreds of data points per user, auto-regulation, meet prep. Created by Chad Wesley Smith (athlete credibility). No cross-domain, no conversational AI, no free tier
- **ArmProgress:** armwrestling-specific logging, premium analytics dashboards ("AI-powered Intelligent Reports"), growing user base. No conversational AI coaching, no general knowledge RAG, no cross-domain transfer
- **Pelaris:** 5-layer LLM pipeline, MCP integration with Claude/ChatGPT, multi-sport support, coaching rationale per session, privacy-first. No personal data RAG, no niche sport depth, generalist positioning
- **SensAI:** $69.99/year, LLM-powered coaching with persistent memory ("remembers injuries and preferences"), wearable integration (Oura/WHOOP/Garmin). General fitness focus — no niche sport knowledge bases, no dual-source RAG
- **Strong:** 3M+ users, Reddit's #1 recommendation for simple logging. No AI, no coaching, no insights. Default incumbent that users outgrow
- **Ray:** real-time voice coaching, leading AI personal trainer 2026. General fitness, no persistent memory architecture
- **Armwrestling Coaching App (iOS, 2025):** static programs from one coach, no AI, no personalization
- **Key gap confirmed:** no competitor occupies intersection of niche sport depth + dual-source RAG + persistent memory. Closest: SensAI (memory + LLM, no niche), JuggernautAI (sport depth + AI, no cross-domain, no free tier)

## Market Data

- **Global AI fitness market:** $16.86B (2025) → $48.79B (2032), 16.3% CAGR
- **SAM:** 500K-2M niche strength athletes globally
- **SOM:** 50K-200K English-speaking, digitally active, tool-seeking
- **OpenPowerlifting:** ~980K competitive lifters tracked, 700% increase in US meets 2010-2024
- **Armwrestling market:** $150M (2025) → $220M (2032), 8% CAGR
- **Grip sport:** ~1K-5K competitive athletes (smallest, most dedicated)
- **Community channels:** Reddit r/GripTraining ~95K, r/armwrestling ~45K, r/powerlifting ~450K, GripBoard forums, Discord servers
- **Freemium conversion benchmarks:** median 2.18% download-to-paid, top decile 12.1%. Hard paywall apps: 12.11% median. Trial-to-paid: 39.9% median
- **Fitness app 90-day abandonment:** 69%. AI-personalized apps show 50% higher retention
- **Price sensitivity:** $0 for generic tools, $5-15/month for genuinely sport-specific AI coaching, $50-200/month for human coaching

## Pricing & Unit Economics

- **Model:** freemium with metered AI coaching. Free logging always. 3 queries/day free (10/day first week). Premium ~$7-10/month unlimited
- **Break-even:** ~20 paying subscribers covers infrastructure
- **Conservative (500 users, 5% conversion):** ~$210/mo revenue vs ~$170/mo costs = ~$40/mo net
- **Optimistic (1K users, 10% conversion):** ~$850/mo revenue vs ~$500/mo costs = ~$350/mo net
- **Usage-based pricing** (pay-per-query packs) noted as potential alternative to flat subscription — may fit cost-conscious audience better. Decision deferred
- **Cost per action:** logging = $0, AI query = ~$0.01-0.05, knowledge base setup = ~$0.50 one-time

## Open Questions

- **Exact subscription price:** $7 vs $10/month — needs user testing. Lower converts more, higher reaches break-even faster
- **Usage-based vs subscription:** query packs may outperform flat monthly for variable-usage athletes. Subscription fatigue trends support usage-based
- **Cross-domain transfer validation:** "periodization is periodization" is builder hypothesis, not validated user need. Some athletes may distrust advice from other disciplines. Product still delivers value from personal data analysis alone if cross-domain is less compelling than expected
- **Exercise database bootstrapping:** how to populate grip/armwrestling-specific exercises in 7-day build? Manual curation? Community contribution post-launch?
- **AI response quality evaluation:** no test set or rubric defined for measuring whether coaching advice is correct, safe, and useful. Need at minimum: 50 known-good Q&A pairs for pre-launch spot-checking
- **Community engagement strategy:** Reddit/Discord communities are hostile to self-promotion. Authentic sharing of real insights ("I asked about my stall and it told me...") is the approach, but execution details not defined
- **Competition peaking feature:** high-value coaching moment, natural premium feature. Not in v1 scope but strong candidate for v2 — could justify higher willingness-to-pay

## Scope Signals

**In v1:** structured logging form, dual-source RAG query engine, program analysis, cross-domain cited responses, AWS deployment (Lambda/DynamoDB/S3/FAISS/API Gateway/Cognito), basic frontend (log/chat/history pages)

**Out of v1 (confirmed):** proactive pattern detection, community/social features, coach-facing tools/B2B, wearable integration, voice/photo logging, native mobile app, XLSX bulk import

**v2 candidates:** XLSX import, proactive weekly pattern alerts, competition peaking feature, shareable insight cards for social media, deeper exercise database, coach referral layer

**Fallback (Day 3 decision):** drop program analysis, ship general RAG + logging + bare frontend
