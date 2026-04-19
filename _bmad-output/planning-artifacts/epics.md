---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
status: complete
completedAt: '2026-04-20'
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
  - '_bmad-output/planning-artifacts/ux-design-specification.md'
---

# StrengthWise - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for StrengthWise, decomposing the requirements from the PRD, UX Design, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Athletes can log a training session with date, sport/discipline, exercises, sets, reps, weight, RPE, and free-text notes
FR2: Athletes can select their sport/discipline from a predefined list (grip sport, armwrestling, powerlifting, general strength)
FR3: Athletes can select exercises from a sport-specific pre-populated database when logging
FR4: Athletes can add free-text notes to any session (e.g., "felt weak", "elbow pain", "new PR")
FR5: Athletes can add multiple exercises with multiple sets per exercise in a single session log
FR6: Athletes can view their training session history in reverse chronological order
FR7: Athletes can view details of any individual past session
FR8: Athletes can ask natural language questions about their training and receive cited responses
FR9: The system retrieves relevant information from both the athlete's personal training history and the general strength knowledge base for each query
FR10: AI responses cite personal data sources (specific session dates and metrics) and general knowledge sources (principle name and source text)
FR11: The system distinguishes between personal data citations and general knowledge citations in response formatting
FR12: Athletes can submit a training program (pasted text) and receive an evaluation against general principles and their personal training patterns
FR13: The system provides confidence-appropriate responses based on available data volume (few sessions vs. many sessions)
FR14: The system acknowledges gaps when retrieval doesn't surface relevant information rather than fabricating answers
FR15: Free-tier athletes can make up to 3 AI coaching queries per day
FR16: Athletes in their first 7 days receive 10 AI coaching queries per day
FR17: Premium athletes can make unlimited AI coaching queries (subject to per-minute burst limits)
FR18: Athletes can see their remaining daily query count
FR19: Athletes can create an account with email-based registration
FR20: Athletes can sign in and sign out securely
FR21: Athletes can export all their training data as CSV
FR22: Athletes can delete their account and all associated data
FR23: Athletes can view their profile and usage statistics (sessions logged, queries made)
FR24: The system maintains a curated general knowledge base of strength training science (periodization, progressive overload, sport-specific programming)
FR25: The system maintains a pre-populated exercise database covering grip sport, armwrestling, powerlifting, and general strength exercises
FR26: The system supports cross-domain knowledge transfer — applying principles from one strength discipline to questions about another
FR27: AI responses include a disclaimer that the system provides training insights, not medical advice
FR28: Athletes can provide thumbs up/down feedback on AI responses
FR29: The system validates and sanitizes all user input before processing (chat queries, notes, program analysis text)
FR30: The system can be deployed with a single IaC command and torn down with a single command, leaving zero lingering resources
FR31: The operator can monitor system usage (logging events, AI queries, active users, LLM costs) via AWS CloudWatch
FR32: The operator can update the general knowledge base (rebuild FAISS index) without system downtime
FR33: The system enforces per-user rate limits on AI query endpoints

### NonFunctional Requirements

NFR1: Training session logging (form submission to confirmation) completes in under 500ms
NFR2: AI coaching query responses return within 10 seconds (FAISS search + DynamoDB fetch + LLM call)
NFR3: Session history page loads within 2 seconds for users with up to 500 logged sessions
NFR4: Initial page load (cached, via CloudFront) completes within 2 seconds
NFR5: Time to interactive for the SPA is under 3 seconds on a 4G mobile connection
NFR6: The logging form end-to-end experience (open form -> fill -> submit -> confirm) takes under 30 seconds for a typical 4-exercise session
NFR7: All API endpoints require authenticated Cognito JWT tokens — no unauthenticated access to user data or AI queries
NFR8: Training data is encrypted at rest in DynamoDB (AWS default encryption)
NFR9: All data in transit uses HTTPS/TLS (API Gateway and CloudFront enforce this by default)
NFR10: User input (chat queries, notes, program text) is validated and sanitized before inclusion in LLM prompts to prevent prompt injection
NFR11: Maximum input length enforced on all text fields (2000 chars for queries, 500 chars for notes) to prevent abuse
NFR12: Per-user rate limits are enforced server-side and cannot be bypassed by client manipulation
NFR13: Account deletion removes all user data from DynamoDB within 24 hours, with no residual data in backups beyond standard DynamoDB retention
NFR14: The system supports up to 100 concurrent users without performance degradation (Lambda auto-scaling, DynamoDB on-demand capacity)
NFR15: LLM costs remain bounded at scale through rate limiting: worst-case free-tier cost is calculable as (active users x 3 queries/day x $0.05/query)
NFR16: The FAISS index file remains small enough to load within Lambda's memory constraints (128MB-512MB) for the MVP knowledge corpus
NFR17: DynamoDB table design supports efficient queries by user ID and date range without full table scans
NFR18: Core flows (logging, chat, history) are keyboard-navigable
NFR19: All form inputs have associated labels and ARIA attributes for screen reader compatibility
NFR20: Color contrast ratios meet WCAG 2.1 AA standard (4.5:1 for normal text, 3:1 for large text)
NFR21: Touch targets are minimum 44x44px on mobile for all interactive elements
NFR22: The system gracefully handles Claude API outages or rate limits — AI query failures return a user-friendly error message, not a system crash. Logging continues to function
NFR23: The FAISS index can be rebuilt and redeployed to S3 without downtime — Lambda picks up the updated index on next cold start
NFR24: CSV data export produces a standards-compliant file that opens correctly in Excel, Google Sheets, and other common spreadsheet tools
NFR25: Training session data has zero tolerance for data loss — DynamoDB provides 99.999% durability by default
NFR26: The system remains functional for logging even if the LLM provider is unavailable — the logging path has no LLM dependency
NFR27: IaC deployment is idempotent — running deploy multiple times produces the same result without errors or resource duplication

