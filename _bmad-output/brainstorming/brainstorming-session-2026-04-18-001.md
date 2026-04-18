---
stepsCompleted: [1, 2, 3]
inputDocuments: []
session_topic: 'GenAI capstone product ideation — real product solving personal frustrations with sports training and PhD research'
session_goals: 'One winning MVP idea buildable in 7 days with zero-cost AWS, advanced GenAI patterns, persistent user data'
selected_approach: 'ai-recommended'
techniques_used: ['question-storming', 'morphological-analysis', 'resource-constraints']
ideas_generated: ['Sports #1: Training Memory', 'Sports #2: Adaptive Coach', 'Sports #3: Niche Sport Knowledge Base', 'Sports #4: Personal Coach with General Knowledge', 'Sports #5: Training Pattern Detective', 'Sports #6: Program Translator', 'Sports #4+5 revised: StrengthWise', 'Research #1: Research Idea Feasibility Filter', 'Research #2: Journal Quartile Matcher', 'Research #3: PhD Progress Tracker', 'Hybrid #1: StrengthWise + Research Paper', 'Wild #1: Coach-as-a-Service API']
technique_execution_complete: true
selected_idea: 'StrengthWise — Cross-Domain Strength Coach with Memory'
---

# Brainstorming Session Results

**Facilitator:** Mr.A
**Date:** 2026-04-18

## Session Overview

**Topic:** GenAI capstone product ideation — a real product that solves personal frustrations using advanced GenAI patterns
**Goals:** One winning MVP idea that is buildable in 7 days, uses zero-cost AWS infrastructure, stores user data, and demonstrates advanced GenAI capabilities

### Session Setup

**User Profile:** ML engineer, PhD student, sportsman (grip sport, armwrestling, running)
**Domains:** Sports, healthcare, recommender systems
**Key Frustrations:**
1. Loses track of training progress
2. Trains without systematic approach
3. Struggles with new PhD paper ideas
4. Don't know which journal tier fits papers

**Constraints:** 7-day build, $0 AWS steady state, Claude Code $20 plan, must store user data, must use advanced GenAI pattern (RAG/agents/tool use)

## Technique Selection

**Approach:** AI-Recommended Techniques

- **Question Storming:** Define the right problem space
- **Morphological Analysis:** Systematically map parameter combinations
- **Resource Constraints:** Stress-test against build constraints

## Technique Execution Results

### Phase 1: Question Storming

**Key questions surfaced:**
- "Can I simply track in Google Sheets?" → Revealed the real gap isn't logging, it's *insight extraction*
- "Where do I get domain-specific data for niche strength sports?" → Led to discovering the 13 .xlsx powerlifting training cycles as a goldmine
- "How to validate if a plan is good or bad?" → Shifted focus from plan generation to pattern detection
- "Is RAG + LLM better than books + sheets + ChatGPT prompt?" → Forced articulation of the real moat (persistent memory, accumulated analysis, zero-friction)
- "How complex is AWS Free Tier + MLOps?" → Killed MLOps scope, simplified to Lambda + DynamoDB + FAISS
- "Processing every user input with LLM is expensive" → Led to structured logging (no LLM) vs. on-demand queries (LLM) split

**Critical insight:** The winning idea needs an LLM handling the *messy human interface* (explaining results, bridging domains) while simple analytical logic does the actual *work*.

### Phase 2: Morphological Analysis

**Parameter Grid:**
- **Problem Space:** Training insight extraction, adaptive plans, research idea matching, journal targeting
- **GenAI Patterns:** RAG, LLM as ingestion, LLM as explanation, multi-step agent, LLM classification
- **Data Sources:** User logs, PDF/doc uploads, external APIs, structured forms, free text, curated external knowledge
- **Users:** Solo athlete, niche sport community, PhD students, small coaches

**Ideas Generated (12):**
1. Sports #1: Training Memory — conversational query over personal training history
2. Sports #2: Adaptive Coach — weekly agent-driven plan adaptation
3. Sports #3: Niche Sport Knowledge Base — community-level dataset building
4. Sports #4: Personal Coach with General Knowledge — dual-corpus RAG (general + personal)
5. Sports #5: Training Pattern Detective — proactive pattern detection
6. Sports #6: Program Translator — parse existing programs, map against principles
7. **Sports #4+5 revised: StrengthWise** — merged, cross-domain strength coach with memory ★ SELECTED
8. Research #1: Research Idea Feasibility Filter
9. Research #2: Journal Quartile Matcher
10. Research #3: PhD Progress Tracker
11. Hybrid #1: StrengthWise + Research Paper (dual-purpose)
12. Wild #1: Coach-as-a-Service API (B2B angle)

**Key evolution:** Sports #4 (dual-corpus RAG) + Sports #5 (proactive detection) merged, then broadened from grip-only to all strength sports via cross-domain knowledge transfer.

