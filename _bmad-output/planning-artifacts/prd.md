---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish', 'step-12-complete']
status: complete
completedAt: '2026-04-19'
classification:
  projectType: 'web_app'
  domain: 'sports_fitness_ai'
  complexity: 'medium'
  projectContext: 'greenfield'
inputDocuments:
  - '_bmad-output/planning-artifacts/product-brief-strengthwise.md'
  - '_bmad-output/planning-artifacts/product-brief-strengthwise-distillate.md'
  - '_bmad-output/planning-artifacts/research/market-strengthwise-ai-coaching-research-2026-04-18.md'
  - '_bmad-output/brainstorming/brainstorming-session-2026-04-18-001.md'
  - '_bmad-output/design-thinking-2026-04-18.md'
documentCounts:
  briefs: 2
  research: 1
  brainstorming: 1
  designThinking: 1
  projectDocs: 0
workflowType: 'prd'
---

# Product Requirements Document - StrengthWise

**Author:** Mr.A
**Date:** 2026-04-19

## Executive Summary

StrengthWise is a conversational AI strength coach for niche sport athletes — grip, armwrestling, and powerlifting — that combines a curated general knowledge base of strength science with each athlete's personal training history through dual-source RAG. Athletes in these sports accumulate years of training data across spreadsheets and memory, but have no way to extract insights from it. General LLMs can answer training questions but forget everything between sessions. Sport-specific apps log workouts but offer dashboards, not coaching. StrengthWise bridges both: ask "why did my grip stall in cycle 8?" and get a cited answer that references your cycle 8 data alongside relevant periodization principles from the knowledge base.

The architecture is cost-conscious by design. Structured training logging uses no LLM — it's instant, free, and unlimited. AI coaching fires only on-demand (~$0.01-0.03 per query). This split enables a genuinely sustainable free tier: logging at zero cost, with metered AI queries for premium. The target market — 500K-2M niche strength athletes globally — is small enough that well-funded competitors won't pursue it, but passionate enough that community word-of-mouth drives adoption at near-zero acquisition cost.

### What Makes This Special

Today, getting a quality training answer requires five tools: open a spreadsheet, find the relevant data, open a training book, craft a prompt for ChatGPT, and re-explain your history because it forgot last week's conversation. Nobody actually does this. StrengthWise collapses that entire workflow into a single question.

The core insight: the knowledge to train smarter already exists in two places — your own training history and published strength science. The problem was never access to either; it was bridging them without friction. Dual-source RAG with citations is the mechanism: personal citations reference specific session dates and metrics, knowledge citations reference the source text and principle. No competitor occupies this intersection of niche sport depth, conversational AI coaching, and persistent personal memory. Every logged session compounds the system's understanding, creating switching costs and a data moat that strengthens over time.

## Project Classification

- **Project Type:** Web application — SPA frontend (S3 + CloudFront), serverless backend (Lambda, API Gateway), mobile-responsive
- **Domain:** Sports/Fitness Tech + AI (dual-source RAG, LLM coaching layer)
- **Complexity:** Medium — no regulatory compliance, but high quality bar on sport-specific AI responses, knowledge base curation, and cross-domain transfer credibility
- **Project Context:** Greenfield — 7-day capstone build on AWS (Lambda, DynamoDB, S3/FAISS, API Gateway, Cognito)

## Success Criteria

### User Success

- **First dual-cited response within session 1.** The "aha" moment — a response that references both personal training data AND general strength science — must occur in the user's first interaction. If it doesn't, the user is lost permanently (market research confirms 2-3 interaction decision window).
- **Session logging in under 30 seconds.** The structured form must survive the "sweaty hands, post-session brain fog" mobile test. Logging friction kills consistency; consistency is the data flywheel.
- **Sport-specific recognition on first use.** When a grip athlete types "gripper close" or "hub lift," the system must recognize it immediately. Failure to speak the user's sport language breaks trust instantly.
- **Cross-domain insight credibility.** Users trust recommendations that bridge disciplines (e.g., powerlifting periodization applied to grip training) because they're cited from both sources — not because the system asserts authority.

### Business Success

- **Capstone evaluation:** Working end-to-end demo with seeded data (30+ sessions) demonstrating all core flows — structured logging, dual-source RAG query, program analysis, cross-domain citations. Evaluators see the difference between a general LLM answer and a StrengthWise answer side-by-side.
- **Dogfooding validation:** Mr.A uses StrengthWise daily for logging and weekly for coaching queries for 2+ weeks post-build. If the builder stops using it, the product failed its own test.
- **Infrastructure self-sufficiency (12-month):** Revenue covers AWS + LLM costs. Break-even at ~20 paying subscribers (~$170/month costs).
- **Organic growth (12-month):** 500+ active users through community word-of-mouth only. Zero paid marketing. >80% of signups from community channels (Reddit, GripBoard, Discord).
- **Freemium conversion:** 5-10% free-to-paid, benchmarked against industry median of 2.18%.