### Additional Requirements

- Composed stack starter: Vite 8 + React frontend, AWS CDK v2 (Python) IaC, custom FastAPI backend — project scaffold is the first implementation story
- FastAPI + Mangum v0.21.0 dual-mode adapter: same handler code runs locally (uvicorn) and on Lambda
- Docker container deployment for Lambda (FAISS + sentence-transformers exceeds ZIP size limits) — multi-stage build targeting linux/amd64
- DynamoDB multi-table design: Sessions (PK: userId, SK: sessionDate#sessionId), QueryUsage (PK: userId, SK: date), Feedback (PK: queryId)
- Sentence-transformers (all-MiniLM-L6-v2) for FAISS embeddings — free, local, no external API dependency, ~80MB model in container
- Exercise database as static JSON file bundled with backend (not DynamoDB) — loaded at startup, served from memory
- Local dev parity: DynamoDB Local (Docker), FAISS on local filesystem, auth bypass mode (AUTH_BYPASS=true injects TEST_USER_ID), Vite dev server for frontend
- Pydantic models for all request/response validation with alias_generator=to_camel for snake_case Python to camelCase JSON
- Environment config via single config.py reading os.environ with defaults — no code branches for local vs. AWS
- CDK single stack for all AWS resources: DynamoDB tables, Cognito user pool, Lambda (container from ECR), API Gateway, S3 + CloudFront
- Routers are thin (validate input, call service, return response) — business logic lives in services/
- FAISS index loaded once per Lambda instance (cold start) or at FastAPI startup (local dev)
- Onboarding tier detection: use Cognito UserCreateDate from JWT claims to determine if user is in first 7 days
- CORS via FastAPI CORSMiddleware — works identically in local dev and on Lambda
- Makefile for dev workflow: make dev-backend, make dev-frontend, make deploy, make seed

### UX Design Requirements

UX-DR1: Dark-first color system with Zinc-900 background, Zinc-800 surfaces, Blue-400 personal data accent, Amber-400 knowledge accent — light mode toggle available
UX-DR2: System font stack (no custom fonts) for instant loading — 16px minimum body text to prevent iOS zoom
UX-DR3: Bottom tab bar navigation (4 tabs: Home, Log, Chat, History) on mobile (56px height), left sidebar (200px) on desktop (md: breakpoint)
UX-DR4: CitationBlock component with two variants — PersonalCitation (Blue-400 left border, blue-tinted bg, "YOUR DATA" label) and KnowledgeCitation (Amber-400 left border, amber-tinted bg, "TRAINING SCIENCE" label)
UX-DR5: SetEntryRow component — 4-column grid (Set# | Weight | Reps | RPE) with monospace font, pre-filled from last session values as defaults
UX-DR6: ExerciseBlock component — container with exercise name header, last-session hint, set rows, "+ Add Set" button, Zinc-800 background
UX-DR7: FollowupChip component — pill-shaped suggested follow-up questions (2-3 per response), tappable to submit as new query
UX-DR8: ChatInputBar component — persistent text input with send button, placeholder "Ask about your training...", multi-line for program paste
UX-DR9: QueryCounter component — shows remaining daily queries with color-coded states (normal Zinc-400, low Amber-400, exhausted Red-400 with reset time)
UX-DR10: SportSelector component — segmented control with 4 sport options (Grip Sport, Armwrestling, Powerlifting, General Strength), auto-selects last-used sport
UX-DR11: ExercisePicker — sport-specific exercise list sorted by user's usage frequency, recent exercises surfaced first
UX-DR12: SessionCard component — Dashboard variant (Zinc-800 card with 8px radius) and History variant (borderless, bottom-divider, date-grouped)
UX-DR13: Smart defaults — date auto-fills today, sport auto-selects from last session, weight/reps pre-filled from last session values
UX-DR14: Skeleton screens for loading states (Zinc-800 blocks with pulse animation), inline spinners for button actions
UX-DR15: Confidence-calibrated response framing — low data (1-5 sessions): "early indicators suggest...", medium (6-30): "looking at recent data...", high (30+): "a clear pattern shows..."
UX-DR16: Starter prompt cards for new users (<5 sessions) with 3 sport-specific suggested questions
UX-DR17: Post-log nudge after session save — "Log X sessions and ask me anything about your training" with link to Chat tab
UX-DR18: Three-tier button system — Primary (Blue-500 bg, one per screen max), Secondary (Blue-500 border), Ghost (transparent, Zinc-400 text)
UX-DR19: Inline error and feedback patterns — no modal dialogs. Form validation, API errors, rate limits all displayed in-place with retry options
UX-DR20: WCAG 2.1 AA accessibility — focus-visible rings, ARIA attributes on custom components, semantic HTML, skip-to-content link, aria-live for dynamic content
UX-DR21: Responsive layout — mobile single-column (full-width), md: sidebar + centered content (max 720px), content max-width capped
UX-DR22: Touch accessibility — 44x44px minimum touch targets, 8px minimum gap between tappable elements, no gesture-only interactions in MVP
UX-DR23: Empty states for all screens — Dashboard (welcome + log CTA), Chat (starter prompts), History (no sessions + log link), Chat rate-limited (disabled input with reset time)
UX-DR24: HeaderBar component (48px) with screen title and contextual info (query count on Chat, save button on Log)
UX-DR25: FeedbackButtons component — thumbs up/down on every AI response for quality rating
UX-DR26: Confirmation patterns — inline success for non-destructive actions, explicit inline confirmation for destructive actions (account deletion)
UX-DR27: Mobile numeric input — inputmode="decimal" for weight/RPE, inputmode="numeric" for reps/sets to trigger correct mobile keyboard

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1 | Epic 2 | Log session with date, sport, exercises, sets, reps, weight, RPE, notes |
| FR2 | Epic 2 | Select sport/discipline from predefined list |
| FR3 | Epic 2 | Select exercises from sport-specific database |
| FR4 | Epic 2 | Add free-text notes to any session |
| FR5 | Epic 2 | Multiple exercises with multiple sets per session |
| FR6 | Epic 2 | View session history in reverse chronological order |
| FR7 | Epic 2 | View details of individual past sessions |
| FR8 | Epic 3 | Ask natural language questions, receive cited responses |
| FR9 | Epic 3 | Dual-source retrieval (personal history + general knowledge) |
| FR10 | Epic 3 | Cite personal data sources and general knowledge sources |
| FR11 | Epic 3 | Distinguish personal vs. knowledge citations visually |
| FR12 | Epic 3 | Submit program for evaluation |
| FR13 | Epic 3 | Confidence-appropriate responses based on data volume |
| FR14 | Epic 3 | Acknowledge gaps rather than fabricating answers |
| FR15 | Epic 4 | Free-tier: 3 AI queries/day |
| FR16 | Epic 4 | Onboarding: 10 AI queries/day for first 7 days |
| FR17 | Epic 4 | Premium: unlimited queries (burst-limited) |
| FR18 | Epic 4 | See remaining daily query count |
| FR19 | Epic 1 | Create account with email registration |
| FR20 | Epic 1 | Sign in and sign out securely |
| FR21 | Epic 5 | Export training data as CSV |
| FR22 | Epic 5 | Delete account and all data |
| FR23 | Epic 4 | View profile and usage statistics |
| FR24 | Epic 3 | Curated general knowledge base |
| FR25 | Epic 2 | Pre-populated exercise database for all sports |
| FR26 | Epic 3 | Cross-domain knowledge transfer |
| FR27 | Epic 3 | Medical advice disclaimer on AI responses |
| FR28 | Epic 5 | Thumbs up/down feedback on AI responses |
| FR29 | Epic 3 | Validate and sanitize all user input |
| FR30 | Epic 1 | Single-command IaC deploy and teardown |
| FR31 | Epic 6 | Monitor usage via CloudWatch |
| FR32 | Epic 6 | Update knowledge base without downtime |
| FR33 | Epic 4 | Enforce per-user rate limits server-side |

## Epic List

### Epic 1: Project Foundation & User Authentication
Athletes can create accounts, sign in/out, and access the app. The system deploys and tears down with a single command.
**FRs covered:** FR19, FR20, FR30

### Epic 2: Training Session Logging & Exercise Database
Athletes can log training sessions with sport-specific exercises, view session history, and review individual sessions. The core daily interaction.
**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR25

### Epic 3: AI Coaching with Dual-Source RAG
Athletes can ask natural language questions and receive dual-cited coaching responses drawing from their personal training history and general strength science. Includes program analysis, confidence calibration, gap acknowledgment, cross-domain transfer, and input sanitization.
**FRs covered:** FR8, FR9, FR10, FR11, FR12, FR13, FR14, FR24, FR26, FR27, FR29

### Epic 4: Usage Management & Rate Limiting
Athletes see their remaining daily query count, usage is metered per tier (free/onboarding/premium), and profile shows usage statistics.
**FRs covered:** FR15, FR16, FR17, FR18, FR23, FR33

### Epic 5: Feedback, Data Export & Account Lifecycle
Athletes can provide thumbs up/down on AI responses, export all training data as CSV, and delete their account with full data removal.
**FRs covered:** FR21, FR22, FR28

### Epic 6: Operations & Monitoring
The operator can monitor system usage via CloudWatch and update the knowledge base (rebuild FAISS index) without downtime.
**FRs covered:** FR31, FR32

## Epic 1: Project Foundation & User Authentication

Athletes can create accounts, sign in/out, and access the app. The system deploys and tears down with a single command.

### Story 1.1: Project Scaffold & Local Development Environment

As a **developer**,
I want a complete project scaffold with backend, frontend, and IaC directories and a working local dev environment,
So that I have a solid foundation to build all features on.

**Acceptance Criteria:**

**Given** a fresh checkout of the repository
**When** I run `make dev` (or `scripts/dev.sh`)
**Then** DynamoDB Local starts on port 8000, FastAPI backend starts on port 8080 with a `/health` endpoint returning 200, and Vite dev server starts on port 5173 serving the React app
**And** the directory structure matches the architecture specification (backend/, frontend/, infra/, scripts/, Makefile)

**Given** the FastAPI backend is running locally
**When** I call `GET /health`
**Then** I receive a 200 response confirming the API is operational
**And** the Mangum adapter is configured so the same handler works on Lambda

**Given** the frontend scaffold is initialized
**When** I open the Vite dev server in a browser
**Then** I see a basic React app with Tailwind CSS v4 configured, dark theme (Zinc-900 background), system font stack, and the 4-tab navigation shell (Home, Log, Chat, History)

**Given** the infra/ directory is initialized
**When** I inspect the CDK project
**Then** it contains a Python CDK app with a single stack shell ready for resource definitions

### Story 1.2: AWS Infrastructure & Deployment Pipeline

As an **operator**,
I want to deploy the entire StrengthWise stack to AWS with a single command and tear it down completely with another,
So that I have zero lingering resources and repeatable deployments.

**Acceptance Criteria:**

**Given** the CDK stack is defined with all required resources
**When** I run `make deploy` (or `scripts/deploy.sh`)
**Then** the following resources are provisioned: DynamoDB tables (Sessions, QueryUsage, Feedback), Cognito user pool, Lambda function (container image from ECR), API Gateway, S3 bucket + CloudFront distribution
**And** the deployment completes without errors

**Given** a deployed stack exists
**When** I run `make teardown` (or `scripts/teardown.sh`)
**Then** all AWS resources are destroyed with zero lingering resources
**And** running teardown multiple times does not produce errors (idempotent)

**Given** the backend Dockerfile exists
**When** I build the container image
**Then** it produces a working Lambda container image targeting linux/amd64 with all dependencies (FastAPI, Mangum, boto3, faiss-cpu, sentence-transformers, anthropic)

**Given** I run `cdk deploy` multiple times
**When** the stack already exists
**Then** deployment is idempotent — no errors or resource duplication (NFR27)

### Story 1.3: User Registration & Authentication

As an **athlete**,
I want to create an account with my email and sign in/out securely,
So that my training data is private and I can access it across sessions.

**Acceptance Criteria:**

**Given** I am a new user on the sign-up page
**When** I enter my email and password and submit
**Then** a Cognito account is created, I receive a verification email, and after verification I am signed in and redirected to the Dashboard
**And** the sport selector appears post-signup asking "What do you train?" with options: Grip Sport, Armwrestling, Powerlifting, General Strength

**Given** I am a registered user on the sign-in page
**When** I enter my email and password
**Then** I am authenticated via Cognito, a JWT token is stored in memory (not localStorage), and I am redirected to the Dashboard

**Given** I am signed in
**When** I tap the sign-out action
**Then** my JWT is cleared, I am redirected to the sign-in page, and subsequent API calls return 401

**Given** any API endpoint (other than health check)
**When** a request is made without a valid Cognito JWT
**Then** the request is rejected with a 401 status code (NFR7)

**Given** the local development environment is running
**When** AUTH_BYPASS=true is set in .env
**Then** the auth middleware injects TEST_USER_ID from .env, allowing development without a Cognito connection

## Epic 2: Training Session Logging & Exercise Database

Athletes can log training sessions with sport-specific exercises, view session history, and review individual sessions. The core daily interaction.

### Story 2.1: Exercise Database & Sport Selection

As an **athlete**,
I want to select my sport and see exercises specific to my discipline,
So that the app speaks my sport's language and I can log accurately.

**Acceptance Criteria:**

**Given** the backend is running
**When** I call `GET /exercises` with no query parameter
**Then** I receive the full exercise database organized by sport

**Given** the backend is running
**When** I call `GET /exercises?sportType=grip`
**Then** I receive only grip sport exercises: gripper close, hub lift, pinch block, wrist curl, fat bar (and any others defined)

**Given** the exercise database
**When** I inspect the available sports
**Then** all four sports are covered: Grip Sport (gripper close, hub lift, pinch block, wrist curl, fat bar), Armwrestling (pronation, supination, side pressure, hook, cupping, table practice), Powerlifting (squat, bench, deadlift, accessories), General Strength (common exercises)
**And** the database is a static JSON file loaded at startup, not a DynamoDB table (FR25)

**Given** the frontend logging form
**When** I open the SportSelector component
**Then** I see a segmented control with 4 options (Grip Sport, Armwrestling, Powerlifting, General Strength) with 48px height per option and 44x44px minimum touch targets (UX-DR10, UX-DR22)

**Given** I have logged sessions before
**When** I open the logging form
**Then** the SportSelector auto-selects my last-used sport (UX-DR13)

**Given** I select a sport in the SportSelector
**When** the ExercisePicker opens
**Then** exercises are filtered by the selected sport and sorted by my usage frequency with recent exercises first (UX-DR11)

### Story 2.2: Training Session Logging Form

As an **athlete**,
I want to log a training session with exercises, sets, reps, weight, RPE, and notes in under 30 seconds,
So that I can consistently capture my training data post-session without friction.

**Acceptance Criteria:**

**Given** I am on the logging form
**When** I open it from the Dashboard or Log tab
**Then** the date auto-fills to today, sport auto-selects from my last session, and the form is ready for exercise entry (UX-DR13)

**Given** I have selected an exercise
**When** it is added to the form
**Then** an ExerciseBlock appears with the exercise name, a "Last: 4x3 @ 80kg" hint from my most recent session with that exercise, and pre-filled set rows matching last session's values (UX-DR6, UX-DR13)

**Given** I am entering set data
**When** I interact with a SetEntryRow
**Then** I see a 4-column grid (Set# | Weight | Reps | RPE) with monospace font, center-aligned numeric inputs, inputmode="decimal" for weight/RPE and inputmode="numeric" for reps (UX-DR5, UX-DR27)
**And** tab moves between fields left-to-right then down, Enter adds a new set row

**Given** I have entered exercises and sets
**When** I tap the green "Save" button in the header bar
**Then** the session is saved via `POST /sessions`, I see an inline confirmation "Session saved. X sessions this month." in Green-500, and the form data is stored in DynamoDB Sessions table with userId as PK and sessionDate#sessionId as SK
**And** the response completes in under 500ms (NFR1)

**Given** I have just saved a session
**When** the confirmation appears
**Then** I see a post-log nudge: "Ask me anything about your training" with a link to the Chat tab (UX-DR17)

**Given** I am filling the form and a validation error occurs
**When** I submit with invalid data (e.g., missing required fields)
**Then** inline error messages appear next to the invalid fields in Red-500 without clearing any entered data (UX-DR19)

**Given** I want to add notes
**When** I type in the notes text area
**Then** I can enter free-text up to 500 characters (NFR11), the area has max-height 120px and scrolls if exceeded (FR4)

**Given** a typical 4-exercise session with 3-4 sets each
**When** I log it using smart defaults and minimal edits
**Then** the entire flow (open form -> fill -> submit -> confirm) completes in under 30 seconds (NFR6)

### Story 2.3: Session History & Detail View

As an **athlete**,
I want to view my training history and drill into individual sessions,
So that I can review past training and track my progress over time.

**Acceptance Criteria:**

**Given** I navigate to the History tab
**When** the page loads
**Then** I see my training sessions in reverse chronological order, displayed as borderless date-grouped rows with monospace set counts right-aligned (D6 minimal style per UX-DR12 History variant)
**And** the page loads within 2 seconds for up to 500 sessions (NFR3)

**Given** I have sessions in my history
**When** I tap on a session row
**Then** I see the full session detail: date, sport, each exercise with all sets (weight/reps/RPE), and notes (FR7)

**Given** I have no logged sessions
**When** I navigate to the History tab
**Then** I see the empty state: "No sessions logged yet." with a "Log Session" link (UX-DR23)

**Given** the Dashboard/Home tab
**When** I view my dashboard
**Then** I see recent session cards (Dashboard variant: Zinc-800 background, 8px radius, showing sport tag, exercise count, total sets) and a prominent "Log Session" primary button (UX-DR12 Dashboard variant)

**Given** I am a new user with 0 sessions
**When** I view the Dashboard
**Then** I see: "Welcome to StrengthWise" heading, "Log your first session to get started." body text, primary "Log Session" button, and a chat input with hint "Log a few sessions first, then ask me anything." (UX-DR23)

**Given** the backend has sessions for my user
**When** I call `GET /sessions`
**Then** sessions are returned sorted by date descending, queried efficiently by userId PK (NFR17)

**Given** the backend
**When** I call `GET /sessions/{id}`
**Then** I receive the full session record including all exercises, sets, and notes

## Epic 3: AI Coaching with Dual-Source RAG

Athletes can ask natural language questions and receive dual-cited coaching responses drawing from their personal training history and general strength science.

### Story 3.1: Knowledge Base Ingestion & FAISS Index

As an **operator**,
I want to ingest the curated strength science corpus into a FAISS vector index,
So that the AI coaching system has a searchable general knowledge base to cite from.

**Acceptance Criteria:**

**Given** knowledge base source documents exist in `backend/data/knowledge/`
**When** I run `scripts/build_faiss_index.py`
**Then** the script embeds all documents using sentence-transformers (all-MiniLM-L6-v2), produces a FAISS index file and an index_metadata.json mapping chunks to source names, and saves them to `backend/data/faiss_index/`

**Given** a built FAISS index
**When** I query it with a strength training concept (e.g., "progressive overload periodization")
**Then** it returns relevant chunks with source attribution (principle name and source text) (FR24)

**Given** the FAISS index
**When** I inspect its size
**Then** it is small enough to load within Lambda's 128-512MB memory allocation (NFR16)

**Given** a local FAISS index exists
**When** I run `scripts/upload_index_to_s3.py`
**Then** the index files are uploaded to the configured S3 bucket for Lambda consumption

**Given** the corpus covers strength training science
**When** I inspect the indexed content
**Then** it includes periodization principles, progressive overload, sport-specific programming for grip, armwrestling, and powerlifting, and cross-domain transfer knowledge (FR24, FR26)

### Story 3.2: Dual-Source RAG Pipeline

As an **athlete**,
I want my coaching queries to draw from both my personal training history and general strength science,
So that I receive personalized, cited advice grounded in both my data and established principles.

**Acceptance Criteria:**

**Given** I send a `POST /query` with a natural language question
**When** the RAG pipeline processes it
**Then** it: (1) embeds the query via sentence-transformers, (2) searches FAISS for top-K relevant general knowledge chunks, (3) fetches my relevant sessions from DynamoDB via session_service, (4) builds a combined LLM prompt with both sources, (5) calls Claude API, (6) returns a structured response with separated personal and knowledge citations (FR8, FR9)

**Given** the RAG pipeline returns a response
**When** I inspect the response JSON
**Then** it follows the architecture format: `{ data: { response, citations: { personal: [...], knowledge: [...] }, confidence, queriesRemaining } }` with personal citations containing sessionDate/exercise/detail and knowledge citations containing source/principle (FR10)

**Given** user input in the query
**When** the text is processed
**Then** it passes through `sanitize_llm_input()` in the service layer, stripping injection patterns, enforcing 2000-char max length, and escaping delimiters before LLM prompt inclusion (FR29, NFR10, NFR11)

**Given** the athlete has sufficient training data
**When** the system responds
**Then** it provides confidence-calibrated framing: "Based on your first few sessions..." (1-5 sessions), "Looking at your recent training data..." (6-30), "Based on X months of data, a clear pattern shows..." (30+) (FR13)

**Given** the retrieval doesn't surface relevant personal data or knowledge
**When** the system responds
**Then** it acknowledges the gap rather than fabricating: "I don't have enough data on [topic] to give a confident answer" (FR14)

**Given** the Claude API is unavailable or returns an error
**When** an athlete submits a query
**Then** they receive a friendly error: "I couldn't process that question right now. Please try again." — no raw error exposed, and the logging path remains fully functional (NFR22, NFR26)

**Given** a query about applying principles across disciplines (e.g., powerlifting peaking for armwrestling)
**When** the RAG pipeline processes it
**Then** it retrieves cross-domain knowledge and bridges concepts with cited sources from both disciplines (FR26)

**Given** the full RAG pipeline completes
**When** measured end-to-end (FAISS search + DynamoDB fetch + LLM call)
**Then** the response returns within 10 seconds (NFR2)

### Story 3.3: Chat Interface with Citation Display

As an **athlete**,
I want a conversational chat interface that displays dual-cited coaching responses with distinct citation styling,
So that I can ask questions naturally and verify the sources behind every recommendation.

**Acceptance Criteria:**

**Given** I navigate to the Chat tab
**When** the page loads
**Then** I see a ChatInputBar at the bottom with placeholder "Ask about your training..." and a send button (UX-DR8)

**Given** I type a question and tap send
**When** the query is submitted
**Then** my message appears as a user ChatBubble (right-aligned), a loading indicator shows "StrengthWise is thinking..." with pulsing dots (UX-DR14), and the AI response appears as an AI ChatBubble (left-aligned) when complete

**Given** an AI response contains personal data citations
**When** the response renders
**Then** PersonalCitation blocks appear with Blue-400 left border (3px), blue-tinted background, "YOUR DATA" label in uppercase, showing session date and specific metrics (UX-DR4)

**Given** an AI response contains general knowledge citations
**When** the response renders
**Then** KnowledgeCitation blocks appear with Amber-400 left border (3px), amber-tinted background, "TRAINING SCIENCE" label in uppercase, showing principle name and source (UX-DR4)

**Given** an AI response is displayed
**When** I look below the response
**Then** I see 2-3 FollowupChip components with suggested follow-up questions (pill-shaped, tappable to send as new query) (UX-DR7)

**Given** an AI response is displayed
**When** I look at the response
**Then** it includes a medical advice disclaimer: "StrengthWise provides training insights, not medical advice" (FR27)

**Given** I am a new user with fewer than 5 sessions
**When** I open the Chat tab
**Then** I see 3 starter prompt cards with sport-specific suggested questions and subtitle "The more sessions you log, the better my answers get." (UX-DR16)

**Given** the chat area has messages
**When** a new AI response appears
**Then** the chat area has `role="log"` with `aria-live="polite"` so screen readers announce it, and citation blocks have `aria-label` identifying source type (UX-DR20)

### Story 3.4: Program Analysis

As an **athlete**,
I want to paste a training program and receive an evaluation against general principles and my personal training patterns,
So that I can assess program quality before committing to it.

**Acceptance Criteria:**

**Given** I am in the Chat interface
**When** I paste a multi-line training program (up to 2000 characters) into the ChatInputBar
**Then** the input expands to accommodate the text (max 200px height) and I can submit it with context like "Evaluate this program for my grip training" (FR12)

**Given** I submit a program for analysis via `POST /analyze`
**When** the system processes it
**Then** the response evaluates the program against general principles (amber citations) and my personal training patterns (blue citations), with specific recommendations and suggested modifications

**Given** the program analysis response
**When** it renders in the chat
**Then** it uses the same CitationBlock styling, FollowupChip pattern, and confidence framing as regular coaching queries — consistent UI across all query types

**Given** the program analysis request
**When** processed by the backend
**Then** it passes through the same input sanitization and rate limiting as `/query` (FR29, counts as one query against daily limit)

## Epic 4: Usage Management & Rate Limiting

Athletes see their remaining daily query count, usage is metered per tier (free/onboarding/premium), and profile shows usage statistics.

### Story 4.1: Server-Side Rate Limiting & Tier Enforcement

As a **system operator**,
I want per-user daily query limits enforced server-side with tier-based access,
So that LLM costs are bounded and the free tier is sustainable.

**Acceptance Criteria:**

**Given** a free-tier athlete (account older than 7 days)
**When** they submit their 4th `/query` or `/analyze` request in a day
**Then** the request is rejected with HTTP 429, error code "RATE_LIMIT_EXCEEDED", and detail including resetAt time and limit of 3 (FR15)

**Given** an athlete in their first 7 days (onboarding tier, detected via Cognito UserCreateDate)
**When** they submit their 11th query in a day
**Then** the request is rejected with HTTP 429 and a limit of 10 (FR16)

**Given** a premium-tier athlete
**When** they submit queries
**Then** they are not subject to daily limits but are still subject to per-minute burst rate limits (FR17)

**Given** a `/query` or `/analyze` request
**When** the rate_limit_service checks the QueryUsage DynamoDB table
**Then** it uses atomic DynamoDB `UpdateItem` with condition expression — no race conditions, server-side enforced, cannot be bypassed by client manipulation (FR33, NFR12)

**Given** any rate limit check
**When** the daily counter is read and incremented
**Then** the operation uses the QueryUsage table (PK: userId, SK: date) and returns the current count for inclusion in the API response

### Story 4.2: Query Counter Display & User Profile

As an **athlete**,
I want to see my remaining daily queries and my usage statistics,
So that I can manage my query budget and see how much I've used the system.

**Acceptance Criteria:**

**Given** I am using the Chat interface
**When** I view the header or below an AI response
**Then** I see a QueryCounter showing "X of Y queries remaining today" (UX-DR9)

**Given** my query count is at 1 remaining
**When** the QueryCounter renders
**Then** it displays in Amber-400 text as a warning state (UX-DR9)

**Given** my daily limit is exhausted
**When** I view the Chat interface
**Then** the QueryCounter shows in Red-400 with reset time, the ChatInputBar is disabled with message "Daily limit reached. Resets at [time]." — no interstitial paywall (UX-DR9, UX-DR23)

**Given** I call `GET /profile`
**When** the response returns
**Then** it includes my usage statistics: total sessions logged, total queries made, current tier, account creation date (FR23)

**Given** I view the profile area
**When** it renders
**Then** I see my usage stats displayed clearly with session count and query count

## Epic 5: Feedback, Data Export & Account Lifecycle

Athletes can provide thumbs up/down on AI responses, export all training data as CSV, and delete their account with full data removal.

### Story 5.1: AI Response Feedback

As an **athlete**,
I want to give thumbs up or thumbs down on AI coaching responses,
So that the system can track response quality and improve over time.

**Acceptance Criteria:**

**Given** an AI coaching response is displayed in the Chat
**When** I look below the response
**Then** I see FeedbackButtons with thumbs up and thumbs down icons (UX-DR25)

**Given** I tap thumbs up or thumbs down
**When** the feedback is submitted
**Then** it is stored in the Feedback DynamoDB table (PK: queryId) with the rating and the button I tapped is visually highlighted as selected (FR28)

**Given** I have already provided feedback on a response
**When** I view that response again
**Then** my previous feedback selection is shown (no duplicate submissions)

### Story 5.2: Training Data Export

As an **athlete**,
I want to export all my training data as a CSV file,
So that I own my data and can use it outside StrengthWise.

**Acceptance Criteria:**

**Given** I trigger a data export via `POST /export`
**When** the export completes
**Then** I receive a CSV file containing all my training sessions with date, sport, exercise, set number, weight, reps, RPE, and notes (FR21)

**Given** the exported CSV file
**When** I open it in Excel, Google Sheets, or another spreadsheet tool
**Then** it opens correctly with proper column headers and data formatting — standards-compliant CSV (NFR24)

**Given** I trigger export in the frontend
**When** the request is processing
**Then** I see "Preparing your export..." inline, then a download link appears when ready (UX-DR26)

### Story 5.3: Account Deletion

As an **athlete**,
I want to delete my account and all associated data permanently,
So that I can exercise my right to data removal.

**Acceptance Criteria:**

**Given** I choose to delete my account
**When** the confirmation UI appears
**Then** I see an inline (not modal) confirmation: "Delete your account and all training data? This cannot be undone." with a Red-500 "Delete" button and a Ghost "Cancel" button (UX-DR26)

**Given** I confirm account deletion via `DELETE /account`
**When** the deletion processes
**Then** all my data is removed from all DynamoDB tables (Sessions, QueryUsage, Feedback) and my Cognito account is deleted (FR22)
**And** data removal completes within 24 hours (NFR13)

**Given** my account has been deleted
**When** I try to sign in
**Then** authentication fails and I would need to create a new account

## Epic 6: Operations & Monitoring

The operator can monitor system usage via CloudWatch and update the knowledge base (rebuild FAISS index) without downtime.

### Story 6.1: System Usage Monitoring

As an **operator**,
I want to monitor system usage via AWS CloudWatch,
So that I can track adoption, costs, and system health.

**Acceptance Criteria:**

**Given** the system is deployed and serving traffic
**When** I check CloudWatch
**Then** I can see Lambda invocation counts (logging endpoints vs. query endpoints), API Gateway request counts, and DynamoDB read/write capacity consumption (FR31)

**Given** AI coaching queries are being made
**When** I check the LLM cost tracking
**Then** I can see a per-query counter in DynamoDB that tracks total AI queries for cost estimation (FR31)

**Given** the CDK stack defines the infrastructure
**When** I inspect CloudWatch metrics
**Then** Lambda logs, API Gateway metrics, and DynamoDB metrics are available via the AWS Console without additional setup

### Story 6.2: Knowledge Base Update Pipeline

As an **operator**,
I want to rebuild and deploy an updated FAISS index without system downtime,
So that I can add new knowledge sources and improve coaching quality continuously.

**Acceptance Criteria:**

**Given** I have added new source documents to `backend/data/knowledge/`
**When** I run `scripts/build_faiss_index.py` followed by `scripts/upload_index_to_s3.py`
**Then** a new FAISS index is built, uploaded to S3, and Lambda instances pick up the updated index on their next cold start (FR32, NFR23)

**Given** Lambda instances are currently serving queries with the old index
**When** the new index is uploaded to S3
**Then** existing Lambda instances continue serving with the old index until their next cold start — no downtime, no errors, no manual intervention required

**Given** the index rebuild process
**When** it completes
**Then** the new index contains all previously indexed content plus the new documents, with no content loss