### Phase 3: Resource Constraints

**7-day build plan validated.** Key de-risk decisions:
- FAISS (file-based) eliminates vector store infrastructure — works identically local and AWS
- Structured form logging (no LLM) eliminates cost-per-log problem
- LLM calls only on user questions (rate-limited, ~$0.01-0.03 each)
- 3-day fallback: general RAG only + logging + bare frontend — still viable demo
- No MLOps, no model training, no fine-tuning

**Cost architecture stress-tested:** Demo day ~$0.50, solo use ~$3-5/month, 10 users ~$15-30/month.

## Selected Idea

### StrengthWise — Cross-Domain Strength Coach with Memory

**Why this won:**
- Solves a real personal frustration (training without systematic approach)
- Has real data available (13 .xlsx powerlifting training cycles + strength training books)
- No competition in niche strength sports
- Cross-domain knowledge transfer is genuinely impressive GenAI capability
- Cost-conscious architecture (structured logging = $0, LLM only for questions)
- FAISS works identically local and AWS — no infra surprises
- 3-day fallback version is still a viable demo
- Potential dual-use as research paper topic

---

## StrengthWise — Pitch

### One-liner

General strength science, applied to YOUR sport, adapted to YOUR history.

### The Problem

Athletes in niche strength sports (grip, armwrestling, strongman) train without systematic, personalized guidance. General strength training science exists in books and spreadsheets, but no tool connects that knowledge to an individual athlete's history and response patterns.

### Why Not Just Use ChatGPT?

Anyone can ask ChatGPT a training question. But ChatGPT doesn't know that you stalled on deadlifts in March, that your grip fails before your back does, that you respond better to high-frequency low-volume blocks, and that last time you peaked for a competition you started too heavy. StrengthWise does — because it was there for all of it.

#### The Moat: Three Things ChatGPT Cannot Do

| Capability | ChatGPT | StrengthWise |
|---|---|---|
| **Persistent memory** | Forgets every session (or has unreliable memory) | DynamoDB stores every log, every response, every pattern — forever |
| **Accumulated analysis** | Can only analyze what you paste right now | Runs trend detection across months: "your grip endurance drops every 4th week" |
| **Zero-friction logging** | You must structure your own prompt every time | Structured form entry — fast, zero-cost, no LLM needed |

#### What "books + sheets + ChatGPT" Actually Looks Like

A user would need to:
1. Open their training spreadsheet
2. Copy relevant rows
3. Open a PDF of a strength training book
4. Find the relevant chapter
5. Copy the relevant section
6. Open ChatGPT
7. Write a prompt that combines their data + the book knowledge + their question
8. Get an answer with no memory of last week's conversation
9. Repeat all of this every single time

Nobody actually does this. The knowledge exists in theory but the workflow is shattered across 5 tools.

### How It Works

#### Cost-Conscious Architecture

Two paths — cheap vs. expensive:

**CHEAP PATH (every interaction — $0):**
- User logs training via structured form (exercise, sets, reps, weight, RPE, notes)
- Backend Python validation (no LLM)
- DynamoDB write
- Unlimited, free, fast

**EXPENSIVE PATH (on-demand questions only — ~$0.01-0.03 per query):**
- User asks a question
- Embed query → FAISS search across general knowledge corpus
- Retrieve user's personal training history from DynamoDB
- ONE LLM call: synthesize personalized answer from both sources
- Rate-limited per user (e.g., 20 queries/day)

#### Architecture Diagram

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Frontend    │────▶│  API Gateway  │────▶│   Lambda     │
│              │     │  + Cognito    │     │              │
│ - Log form   │     │  (auth+rate   │     │ LOG: Python  │
│ - Ask chat   │     │   limiting)   │     │  validation  │
│ - History    │     │               │     │  → DynamoDB  │
│              │     │               │     │  (NO LLM)    │
│              │     │               │     │              │
│              │     │               │     │ ASK: FAISS   │
│              │     │               │     │  search →    │
│              │     │               │     │  LLM call →  │
│              │     │               │     │  response    │
└─────────────┘     └──────────────┘     └──────────────┘
                                               │
                                    ┌──────────┴──────────┐
                                    │                     │
                              ┌─────▼─────┐       ┌──────▼──────┐
                              │ DynamoDB   │       │ S3          │
                              │ user logs  │       │ FAISS index │
                              │ profiles   │       │ (general    │
                              │            │       │  knowledge) │
                              └────────────┘       └─────────────┘