### Technical Success

- **AWS cost at capstone:** $0/month (Free Tier sufficient for demo-scale usage).
- **AWS cost at 100 DAU production:** ~$100-300/month estimate — must be covered by monetization model.
- **LLM query cost:** ~$0.01-0.05 per query (embed + FAISS search + DynamoDB fetch + one LLM call). Rate limiting (3/day free, 10/day onboarding week) keeps free-tier costs bounded.
- **One-command deploy, one-command teardown.** IaC (CDK/Terraform) with zero lingering resources.
- **RAG response quality:** 4+/5 user rating on relevance. Every response cites both personal and general sources.
- **XLSX import accuracy:** >90% fields correctly parsed from real-world messy spreadsheets (v2, but the architecture must support it).

### Measurable Outcomes

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Session logging time | < 30 seconds | Stopwatch during user testing |
| First dual-cited response | Within session 1 | Onboarding flow tracking |
| Query response relevance | 4+/5 | Post-query thumbs up/down + periodic rating |
| Cross-domain citation credibility | 3.5+/5 | Post-query rating |
| 90-day retention | > 50% (vs 31% industry avg) | Active session logging in rolling 7-day window |
| Capstone demo completion | All core flows working by Day 6 | Day 6 checkpoint |
| Personal daily use post-build | 2+ weeks continuous | Self-tracking |

## User Journeys

### Journey 1: Marcus — First Session to "Aha" Moment

**Persona:** Marcus, 28, grip sport athlete for 3 years. Trains 4x/week — grippers, hub lifts, pinch blocks, plus deadlift variations for general strength. Has 8 months of training data in a Google Sheet he barely looks at. Found StrengthWise through a Reddit thread on r/GripTraining where someone posted a screenshot of a cited coaching response.

**Opening Scene:** Marcus downloads the app on a Tuesday evening after training. He's frustrated — his gripper close has been stuck at the same level for 6 weeks despite training it 3x/week. He's tried asking ChatGPT but got generic advice about "progressive overload" with no reference to his actual training. He opens StrengthWise skeptically — another fitness app that probably doesn't know what a hub lift is.

**Rising Action:** He creates an account (Cognito, 30 seconds). The sport selector shows "Grip Sport" as a first-class option — first surprise. He taps into the logging form: date auto-fills, he selects grip sport, and the exercise dropdown includes gripper close, hub lift, pinch block, wrist curl, and more. He logs today's session — 4 exercises, 3-4 sets each — in about 25 seconds. The form feels like it was built by someone who trains grip. He logs two more sessions from memory over the next few days.

**Climax:** On day 3, with three sessions logged, he opens the chat and types: "Why is my gripper close stuck? I've been training it 3x/week for 6 weeks." StrengthWise responds: *"Looking at your last 3 logged sessions, your gripper volume is high (12+ working sets/week) but your intensity hasn't progressed. From the general knowledge base: Prilepin's chart suggests that for near-maximal grip efforts, 4-10 total reps per session is optimal — you're averaging 18. Your high-rep sets may be building endurance without driving maximal strength adaptation. Consider dropping to 4-6 heavy singles and doubles per session. [Source: Prilepin's Chart, Periodization principles] [Personal data: Sessions Apr 15-17, gripper close sets]"* Marcus reads it twice. This isn't generic advice. It cited his actual sessions and connected them to a real principle he's heard of but never applied to grip work.

**Resolution:** Marcus adjusts his next session based on the recommendation. He logs it. He asks a follow-up: "Should I keep hub lifts at the same volume?" The system references his hub lift data and a different principle. He's hooked — not because the app is flashy, but because it answered like a coach who actually understood grip sport and remembered what he did last Tuesday. He logs every session for the next two weeks without missing one.

### Journey 2: Marcus — Stall Diagnosis After 3 Months

**Opening Scene:** Three months in, Marcus has 60+ sessions logged. His gripper close improved after the initial advice, but now his pinch block has stalled. He's also noticed his deadlift is regressing slightly. He's not sure if the two are related.

**Rising Action:** He types: "My pinch has been flat for 3 weeks and my deadlift is going down. What's happening?" StrengthWise retrieves his full training history and cross-references against the knowledge base.

**Climax:** The response surfaces a pattern Marcus couldn't see himself: *"Your total weekly volume across all exercises increased 35% over the last 4 weeks — you added wrist curls and fat bar holds while keeping everything else the same. Your RPE ratings have trended from 7-8 to 9-10 across all movements, and your free-text notes mention 'felt tired' three times in the last two weeks. From the knowledge base: accumulated fatigue from excessive volume typically manifests as stagnation in technical lifts (pinch) and regression in compound movements (deadlift) before it appears in simpler exercises. This pattern matches a classic overreaching signature. [Source: Periodization Theory and Methodology, Bompa & Buzzichelli] [Personal data: 14 sessions, Mar 20 — Apr 19, volume trend analysis]"* The system then suggests a deload protocol adapted from powerlifting taper research, applied to his grip-specific context.

**Resolution:** Marcus realizes the system caught something he would have missed for another 2-3 weeks — and it connected a powerlifting concept (overreaching/deload) to his grip training context. The 60 sessions of accumulated data made this possible. He shares the insight screenshot in his grip sport Discord. Two friends sign up that week.

### Journey 3: Elena — Cross-Domain Discovery

**Persona:** Elena, 34, competes in armwrestling (2 years) and recently started powerlifting to build general pulling strength. She trains armwrestling 3x/week (table practice, pronation, supination, side pressure drills) and powerlifts 2x/week. She's strong but programs both sports independently with no systematic connection between them.

**Opening Scene:** Elena's armwrestling coach told her to "peak for the regional tournament in 8 weeks" but gave no specific protocol. She knows powerlifting has well-documented peaking strategies but has no idea how to translate them to armwrestling-specific movements. She heard about StrengthWise from an armwrestling Discord server.

**Rising Action:** Elena creates an account and logs her last week of training — 3 armwrestling sessions and 2 powerlifting sessions. The sport selector lets her tag each session appropriately. She types her exercises: pronation, supination, side pressure, hook practice, and the system recognizes all of them. She adds her powerlifting exercises (bench, squat, deadlift) under general strength. After logging a week's worth of data, she asks: "I need to peak for an armwrestling tournament in 8 weeks. How should I structure my training?"

**Climax:** StrengthWise delivers a cross-domain response: *"From the general knowledge base: a standard powerlifting peaking protocol involves 3-4 weeks of accumulated volume followed by a 2-3 week taper, dropping volume 40-60% while maintaining or slightly increasing intensity. This principle transfers to armwrestling preparation. Looking at your logged sessions: your pronation and side pressure volumes are currently moderate (6-8 working sets each), and your RPE is consistently 7-8 — you have room to push volume higher for 3 weeks before beginning a taper. Suggested 8-week structure: Weeks 1-3: increase armwrestling-specific volume by 20-30%, maintain powerlifting as general strength support. Weeks 4-5: hold peak volume, begin reducing powerlifting volume. Weeks 6-7: taper armwrestling volume by 40%, drop powerlifting to maintenance only. Week 8: competition week, minimal volume, technique sharpening only. [Source: Peaking protocols, Periodization for Strength Sports] [Personal data: 5 sessions, current volume and intensity baselines]"*

**Resolution:** Elena has never seen powerlifting peaking science applied to her armwrestling prep in a single cited response. Her coach gave her "peak for 8 weeks" — StrengthWise gave her a week-by-week plan grounded in both her actual training data and established periodization science. She follows the plan, logs every session, and after the tournament asks: "How did my actual taper compare to the plan?" — getting a retrospective analysis that informs her next competition prep.

### Journey 4: Mr.A — Builder/Admin Operations

**Persona:** Mr.A, builder and sole operator. ML engineer, PhD student, grip sport and armwrestling athlete. Runs StrengthWise on AWS, manages the knowledge base, monitors costs, and is the primary dogfooding user.

**Opening Scene:** It's two weeks post-launch. 15 users have signed up through Reddit and Discord posts. Mr.A checks the AWS console on Sunday evening to review the week.

**Rising Action:** He checks CloudWatch metrics: Lambda invocations (logging endpoints vs. query endpoints), DynamoDB read/write capacity consumption, API Gateway request counts. He reviews the LLM cost tracker — a simple DynamoDB counter that increments per AI query. This week: 180 logging events (free), 45 AI queries (~$1.35 in LLM costs). All within Free Tier for AWS services. He scans the Cognito user pool: 15 registered users, 8 active in the last 7 days.

**Climax:** He notices one user has been hitting the rate limit daily (3 queries/day) for 5 straight days — a power user. He also spots that several queries about "strongman" exercises are returning weak results from the knowledge base — the corpus doesn't cover strongman implements well. He pulls the query logs from DynamoDB to see what users are actually asking. Three users asked about atlas stones and log press — exercises not in the knowledge base.