```

### Cross-Domain Knowledge Transfer

The LLM's killer feature is bridging domains. The RAG corpus knows powerlifting periodization, weightlifting cycles, training templates, and general strength principles from books. When a grip sport athlete asks for help, the LLM extrapolates: "Based on block periodization principles from powerlifting and the peaking protocol in Cycle_7.xls, here's how those principles apply to your gripper and pinch training..."

Periodization is periodization. Progressive overload is progressive overload. The science transfers — the LLM makes the translation.

### General Knowledge Base

- 13 polished .xlsx (Microsoft Excel) powerlifting training cycles for different purposes, with self-calculated formulas (parsed via openpyxl + LLM once at setup into natural language descriptions of the training logic)
- 3-5 strength training books/PDFs (chunked and embedded)
- All stored as FAISS index — works identically on local machine and AWS (S3 + Lambda)

### GenAI Patterns Used

- **RAG** (general knowledge corpus via FAISS)
- **LLM as coaching/explanation layer** (synthesizes personal history + general principles)
- **LLM as one-time data ingestion** (.xlsx formula logic → natural language descriptions, run once at setup)
- **Agent with tool use** (queries DynamoDB for personal history, searches FAISS, produces report — stretch goal: proactive weekly analysis)

### Cost Architecture

| Action | Frequency | LLM call? | Cost |
|---|---|---|---|
| Log training | Daily | No — structured form + Python | $0 |
| Parse .xlsx knowledge base | Once at setup | Yes — one-time | ~$0.50 |
| Ask a question | On-demand | Yes — one call per question | ~$0.01-0.03 |
| Proactive analysis (stretch) | Weekly | Yes — batched | ~$0.05 |

| Usage scenario | Queries/day | Cost/month |
|---|---|---|
| Just you | 3-5 | ~$3-5 |
| 10 athletes | 30-50 | ~$15-30 |
| Demo day | 20 queries | ~$0.50 |

### Data Flywheel

Gets smarter with every logged session. After 3 months, StrengthWise knows things about you that no single ChatGPT conversation could access.

### Demo Proof

1. Show empty system → log 10 sessions → ask a question → get generic answer
2. Show system after 30 sessions (pre-seeded) → ask same question → get answer that references specific personal patterns
3. Show proactive alert: "Based on your last 6 weeks, I recommend..." (stretch goal)
4. Try to do step 2 in ChatGPT → watch the user struggle to paste 30 sessions worth of context

### Target Users

- Solo athletes in niche strength sports (grip, armwrestling, strongman)
- Powerlifters and weightlifters wanting personalized coaching
- Small coaches/trainers needing analytical support
- Any strength trainee who wants a system that learns from their history

### Technical Stack

| Component | AWS Service | Free Tier | Local Dev |
|---|---|---|---|
| Compute | Lambda | 1M requests/month | Python locally |
| Database | DynamoDB | 25GB, 25 RCU/WCU | DynamoDB Local (Docker) |
| Storage | S3 | 5GB | Local filesystem |
| API | API Gateway | 1M calls/month | Flask/FastAPI |
| Auth | Cognito | 50K MAU | Mock/skip |
| Vector store | FAISS (file in S3) | $0 — it's a file | FAISS (file on disk) |
| LLM | Claude API (budget-capped) | N/A — pay per call | Same API or Ollama |
| IaC | CDK/Terraform | N/A | N/A |
| Frontend | S3 + CloudFront | Free tier | Local dev server |

### 7-Day Build Plan

| Day | Deliverable |
|---|---|
| 1 | IaC setup, Lambda scaffolding, DynamoDB tables, API Gateway — `cdk deploy` works |
| 2 | Knowledge ingestion: parse 13 .xlsx + books → embed → FAISS index in S3 |
| 3 | RAG pipeline: query → FAISS search → LLM response (general knowledge) |
| 4 | Personal data: structured log form → DynamoDB + personal history in query context |
| 5 | Dual-source query: user question retrieves general knowledge + personal history → synthesized answer |
| 6 | Basic frontend: log page, chat page, history page |
| 7 | Seed 30 demo sessions, polish, demo prep |

**Minimum viable fallback (3-day version):** General knowledge RAG only + structured logging + bare frontend. No personal history in queries. Still a working RAG app with persistent user data.

### Research Paper Potential

**Title:** "A RAG-based cross-domain knowledge transfer system for personalized athletic programming"

**Evaluation approach (no human subjects needed):**
- Ablation study: dual-source (general + personal) vs. personal-only vs. general-only vs. vanilla LLM
- Cross-domain transfer accuracy: do powerlifting principles correctly apply to grip sport queries?
- Retrieval quality: precision/recall on manually labeled query set

**Potential targets:** Workshop paper at RecSys, sports informatics journal (Q2-Q3)

---

### Creative Facilitation Narrative

Session progressed from broad frustration mapping → systematic parameter exploration → convergence on a single strong candidate. The pivotal moments were: (1) the "Google Sheets" question that reframed tracking as an insight problem, (2) the 13 .xlsx files revelation that provided a real data corpus, (3) the cost correction that split logging from querying, and (4) the broadening from grip-sport to all strength sports via cross-domain transfer.