**Resolution:** Mr.A adds a strongman section to the general knowledge corpus: chunks from a strongman training guide, embeds them, rebuilds the FAISS index, and uploads the new index to S3. The next Lambda cold start picks up the updated index. He also notes the power user as a candidate for early premium — someone who'd clearly pay for unlimited queries. He updates a simple tracking spreadsheet with this week's metrics: users, queries, costs, and knowledge gaps identified. Total time spent on admin: 30 minutes on a Sunday evening.

### Journey Requirements Summary

| Journey | Key Capabilities Revealed |
|---------|--------------------------|
| **Marcus — First Session** | Sport-specific exercise database, <30s logging form, dual-source RAG with citations, onboarding that demonstrates value within 3 sessions |
| **Marcus — 3 Months** | Long-term data trend analysis, cross-session pattern detection, free-text note analysis ("felt tired"), volume/RPE trend calculations, shareable insights |
| **Elena — Cross-Domain** | Multi-sport session tagging, cross-domain knowledge retrieval, structured multi-week plan generation from periodization principles + personal baselines, retrospective analysis |
| **Mr.A — Admin/Ops** | CloudWatch monitoring, DynamoDB query logging, LLM cost tracking, FAISS index rebuild and S3 upload pipeline, rate limit visibility, user activity metrics |

## Domain-Specific Requirements

### Safety & Liability

- **Not medical advice.** Every AI response includes explicit disclaimer: StrengthWise provides training insights, not medical or injury treatment advice. Users with injuries or medical conditions should consult healthcare professionals.
- **Citation-backed responses only.** The dual-source RAG architecture inherently mitigates bad advice by requiring cited sources. Users can verify the reasoning behind any recommendation.
- **User feedback mechanism.** Thumbs up/down on AI responses to flag bad advice. Flagged responses logged for quality review.

### Data Privacy & Ownership

- **User data ownership.** Athletes own their training data. Full CSV export available to all users (free and paid). Account deletion fully supported with complete data removal.
- **Encryption at rest.** All training data encrypted in DynamoDB (AWS default encryption).
- **No data sharing.** Training data is never shared with third parties, used for advertising, or aggregated without explicit consent.
- **GDPR readiness.** Data export and deletion capabilities satisfy core GDPR data subject rights for potential European expansion.

### Knowledge Base Quality

- **Corpus curation is the quality bottleneck.** RAG response quality is directly proportional to knowledge base quality. Garbage in = garbage out. The 13 XLSX training cycles and 3-5 strength training books must be parsed, chunked, and embedded with high fidelity.
- **Copyright risk mitigation.** Use freely available training principles and public-domain content where possible. Chunked excerpts for educational use. Replace with original content over time.
- **Sport-specific exercise database.** Pre-populated for grip (gripper close, hub lift, pinch block, wrist curl, fat bar), armwrestling (pronation, supination, side pressure, hook, cupping, table practice), and powerlifting (squat, bench, deadlift, accessories). Missing exercises break trust instantly.

### AI Response Integrity

- **RAG hallucination mitigation.** Cross-reference citations in every response. If the retrieval doesn't surface relevant personal data or general knowledge, the system should acknowledge gaps rather than fabricate answers.
- **Confidence signaling.** Responses based on limited data (e.g., <5 sessions) should indicate lower confidence. "Based on your 3 logged sessions, early indicators suggest..." vs. "Based on 60 sessions, a clear pattern shows..."
- **Prompt injection prevention.** Input validation on all user-facing text fields (chat input, notes field, program analysis input). Sanitize before passing to LLM.

### Technical Constraints

- **Rate limiting is a safety and cost mechanism.** 3 queries/day free (10/day onboarding week) bounds both LLM costs and potential abuse. Premium users get unlimited but are still subject to per-minute rate limits to prevent automated scraping.
- **Cold start latency.** Lambda cold starts + FAISS index loading from S3 may add 3-5 seconds to first query. Acceptable for async coaching (not real-time), but should be monitored.

## Innovation & Novel Patterns

### Detected Innovation Areas

**1. Dual-Source RAG Architecture for Personalized Coaching**
No existing fitness tool combines personal training history retrieval (DynamoDB) with general domain knowledge retrieval (FAISS) in a single query pipeline that cites both sources. This is a novel application of RAG — most RAG implementations query a single corpus. StrengthWise's two-corpus approach (personal + general) with merged citation in the response is architecturally distinct.

**2. Cross-Domain Knowledge Transfer via LLM**
Using the LLM as a translation layer between strength disciplines — applying powerlifting periodization principles to grip sport programming, or peaking protocols to armwrestling — is a novel capability. No competing tool, human or AI, currently spans grip, armwrestling, strongman, and powerlifting in a single cited response. The LLM doesn't just retrieve; it bridges.

**3. Cost-Conscious Split Architecture**
The structural separation of free operations (structured logging = no LLM) from expensive operations (coaching queries = LLM) is a deliberate architectural innovation for sustainability. Most AI fitness apps run LLM on every interaction. StrengthWise's event-driven model makes a genuinely free tier possible at any scale — the free tier costs literally $0 per user because no LLM is invoked during logging.

### Market Context & Competitive Landscape

Market research confirms the gap: after analyzing 12+ competitors across 4 tiers, no existing tool occupies the intersection of niche sport depth + dual-source RAG + persistent memory. Closest competitors cover at most two of these three axes (JuggernautAI: sport depth + data-driven programs, no RAG; ArmProgress: sport depth + logging, no AI coaching; Pelaris: LLM pipeline + multi-sport, no personal data RAG). The combination is uncontested.

### Validation Approach

- **Ablation study (capstone evaluation):** Compare response quality across four conditions: dual-source RAG (personal + general) vs. personal-only vs. general-only vs. vanilla LLM. Measures the marginal value of each source.
- **Cross-domain transfer accuracy:** Manually evaluate whether powerlifting principles correctly apply to grip sport queries. Small test set of 50 known-good Q&A pairs.
- **Side-by-side demo:** Same question asked to ChatGPT and StrengthWise — demonstrates the persistent memory and dual-citation advantage live.

### Risk Mitigation

| Innovation Risk | Mitigation |
|----------------|------------|
| Dual-source RAG adds retrieval complexity and latency | FAISS search is sub-second; DynamoDB queries are single-digit ms. Combined overhead is acceptable for async coaching |
| Cross-domain transfer may feel forced or inaccurate | Every cross-domain claim is cited — users can verify. System should acknowledge when transfer confidence is low |
| Cost-conscious architecture may limit response quality | Single LLM call with rich context (FAISS results + DynamoDB results) is sufficient. Multi-turn refinement deferred to v2 |
| Novel architecture = no established patterns to follow | Standard components (FAISS, DynamoDB, Lambda, Claude API) in a novel combination. Each piece is well-documented individually |

## Web App Specific Requirements

### Project-Type Overview

StrengthWise is a single-page application (SPA) with a serverless backend. The frontend is static files served from S3 via CloudFront. The backend is API Gateway + Lambda functions. There is no server-side rendering, no SEO requirement (athletes discover through community channels, not Google), and no real-time requirement (coaching is async, not live chat). The critical UX constraint is mobile-responsiveness — athletes log training on their phones post-session.

### Technical Architecture Considerations

**SPA Architecture:**
- Static frontend (HTML/CSS/JS) deployed to S3, served via CloudFront CDN
- All dynamic behavior via REST API calls to API Gateway → Lambda
- Client-side routing for page navigation (home, log, chat, history)
- No SSR/SSG needed — content is user-specific and behind auth

**Browser Support:**
- Modern evergreen browsers: Chrome, Safari, Firefox, Edge (latest 2 versions)
- Mobile Safari and Chrome are the primary targets (athletes log on phones)
- No IE11 support required
- Progressive Web App (PWA) capabilities deferred to post-MVP — not needed for core flows

**Responsive Design:**
- Mobile-first design — the logging form must be fully functional on a 375px-wide screen
- Touch targets minimum 44x44px for all interactive elements (logging form buttons, exercise dropdowns)
- The "sweaty hands" test: form elements must be large enough and spaced enough for post-session input
- Desktop layout is secondary but should use available space for chat history and training data side-by-side

**Performance Targets:** See Non-Functional Requirements (NFR1-NFR6) for specific, measurable performance criteria.

**SEO Strategy:**
- Not applicable. StrengthWise is behind authentication. Users discover through Reddit, GripBoard, Discord — not search engines. A simple landing page (outside the app) may be needed for community sharing links, but MVP can use a README or static page.

**Accessibility:**
- WCAG 2.1 Level A minimum for MVP. Core flows (logging, chat) must be keyboard-navigable and screen-reader compatible.
- Color contrast ratios must meet AA standard — athletes may use the app in varied lighting (gym, outdoor).
- Form labels and ARIA attributes on all interactive elements.

### API Architecture

**Endpoints (REST via API Gateway):**

| Method | Path | Purpose | Auth | LLM Cost |
|--------|------|---------|------|----------|
| POST | /sessions | Log a training session | Cognito JWT | $0 |
| GET | /sessions | Retrieve session history | Cognito JWT | $0 |
| GET | /sessions/{id} | Retrieve single session | Cognito JWT | $0 |
| POST | /query | Ask a coaching question (dual-source RAG) | Cognito JWT | ~$0.01-0.05 |
| POST | /analyze | Submit program for analysis | Cognito JWT | ~$0.01-0.05 |
| GET | /exercises | List available exercises by sport | Cognito JWT | $0 |
| GET | /profile | Get user profile and usage stats | Cognito JWT | $0 |
| POST | /export | Export training data as CSV | Cognito JWT | $0 |
| DELETE | /account | Delete account and all data | Cognito JWT | $0 |

**Authentication:** AWS Cognito with JWT tokens. User pools for sign-up/sign-in. 50K MAU free tier. Email-based registration (no social login for MVP — keeps scope tight).

**Rate Limiting:** API Gateway usage plans. Free tier: 3 requests/day on /query and /analyze (10/day during first 7 days). Premium: unlimited (subject to per-minute burst limits).

**Input Validation:** All request bodies validated server-side in Lambda. Chat input and notes fields sanitized before LLM context injection. Maximum input length enforced (2000 chars for queries, 500 chars for notes).

### Implementation Considerations

- **Frontend framework:** Lightweight — React, Preact, or vanilla JS with a small router. No heavy framework needed for 4 screens. Bundle size matters for mobile performance.
- **Local development:** Flask/FastAPI serving the API locally. DynamoDB Local (Docker) for data. FAISS on local filesystem. Same Claude API for LLM calls. Frontend served by local dev server (Vite or similar).
- **Deployment pipeline:** `cdk deploy` (or `terraform apply`) for full stack. `cdk destroy` for complete teardown. No manual AWS console steps in the deploy path.
- **Environment parity:** FAISS index file works identically on local disk and in S3. DynamoDB Local mirrors DynamoDB behavior. The only external dependency that differs is CloudFront (not needed locally).

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Problem-solving MVP — demonstrate that dual-source RAG coaching delivers genuinely better answers than the status quo (ChatGPT + spreadsheets + books). The MVP isn't about polish or feature breadth; it's about proving one thing works: cited, sport-specific coaching that remembers your history.

**Resource Requirements:** Solo developer (Mr.A), 7 days. Python backend, lightweight frontend, AWS serverless. No design team, no QA team, no DevOps — IaC handles deployment, dogfooding handles QA.

**MVP Philosophy:** Ship the smallest thing that produces the "aha" moment — a dual-cited response that references both personal training data and general strength science. Everything else is in service of that moment.

### MVP Feature Set (Phase 1 — 7-Day Build)

**Core User Journeys Supported:**
- Journey 1 (Marcus — First Session): Full support. Logging + first dual-cited query.
- Journey 3 (Elena — Cross-Domain): Partial support. Multi-sport tagging and cross-domain queries work, but no structured multi-week plan generation.
- Journey 4 (Mr.A — Admin): Via AWS console and CloudWatch directly. No admin UI.

**Must-Have Capabilities:**

| Capability | Rationale | Day |
|-----------|-----------|-----|
| IaC scaffold (CDK/Terraform) | One-command deploy/teardown, zero lingering resources | 1 |
| DynamoDB schema + Lambda scaffolding | Foundation for all data operations | 1 |
| Knowledge base ingestion (13 XLSX + books → FAISS) | The coaching brain — without this, responses are generic | 2 |
| Structured logging form | The data flywheel starts here. Must be <30s | 2-3 |
| Dual-source RAG pipeline (FAISS + DynamoDB → LLM) | The core innovation. This IS the product | 3-5 |
| Chat interface with cited responses | Where users experience the value | 4-5 |
| Program analysis | High-value interaction, differentiator | 4-5 |
| Cognito auth + rate limiting | Security and cost control | 1-2 |
| Sport-specific exercise database | Trust builder — system must recognize "gripper close" | 2 |
| Basic frontend (home, log, chat, history) | Minimum viable UI for all core flows | 6 |
| Demo seeding (30+ sessions) | Capstone evaluation requires rich demo data | 7 |

**3-Day Fallback (Day 3 Decision):**
If behind schedule, drop program analysis. Ship general RAG + structured logging + bare frontend. The core dual-source architecture is still demonstrated. This fallback still supports Journey 1 (Marcus) end-to-end.

### Post-MVP Features

**Phase 2 — Growth (Months 1-6 post-launch):**

| Feature | Value | Dependency |
|---------|-------|------------|
| XLSX bulk import | Rescue spreadsheet graveyards, cold-start advantage | Robust parsing of messy real-world data |
| Proactive pattern detection | "Your volume dropped 20%" — surfaces insights without asking | Requires 30+ sessions per user for meaningful patterns |
| Competition peaking analysis | High-value premium feature, natural upsell | Knowledge base needs peaking protocols |
| Suggested follow-up questions | Guides users who don't know what to ask | Low effort, high onboarding impact |
| Thumbs up/down on responses | Quality feedback loop for knowledge base improvement | Simple DynamoDB flag per response |
| Premium tier (Stripe integration) | Revenue generation for sustainability | Payment processing, usage tracking |

**Phase 3 — Expansion (Year 2+):**

| Feature | Value | Dependency |
|---------|-------|------------|
| Adjacent sport expansion (strongman, Olympic WL, Highland games) | Larger addressable market | Knowledge corpus updates per sport |
| Coach-as-a-Service API (B2B) | Multi-athlete management for coaches | Validated individual product first |
| Shareable insight cards | Social media growth engine | Interesting insights worth sharing |
| Geographic expansion (European communities) | Larger market, localization | Multi-language knowledge base |
| Usage-based pricing (query packs) | Alternative to subscription for variable-usage athletes | Billing infrastructure |

### Risk Mitigation Strategy

**Technical Risks:**

| Risk | Severity | Probability | Mitigation | Fallback |
|------|----------|-------------|------------|----------|
| RAG hallucination / bad advice | High | Medium | Citation-backed responses, confidence signaling, user feedback | Explicit disclaimers, flag mechanism |
| FAISS index too large for Lambda memory | Medium | Low | Current corpus (13 cycles + 3-5 books) is small. Only a problem at scale | Move to Lambda with larger memory or EFS mount |
| Knowledge base quality insufficient | High | Medium | Corpus quality = response quality. Invest Day 2 heavily in chunking/embedding | General-only RAG still works if personal data parsing fails |
| 7-day build scope overrun | High | Medium | 3-day fallback explicitly defined. Daily checkpoint against build plan | Drop program analysis, ship core RAG + logging |

**Market Risks:**

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| Athletes prefer spreadsheets / no tool | Medium | Low | Don't replace spreadsheets — make them queryable. XLSX import (v2) meets users where they are |
| Cross-domain transfer feels generic | Medium | Medium | Citation mechanism lets users verify. Acknowledge low-confidence bridges |
| Community backlash (seen as marketing) | High | Low | Authentic use by a real athlete. Share real insights, not features |
| ArmProgress adds LLM features | Medium | Medium | First-mover in cross-domain transfer. Ship fast, build data moat |

**Resource Risks:**

| Risk | Mitigation |
|------|------------|
| Solo developer — no redundancy | Open architecture on standard AWS services. No proprietary infrastructure. User data exportable |
| Time constraint (7 days) | Daily build checkpoints. Day 3 fallback decision. Prioritize core RAG pipeline over UI polish |
| LLM costs grow with users | Rate limiting bounds free-tier costs. Premium revenue covers paid users. LLM costs dropping ~10x/year |

## Functional Requirements

### Training Session Logging

- **FR1:** Athletes can log a training session with date, sport/discipline, exercises, sets, reps, weight, RPE, and free-text notes
- **FR2:** Athletes can select their sport/discipline from a predefined list (grip sport, armwrestling, powerlifting, general strength)
- **FR3:** Athletes can select exercises from a sport-specific pre-populated database when logging
- **FR4:** Athletes can add free-text notes to any session (e.g., "felt weak", "elbow pain", "new PR")
- **FR5:** Athletes can add multiple exercises with multiple sets per exercise in a single session log
- **FR6:** Athletes can view their training session history in reverse chronological order
- **FR7:** Athletes can view details of any individual past session

### AI Coaching (Dual-Source RAG)

- **FR8:** Athletes can ask natural language questions about their training and receive cited responses
- **FR9:** The system retrieves relevant information from both the athlete's personal training history and the general strength knowledge base for each query
- **FR10:** AI responses cite personal data sources (specific session dates and metrics) and general knowledge sources (principle name and source text)
- **FR11:** The system distinguishes between personal data citations and general knowledge citations in response formatting
- **FR12:** Athletes can submit a training program (pasted text) and receive an evaluation against general principles and their personal training patterns
- **FR13:** The system provides confidence-appropriate responses based on available data volume (few sessions vs. many sessions)
- **FR14:** The system acknowledges gaps when retrieval doesn't surface relevant information rather than fabricating answers

### Rate Limiting & Usage Tiers

- **FR15:** Free-tier athletes can make up to 3 AI coaching queries per day
- **FR16:** Athletes in their first 7 days receive 10 AI coaching queries per day
- **FR17:** Premium athletes can make unlimited AI coaching queries (subject to per-minute burst limits)
- **FR18:** Athletes can see their remaining daily query count

### User Account Management

- **FR19:** Athletes can create an account with email-based registration
- **FR20:** Athletes can sign in and sign out securely
- **FR21:** Athletes can export all their training data as CSV
- **FR22:** Athletes can delete their account and all associated data
- **FR23:** Athletes can view their profile and usage statistics (sessions logged, queries made)

### Knowledge Base & Exercise Database

- **FR24:** The system maintains a curated general knowledge base of strength training science (periodization, progressive overload, sport-specific programming)
- **FR25:** The system maintains a pre-populated exercise database covering grip sport (gripper close, hub lift, pinch block, wrist curl, fat bar), armwrestling (pronation, supination, side pressure, hook, cupping, table practice), and powerlifting (squat, bench, deadlift, accessories)
- **FR26:** The system supports cross-domain knowledge transfer — applying principles from one strength discipline to questions about another

### Safety & Feedback

- **FR27:** AI responses include a disclaimer that the system provides training insights, not medical advice
- **FR28:** Athletes can provide thumbs up/down feedback on AI responses
- **FR29:** The system validates and sanitizes all user input before processing (chat queries, notes, program analysis text)

### Infrastructure & Operations

- **FR30:** The system can be deployed with a single IaC command and torn down with a single command, leaving zero lingering resources
- **FR31:** The operator can monitor system usage (logging events, AI queries, active users, LLM costs) via AWS CloudWatch
- **FR32:** The operator can update the general knowledge base (rebuild FAISS index) without system downtime
- **FR33:** The system enforces per-user rate limits on AI query endpoints

## Non-Functional Requirements

### Performance

- **NFR1:** Training session logging (form submission to confirmation) completes in under 500ms
- **NFR2:** AI coaching query responses return within 10 seconds (FAISS search + DynamoDB fetch + LLM call)
- **NFR3:** Session history page loads within 2 seconds for users with up to 500 logged sessions
- **NFR4:** Initial page load (cached, via CloudFront) completes within 2 seconds
- **NFR5:** Time to interactive for the SPA is under 3 seconds on a 4G mobile connection
- **NFR6:** The logging form end-to-end experience (open form → fill → submit → confirm) takes under 30 seconds for a typical 4-exercise session

### Security

- **NFR7:** All API endpoints require authenticated Cognito JWT tokens — no unauthenticated access to user data or AI queries
- **NFR8:** Training data is encrypted at rest in DynamoDB (AWS default encryption)
- **NFR9:** All data in transit uses HTTPS/TLS (API Gateway and CloudFront enforce this by default)
- **NFR10:** User input (chat queries, notes, program text) is validated and sanitized before inclusion in LLM prompts to prevent prompt injection
- **NFR11:** Maximum input length enforced on all text fields (2000 chars for queries, 500 chars for notes) to prevent abuse
- **NFR12:** Per-user rate limits are enforced server-side and cannot be bypassed by client manipulation
- **NFR13:** Account deletion removes all user data from DynamoDB within 24 hours, with no residual data in backups beyond standard DynamoDB retention

### Scalability

- **NFR14:** The system supports up to 100 concurrent users without performance degradation (Lambda auto-scaling, DynamoDB on-demand capacity)
- **NFR15:** LLM costs remain bounded at scale through rate limiting: worst-case free-tier cost is calculable as (active users × 3 queries/day × $0.05/query)
- **NFR16:** The FAISS index file remains small enough to load within Lambda's memory constraints (128MB-512MB) for the MVP knowledge corpus
- **NFR17:** DynamoDB table design supports efficient queries by user ID and date range without full table scans

### Accessibility

- **NFR18:** Core flows (logging, chat, history) are keyboard-navigable
- **NFR19:** All form inputs have associated labels and ARIA attributes for screen reader compatibility
- **NFR20:** Color contrast ratios meet WCAG 2.1 AA standard (4.5:1 for normal text, 3:1 for large text)
- **NFR21:** Touch targets are minimum 44x44px on mobile for all interactive elements

### Integration

- **NFR22:** The system gracefully handles Claude API outages or rate limits — AI query failures return a user-friendly error message, not a system crash. Logging (which doesn't use the API) continues to function
- **NFR23:** The FAISS index can be rebuilt and redeployed to S3 without downtime — Lambda picks up the updated index on next cold start
- **NFR24:** CSV data export produces a standards-compliant file that opens correctly in Excel, Google Sheets, and other common spreadsheet tools

### Reliability

- **NFR25:** Training session data has zero tolerance for data loss — DynamoDB provides 99.999% durability by default
- **NFR26:** The system remains functional for logging even if the LLM provider is unavailable — the logging path has no LLM dependency
- **NFR27:** IaC deployment is idempotent — running deploy multiple times produces the same result without errors or resource duplication
